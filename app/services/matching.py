from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.availability import Availability
from app.models.group import Group
from app.schemas.matching import MatchInput, MatchPlan, MatchGroup, MatchSlot
from app.crud import membership as membership_crud
from app.crud import group as group_crud

def _load_availabilities(db: Session, user_ids: List[int]) -> Dict[int, Dict[int, List[Tuple[int,int]]]]:
    """
    Returns: {user_id: {weekday: [(start_min, end_min), ...]}}
    """
    if not user_ids:
        return {}
    stmt = select(Availability).where(Availability.user_id.in_(user_ids))
    by_user: Dict[int, Dict[int, List[Tuple[int,int]]]] = {}
    for row in db.scalars(stmt):
        by_user.setdefault(row.user_id, {}).setdefault(row.weekday, []).append((row.start_min, row.end_min))
    # normalize sort intervals per user/day
    for u in by_user:
        for d in by_user[u]:
            by_user[u][d].sort()
    return by_user

def _overlap_len(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    start = max(a[0], b[0])
    end = min(a[1], b[1])
    return max(0, end - start)

def _find_common_slot(day_intervals: List[List[Tuple[int,int]]], min_len: int) -> Optional[Tuple[int,int]]:
    """
    day_intervals: list of interval lists for each member on same weekday.
    Greedy intersection sweep to find one interval of length >= min_len.
    """
    # flatten approach: start with intersection = first person's list
    inter: List[Tuple[int,int]] = day_intervals[0][:]
    for nxt in day_intervals[1:]:
        new_inter: List[Tuple[int,int]] = []
        i=j=0
        while i < len(inter) and j < len(nxt):
            a = inter[i]; b = nxt[j]
            start = max(a[0], b[0]); end = min(a[1], b[1])
            if end > start:
                new_inter.append((start, end))
            if a[1] < b[1]: i += 1
            else: j += 1
        inter = new_inter
        if not inter:
            return None
    for s,e in inter:
        if e - s >= min_len:
            return (s, s + min_len)  # pick earliest feasible window of min_len
    return None

def _compatible_slot(users: List[int], avail: Dict[int, Dict[int, List[Tuple[int,int]]]], min_len: int) -> Optional[MatchSlot]:
    # try weekdays 0..6; pick first that yields overlap
    for d in range(7):
        day_lists: List[List[Tuple[int,int]]] = []
        for u in users:
            intervals = avail.get(u, {}).get(d, [])
            if not intervals:
                day_lists = []
                break
            day_lists.append(intervals)
        if day_lists:
            best = _find_common_slot(day_lists, min_len)
            if best:
                return MatchSlot(weekday=d, start_min=best[0], end_min=best[1])
    return None


def preview_plan(db: Session, params: MatchInput) -> MatchPlan:
    """
    Greedy bin-packing:
      - iterate user_ids in sorted order for determinism
      - start a group, keep adding next user that preserves a valid common slot
      - finalize group once size reached; continue
      - optionally allow a final partial group (>=2) if allow_partial_last_group=True
    """
    avail = _load_availabilities(db, params.user_ids)
    pool = sorted(params.user_ids)
    groups: List[MatchGroup] = []
    leftovers: List[int] = []

    while pool:
        seed = pool.pop(0)
        cur = [seed]
        slot = None

        # try to build up to group_size
        i = 0
        while i < len(pool) and len(cur) < params.group_size:
            candidate = pool[i]
            test = cur + [candidate]
            slot_try = _compatible_slot(test, avail, params.min_overlap_minutes)
            if slot_try:
                cur.append(candidate)
                slot = slot_try
                pool.pop(i)  # accept candidate
            else:
                i += 1

        # Accept a group if:
        # - we found a viable slot AND
        # - (size == target) OR (allow_partial_last_group and size >= 2)
        if slot and (len(cur) == params.group_size or (params.allow_partial_last_group and len(cur) >= 2)):
            groups.append(MatchGroup(user_ids=cur, slot=slot))
        else:
            leftovers.extend(cur)

    debug = None
    if params.diagnostics:
        # Very light-weight, but helpful: show pool order and availability density
        avail_counts = {u: sum(len(vd) for vd in byday.values()) for u, byday in avail.items()}
        debug = {
            "pool_order": sorted(params.user_ids),
            "avail_intervals_per_user": avail_counts,
        }

    return MatchPlan(
        groups=groups,
        leftovers=leftovers,
        params={
            "group_size": params.group_size,
            "min_overlap_minutes": params.min_overlap_minutes,
            "course_id": params.course_id if params.course_id is not None else 0,
            "allow_partial_last_group": params.allow_partial_last_group,
            "name_prefix": params.name_prefix or "Auto Group",
            "diagnostics": params.diagnostics,
        },
        debug=debug,
    )


# add near the other imports at top (select is already imported in your file; keep one import)
from sqlalchemy import select

# NEW helper: pick the next free "Auto Group N"
def _next_group_name(db: Session, base: str = "Auto Group") -> str:
    # grab all existing names that start with the base
    existing = set(db.scalars(select(Group.name).where(Group.name.like(f"{base}%"))).all())
    n = 1
    while True:
        candidate = f"{base} {n}"
        if candidate not in existing:
            return candidate
        n += 1

def apply_plan(
    db: Session,
    plan: MatchPlan,
    course_id: Optional[int],
    name_prefix: Optional[str] = None,
) -> List[int]:
    """
    Creates Group + Memberships. Returns created group IDs.
    """
    created_ids: List[int] = []
    base = name_prefix or plan.params.get("name_prefix") or "Auto Group"

    for mg in plan.groups:
        # pick a unique name each time to satisfy UNIQUE(groups.name)
        name = _next_group_name(db, base=base)
        grp = group_crud.create(db, obj_in=type("X",(object,),{"name": name, "course_id": course_id})())
        created_ids.append(grp.id)
        for uid in mg.user_ids:
            membership_crud.create(db, obj_in=type("Y",(object,),{"user_id": uid, "group_id": grp.id})())
    return created_ids