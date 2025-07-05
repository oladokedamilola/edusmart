## 📘 `README.md` — *EduSmart Student Management System*

````markdown
# 🎓 EduSmart – Student Management System

Welcome to **EduSmart**, a comprehensive web-based Student Management System designed to streamline academic administration for universities and institutions.

Built with Django, EduSmart supports three main user roles:

- 👨‍💼 Admin
- 👨‍🏫 Lecturer
- 🎓 Student

---

## 📌 Features

### 🔑 Authentication & Role Management
- Secure registration & login
- Distinct user roles (admin, lecturer, student)
- Custom dashboard per role

---

### 👨‍💼 Admin Features
- Manage courses, sessions, and academic structure
- Assign lecturers to courses
- Approve or reject submitted results
- View system-wide statistics via a custom dashboard
- Post announcements to departments, faculties, or all users

---

### 👨‍🏫 Lecturer Features
- View and manage assigned courses
- Upload course materials (PDF, PPT, DOC)
- Mark and view student attendance
- Post course-specific announcements
- Enter and update student grades
- View approved results and timetable

---

### 🎓 Student Features
- View academic profile (read-only)
- Register for available courses
- Access course materials uploaded by lecturers
- View personal timetable
- Track attendance per course
- View results and grades (GPA/CGPA)
- View/download course transcript (PDF)
- Receive announcements and messages

---

## 🛠 Tech Stack

| Tech | Description |
|------|-------------|
| **Python** | Backend Language |
| **Django** | Web Framework |
| **SQLite/PostgreSQL** | Default Database (Switchable) |
| **Bootstrap 5** | Frontend Styling |
| **HTML/CSS/JS** | Core frontend logic |
| **Font Awesome** | Icon support |
| **WeasyPrint (optional)** | PDF Transcript Generation |

---

## 🚀 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/oladokedamilola/edusmart.git
cd edusmart
````

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # on Unix
venv\Scripts\activate     # on Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

```bash
python manage.py runserver
```

7. **Visit the app**

Go to: `http://127.0.0.1:8000/`

---

## 🧪 Demo Credentials (optional setup)

You can preload demo users using Django fixtures or manually create:

| Role     | Username  | Password |
| -------- | --------- | -------- |
| Admin    | admin     | admin123 |
| Lecturer | lecturer1 | pass123  |
| Student  | student1  | pass123  |

---

## 📁 Project Structure Overview

```bash
edusmart/
├── core/               # Core academic logic (courses, results, announcements, etc.)
├── students/           # Student-facing views and models
├── lecturers/          # Lecturer-facing views and models
├── users/              # CustomUser model and authentication logic
├── templates/          # All HTML templates
│   ├── base_user.html  # Shared user-facing base
│   ├── admin/          # Custom admin pages
│   ├── lecturers/      # Lecturer views
│   └── students/       # Student views
├── static/             # Static files (CSS, JS, Images)
├── media/              # Uploaded materials
└── manage.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 💡 Author

**Oladoke Damilola**
🔗 [github.com/oladokedamilola](https://github.com/oladokedamilola)

---

## 🏷️ Tags

`django` `student-management` `education` `university` `edusmart` `academic-portal` `python`

```
