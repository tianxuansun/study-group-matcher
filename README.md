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
