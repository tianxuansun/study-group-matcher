# Study Group Matcher

Backend microservice for forming small stable study groups.
## 🚀 Quick Start (Local Setup)

1. **Clone the repo**
   ```bash
   git clone https://github.com/tianxuansun/study-group-matcher.git
   cd study-group-matcher
## Testing

Run the full test suite with coverage:

```bash
source .venv/bin/activate
pytest -v --cov=app --cov-report=term-missing
## Groups & Memberships

### Groups
- `POST /api/groups/` → create a group. Body:
  ```json
  {"name": "Study Group A", "course_id": 1}
## Matching

Two endpoints:

- `POST /api/matching/preview/`
  - Body:
    ```json
    {
      "user_ids": [1,2,3,4,5,6],
      "group_size": 4,
      "min_overlap_minutes": 60,
      "course_id": 1
    }
    ```
  - Returns a plan with `groups` (member user_ids and a meeting slot with `weekday`, `start_min`, `end_min`) and `leftovers`.

- `POST /api/matching/apply/`
  - Same body as preview. Creates `Group`(s) named "Auto Group N" and `Membership`(s).
  - If `course_id` is provided, created groups are tagged with it.

**Algorithm (v1):** greedy bin-packing by common availability slots. Deterministic ordering (sort by user id), ensures each group has a common slot of at least `min_overlap_minutes` on the same weekday.
**Grouping rule:** the matcher creates only full groups of the requested `group_size`. Any remaining users that cannot form a full group are returned in `leftovers`.
