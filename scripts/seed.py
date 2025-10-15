# scripts/seed.py
from app.db.session import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.models.availability import Availability
from app.models.group import Group
from app.models.membership import Membership

from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import random

def seed():
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Membership).delete()
        db.query(Group).delete()
        db.query(Availability).delete()
        db.execute(text("DELETE FROM user_courses;"))
        db.query(Course).delete()
        db.query(User).delete()
        db.commit()

        # 1️⃣ USERS
        users = []
        for i in range(1, 13):
            u = User(
                email=f"u{i:03d}@demo.edu",
                name=f"User{i:03d}"
            )
            db.add(u)
            users.append(u)
        db.commit()

        # 2️⃣ COURSES
        course_data = [
            ("CS523", "Deep Learning for Engineers"),
            ("EC762", "Quantum Optics for Engineers"),
            ("MA401", "Partial Differential Equations"),
            ("CS540", "Machine Learning Systems"),
            ("EC512", "Digital Signal Processing"),
            ("CS580", "Computer Vision Applications")
        ]

        courses = []
        for code, title in course_data:
            c = Course(code=code, title=title)
            db.add(c)
            courses.append(c)
        db.commit()


        # 3️⃣ ENROLLMENTS (user_courses association)
        for u in users:
            chosen_courses = random.sample(courses, k=random.randint(2, 3))
            for c in chosen_courses:
                if c not in u.courses:  # safeguard against duplicates
                    u.courses.append(c)
        db.commit()

        # 4️⃣ AVAILABILITIES
        for u in users:
            for _ in range(random.randint(1, 3)):
                weekday = random.randint(0, 6)
                start_min = random.choice(range(480, 1020, 60))  # 8:00–17:00
                end_min = start_min + random.choice([60, 90, 120])
                a = Availability(user=u, weekday=weekday, start_min=start_min, end_min=end_min)
                db.add(a)
        db.commit()

        # 5️⃣ GROUPS + MEMBERSHIPS
        g1 = Group(name="Math Study Group")
        g2 = Group(name="AI Research Group")
        db.add_all([g1, g2])
        db.commit()

        members_g1 = random.sample(users, 4)
        members_g2 = random.sample(users, 3)

        for m in members_g1:
            db.add(Membership(user_id=m.id, group_id=g1.id))
        for m in members_g2:
            db.add(Membership(user_id=m.id, group_id=g2.id))
        db.commit()

        print("✅ Seeding complete!")
        print(f"Users: {len(users)} | Courses: {len(courses)} | Groups: 2")

    except IntegrityError as e:
        print("❌ Integrity error:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
