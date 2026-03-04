# College ERP System - Complete Setup Guide

## 🎓 Overview

This is a comprehensive College Enterprise Resource Planning (ERP) system built with Django. It manages all aspects of college operations including:

- **Academic Management**: Departments, Programs, Courses, Classes, Sections, Semesters, Subjects
- **User Management**: Students, Teachers, ERP Managers with role-based access
- **Attendance System**: QR Code-based attendance tracking with real-time scanning
- **Examinations**: Exam scheduling, result entry, grade management
- **Fee Management**: Fee structures, student fees, payment tracking
- **Library Management**: Book catalog, issue/return system, overdue tracking  
- **Notices & Events**: Announcements with role-based targeting
- **Leave Management**: Leave applications with approval workflow
- **Timetable**: Class scheduling with time slots

## 🚀 Quick Start

### 1. Initial Setup (First Time Only)

```bash
# Navigate to project directory
cd "/home/akhand/PLAYGROUND/CODE PLAYGROUND/college_erp"

# Make sure virtual environment is activated (if using one)
# source venv/bin/activate  # or your venv path

# Install dependencies (if needed)
pip install -r requirements.txt

# Run migrations (already done)
python manage.py migrate

# Populate database with demo data
python manage.py setup_demo_data
```

### 2. Start the Server

```bash
# From the college_erp directory
python manage.py runserver
```

Then open http://127.0.0.1:8000 in your browser.

## 👥 Login Credentials

### ERP Manager (Full Admin Access)
- **Username**: `erp_admin`
- **Password**: `admin123`
- **Capabilities**: Approve users, manage fees, import students, create exams, manage all data

### Teacher
- **Username**: `T001` (or T002, T003, T004, T005)
- **Password**: `teacher123`
- **Capabilities**: 
  - Create and manage attendance sessions
  - View assigned subjects and sections
  - Enter exam results
  - Apply for leave
  - Issue library books

### Student
- **Username**: `S001` (or S002 through S030)
- **Password**: `student123`
- **Capabilities**:
  - Scan QR codes for attendance
  - View attendance records and percentage
  - View exam results and grades
  - View and pay fees
  - View timetable
  - Apply for leave
  - View issued library books

## 📚 Features by Role

### 🔧 ERP Manager Features

1. **User Approval**: Approve or reject new registrations
2. **Student Import**: Bulk import students via CSV
3. **Fee Management**: 
   - Define fee structures by course/semester
   - Generate student fees
   - View payment reports
4. **Exam Management**:
   - Create exam types (Mid-term, End-term, etc.)
   - Schedule exams
   - Publish results
5. **Academic Structure**: Manage departments, programs, courses, sections
6. **Library**: Add books, manage categories
7. **Notices & Events**: Post announcements and events

### 👨‍🏫 Teacher Features

1. **Attendance Management**:
   - Create attendance sessions for assigned classes
   - Generate QR codes (auto-refreshing every 5 seconds)
   - View attendance statistics
   - Export attendance reports
2. **Result Entry**: Enter marks for exams
3. **View Assignments**: See all assigned subjects and sections
4. **Leave Applications**: Apply for and track leave
5. **Library**: Issue and return books

### 👨‍🎓 Student Features

1. **Attendance**:
   - Scan QR codes to mark attendance
   - View attendance percentage (overall and subject-wise)
   - See low attendance warnings (<75%)
2. **Exam Results**: View marks, grades, and GPA
3. **Fee Management**:
   - View fee details
   - See payment history
   - Check balance
4. **Timetable**: View class schedule
5. **Library**: View issued books and due dates
6. **Leave Applications**: Apply for leave and track status

## 🏗️ System Architecture

### Database Structure

```
Departments → Programs → Courses → Classes → Sections
                      ↓
                  Semesters → Subjects
                                ↓
                        Teacher Assignments
                                ↓
                        Attendance Sessions → Records
```

### Apps Structure

- **apps/core**: Dashboard, common utilities, base models
- **apps/accounts**: User management, authentication, profiles
- **apps/academics**: Academic structure (departments, courses, subjects)
- **apps/faculty**: Teacher assignments, faculty departments
- **apps/attendance**: QR-based attendance system
- **apps/examinations**: Exams, schedules, results, grades
- **apps/fees**: Fee structures, payments, reports
- **apps/library**: Books, categories, issue/return system
- **apps/notices**: Notices and events
- **apps/leave**: Leave types and applications
- **apps/timetable**: Class schedules and calendar

## 📊 Demo Data Included

The `setup_demo_data` command has populated:

- ✅ 3 Departments (CSE, ECE, ME)
- ✅ 3 Courses (B.Tech CS, B.Tech EC, B.Tech ME)
- ✅ 4 Years (Year 1-4) with 5 Sections
- ✅ 8 Semesters with 20 Subjects
- ✅ 5 Teacher profiles with assignments
- ✅ 30 Student profiles across 2 sections
- ✅ 10 Attendance sessions with 150 records
- ✅ 3 Exam types, 1 exam with 45 student results
- ✅ 4 Fee types with structures and payments
- ✅ 7 Books across 5 categories with 10 issues
- ✅ 5 Notices and 3 Events
- ✅ 2 Leave applications
- ✅ 25 Timetable entries with 8 time slots

