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
## Enrollments

- `POST /api/enrollments/`  
  Body: `{"user_id": 1, "course_id": 2}`  
  Creates the enrollment (409 if duplicate, 404 if user/course not found).

- `GET /api/enrollments/?user_id=...` or `?course_id=...`  
  Lists enrollments with `X-Total-Count` header. Supports `limit`/`offset` (default limit 20, max 100).

- `DELETE /api/enrollments/{user_id}/{course_id}`  
  Removes an enrollment (404 if not found).

## Matching by course

- `POST /api/matching/preview/by-course/{course_id}/`  
  Body: `{"group_size": 4, "min_overlap_minutes": 60}`  
  Returns a plan based on the current roster for that course.

- `POST /api/matching/apply/by-course/{course_id}/`  
  Same body; creates `Group`(s) (named "Auto Group N") + `Membership`(s).  
  Only **full groups** are created; partial groups are returned in `leftovers`.
