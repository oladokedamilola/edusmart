import os
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from lecturers.models import PreexistingLecturer
from students.models import PreexistingStudent
from core.models import Faculty, Department  # 👈 Add this import

# 📁 Load the JSON file
with open("preexisting_users.json", "r") as file:
    data = json.load(file)

def create_faculties():
    faculties = data.get("faculties", [])
    for item in faculties:
        Faculty.objects.get_or_create(name=item["name"])
    print(f"✅ {len(faculties)} faculties inserted.")

def create_departments():
    departments = data.get("departments", [])
    for item in departments:
        faculty_name = item["faculty"]
        faculty = Faculty.objects.get(name=faculty_name)
        Department.objects.get_or_create(
            name=item["name"],
            faculty=faculty
        )
    print(f"✅ {len(departments)} departments inserted.")

def create_lecturers():
    lecturers = data.get("lecturers", [])
    for item in lecturers:
        PreexistingLecturer.objects.get_or_create(
            staff_id=item["staff_id"],
            defaults={
                "first_name": item["first_name"],
                "middle_name": item.get("middle_name", ""),
                "last_name": item["last_name"],
                "faculty": item["faculty"],
                "department": item["department"],
                "email": item["email"]
            }
        )
    print(f"✅ {len(lecturers)} lecturers inserted.")

def create_students():
    students = data.get("students", [])
    for item in students:
        PreexistingStudent.objects.get_or_create(
            matric_number=item["matric_number"],
            defaults={
                "first_name": item["first_name"],
                "middle_name": item.get("middle_name", ""),
                "last_name": item["last_name"],
                "faculty": item["faculty"],
                "department": item["department"],
                "email": item["email"],
                "dob": datetime.strptime(item["dob"], "%Y-%m-%d").date(),
                "year_of_entry": item["year_of_entry"],
                "level": item["level"]
            }
        )
    print(f"✅ {len(students)} students inserted.")

if __name__ == "__main__":
    create_faculties()
    create_departments()
    create_lecturers()
    create_students()
    print("🎉 Database populated from preexisting_users.json")