## 🔄 Attendance System (QR Code Based)

### How It Works

1. **Teacher Creates Session**: Teacher selects subject, section, and date
2. **QR Code Generation**: System generates a rotating QR code (changes every 5 seconds)
3. **Student Scans**: Students scan the QR code using their phone camera or QR scanner app
4. **Attendance Marked**: System verifies the token and marks attendance (Present/Absent)
5. **Session Management**: Teacher can view live attendance, close session, or lock it

### Security Features

- QR tokens use HMAC-SHA256 cryptographic signing
- Each token is valid for only 5 seconds
- Token includes session ID and time window
- Prevents replay attacks and manual marking

## 💾 Data Management

### Resetting Demo Data

To clear and recreate all demo data:

```bash
python manage.py setup_demo_data --clear
```

This will:
- Delete all non-superuser accounts
- Clear all academic, attendance, exam, fee, library, and leave data
- Recreate everything from scratch

### Manual Data Entry

You can also add data through:
- Django Admin: http://127.0.0.1:8000/admin/
- Web Interface: Use ERP Manager account to add data through the UI

## 🎨 Technology Stack

- **Backend**: Django 4.2.28
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3 (Custom Design System)
- **JavaScript**: Vanilla JS for interactive features
- **Icons**: Custom SVG icons
- **QR Code**: Python hashlib + hmac for secure tokens

## 📁 File Structure

```
college_erp/
├── apps/                          # Django applications
│   ├── accounts/                  # User management
│   ├── academics/                 # Academic structure
│   ├── attendance/                # Attendance system
│   ├── core/                      # Core utilities
│   ├── examinations/              # Exam management
│   ├── faculty/                   # Faculty management
│   ├── fees/                      # Fee management
│   ├── leave/                     # Leave management
│   ├── library/                   # Library management
│   ├── notices/                   # Notices & events
│   └── timetable/                 # Timetable management
├── config/                        # Django configuration
│   ├── settings/                  # Environment-specific settings
│   │   ├── base.py               # Base settings
│   │   ├── dev.py                # Development settings
│   │   └── prod.py               # Production settings
│   └── urls.py                   # URL routing
├── templates/                     # HTML templates
│   ├── base.html                 # Base template with sidebar
│   ├── dashboard/                # Dashboard templates
│   ├── attendance/               # Attendance templates
│   ├── examinations/             # Exam templates
│   └── ...                       # Other app templates
├── static/                        # Static files
│   ├── css/style.css             # Main stylesheet
│   └── js/main.js                # JavaScript
├── media/                         # Uploaded files
├── db.sqlite3                     # Database
├── manage.py                      # Django management script
└── requirements.txt               # Python dependencies
```

## 🛠️ Common Tasks

### Add a New Student

1. Log in as ERP Manager
2. Go to "Import Students" or Django Admin
3. Create user with role STUDENT
4. Create StudentProfile with section, admission number, enrollment number

### Assign Teacher to Subject

1. Go to Django Admin
2. Navigate to Faculty → Teacher Assignments
3. Select Teacher, Subject, and Section
4. Save

### Create an Exam

1. Log in as ERP Manager
2. Go to Examinations
3. Click "Create Exam"
4. Select exam type, course, semester, dates
5. Add schedules for each subject
6. Publish when ready

### Mark Attendance

**Teacher Side:**
1. Go to "New Session"
2. Select Date, Subject, Section
3. Click "Generate QR"
4. Show QR to students

**Student Side:**
1. Go to "Scan QR"
2. Scan the displayed QR code
3. Attendance marked instantly

## 🔐 Security Features

- CSRF protection enabled
- Password hashing with Django's default hasher
- Role-based access control
- Session management
- SQL injection protection (Django ORM)

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is already in use
lsof -i:8000

# Kill existing process if needed
kill -9 <PID>

# Restart server
python manage.py runserver
```

### Database Issues
```bash
# Reset migrations (use with caution)
python manage.py migrate --fake

# Or recreate database
rm db.sqlite3
python manage.py migrate
python manage.py setup_demo_data
```

### Template Not Found
- Ensure TEMPLATES setting includes templates directory
- Check template path matches URL configuration

## 📈 Future Enhancements

Potential features to add:
- Email notifications
- SMS integration
- Online payment gateway
- Mobile app (React Native/Flutter)
- Biometric attendance
- Video lectures integration
- Assignment submission system
- Hostel management
- Transport management
- Inventory management

## 📝 Notes

- Default ALLOWED_HOSTS includes: 127.0.0.1, localhost
- Debug mode is enabled in development settings
- Media files are stored in `media/` directory
- Static files are in `static/` directory (use WhiteNoise for production)

## 🤝 Contributing

To add new features:
1. Create a new Django app if needed
2. Define models in `models.py`
3. Create views in `views.py`
4. Add URL patterns in `urls.py`
5. Include app URLs in main `config/urls.py`
6. Create templates in `templates/<app_name>/`
7. Register models in `admin.py` for admin interface

## 📞 Support

For issues or questions:
- Check Django documentation: https://docs.djangoproject.com/
- Review code comments in views and models
- Test with different user roles to understand functionality

---

**System Status**: ✅ Fully Operational with Demo Data

**Last Updated**: March 4, 2026

**Django Version**: 4.2.28

**Python Version**: 3.13.11
