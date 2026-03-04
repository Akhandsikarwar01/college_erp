"""
Management command to populate the database with comprehensive demo data for College ERP.
This creates a complete working ERP system with all modules populated.
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from apps.accounts.models import CustomUser, Role, StudentProfile, TeacherProfile, DeanProfile
from apps.academics.models import Department, Program, Course, Class, Section, Semester, Subject
from apps.faculty.models import TeacherAssignment, FacultyDepartment, TeacherMaster, SectionIncharge
from apps.attendance.models import AttendanceSession, AttendanceRecord
from apps.examinations.models import ExamType, Exam, ExamSchedule, GradeScale, StudentResult
from apps.fees.models import FeeType, FeeStructure, StudentFee, Payment
from apps.library.models import BookCategory, Book, BookIssue
from apps.notices.models import NoticeCategory, Notice, Event
from apps.leave.models import LeaveType, LeaveApplication
from apps.timetable.models import TimeSlot, TimetableEntry


class Command(BaseCommand):
    help = 'Set up comprehensive demo data for the College ERP system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new demo data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Setting up College ERP Demo Data'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if options['clear']:
            self.stdout.write(self.style.WARNING('\nClearing existing data...'))
            self.clear_data()

        # Order matters due to foreign key relationships
        self.create_academic_structure()
        self.create_users_and_profiles()
        self.create_teacher_assignments()
        self.create_attendance_data()
        self.create_exam_data()
        self.create_fee_data()
        self.create_library_data()
        self.create_notice_data()
        self.create_leave_data()
        self.create_timetable_data()

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Demo data setup completed successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.print_credentials()

    def clear_data(self):
        """Clear all demo data except superusers"""
        CustomUser.objects.exclude(is_superuser=True).delete()
        Department.objects.all().delete()
        FacultyDepartment.objects.all().delete()
        TeacherMaster.objects.all().delete()
        ExamType.objects.all().delete()
        GradeScale.objects.all().delete()
        FeeType.objects.all().delete()
        BookCategory.objects.all().delete()
        NoticeCategory.objects.all().delete()
        LeaveType.objects.all().delete()
        self.stdout.write(self.style.WARNING('Existing data cleared.'))

    def create_academic_structure(self):
        self.stdout.write('\n[1/10] Creating academic structure...')
        
        # Departments
        cs_dept = Department.objects.create(code='CSE', name='Computer Science & Engineering')
        ec_dept = Department.objects.create(code='ECE', name='Electronics & Communication')
        me_dept = Department.objects.create(code='ME', name='Mechanical Engineering')
        
        # Programs
        btech = Program.objects.create(department=cs_dept, name='B.Tech')
        mtech = Program.objects.create(department=cs_dept, name='M.Tech')
        
        # Courses
        btech_cs = Course.objects.create(program=btech, name='Computer Science')
        btech_ec = Course.objects.create(program=btech, name='Electronics & Communication')
        btech_me = Course.objects.create(program=btech, name='Mechanical Engineering')
        
        # Classes (Years)
        year1 = Class.objects.create(course=btech_cs, name='Year 1')
        year2 = Class.objects.create(course=btech_cs, name='Year 2')
        year3 = Class.objects.create(course=btech_cs, name='Year 3')
        year4 = Class.objects.create(course=btech_cs, name='Year 4')
        
        # Sections
        y1_secA = Section.objects.create(class_obj=year1, name='A')
        y1_secB = Section.objects.create(class_obj=year1, name='B')
        y2_secA = Section.objects.create(class_obj=year2, name='A')
        y3_secA = Section.objects.create(class_obj=year3, name='A')
        y4_secA = Section.objects.create(class_obj=year4, name='A')
        
        # Semesters
        self.semesters = {}
        for i in range(1, 9):
            sem = Semester.objects.create(course=btech_cs, number=i)
            self.semesters[i] = sem
        
        # Subjects for different semesters
        subjects_data = [
            # Semester 1
            (1, 'Engineering Mathematics I'),
            (1, 'Engineering Physics'),
            (1, 'Programming in C'),
            (1, 'Engineering Drawing'),
            (1, 'English Communication'),
            # Semester 2
            (2, 'Engineering Mathematics II'),
            (2, 'Engineering Chemistry'),
            (2, 'Data Structures'),
            (2, 'Digital Logic Design'),
            (2, 'Environmental Science'),
            # Semester 3
            (3, 'Discrete Mathematics'),
            (3, 'Computer Organization'),
            (3, 'Object Oriented Programming'),
            (3, 'Database Management Systems'),
            (3, 'Operating Systems'),
            # Semester 4
            (4, 'Algorithm Design & Analysis'),
            (4, 'Computer Networks'),
            (4, 'Software Engineering'),
            (4, 'Microprocessors'),
            (4, 'Web Technologies'),
        ]
        
        self.subjects = {}
        for sem_num, subject_name in subjects_data:
            subject = Subject.objects.create(
                semester=self.semesters[sem_num],
                name=subject_name,
                code=f"CS{sem_num}{len(self.subjects)+1:02d}"
            )
            self.subjects[subject_name] = subject
        
        # Store sections for later use
        self.sections = {
            'Y1A': y1_secA,
            'Y1B': y1_secB,
            'Y2A': y2_secA,
            'Y3A': y3_secA,
            'Y4A': y4_secA,
        }
        
        self.courses = {
            'btech_cs': btech_cs,
        }
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {Department.objects.count()} departments, '
            f'{Program.objects.count()} programs, '
            f'{Course.objects.count()} courses, '
            f'{Class.objects.count()} classes, '
            f'{Section.objects.count()} sections, '
            f'{Semester.objects.count()} semesters, '
            f'{Subject.objects.count()} subjects'
        ))

    def create_users_and_profiles(self):
        self.stdout.write('\n[2/10] Creating users and profiles...')
        
        # Create ERP Manager
        erp_manager, created = CustomUser.objects.get_or_create(
            username='erp_admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Manager',
                'email': 'admin@college.edu',
                'role': Role.ERP_MANAGER,
                'is_verified': True,
                'is_approved': True,
                'is_active': True,
                'password': make_password('admin123'),
            }
        )

        # Create Deans (one per department)
        dean_data = [
            ('D001', 'Anita', 'Verma', 'dean.cse@college.edu', 'DEAN001', 'CSE'),
            ('D002', 'Rohit', 'Mehra', 'dean.ece@college.edu', 'DEAN002', 'ECE'),
            ('D003', 'Kavita', 'Rao', 'dean.me@college.edu', 'DEAN003', 'ME'),
        ]
        dept_map = {d.code: d for d in Department.objects.all()}
        self.deans = {}
        for username, first_name, last_name, email, emp_id, dept_code in dean_data:
            dean_user, _ = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': Role.DEAN,
                    'is_verified': True,
                    'is_approved': True,
                    'is_active': True,
                    'password': make_password('dean123'),
                }
            )
            if dept_code in dept_map:
                dean_profile, _ = DeanProfile.objects.get_or_create(
                    user=dean_user,
                    defaults={
                        'department': dept_map[dept_code],
                        'employee_id': emp_id,
                    }
                )
                self.deans[username] = dean_profile
        
        # Create Teachers
        teacher_data = [
            ('T001', 'Rajesh', 'Kumar', 'rajesh.kumar@college.edu', 'EMP001'),
            ('T002', 'Priya', 'Sharma', 'priya.sharma@college.edu', 'EMP002'),
            ('T003', 'Amit', 'Singh', 'amit.singh@college.edu', 'EMP003'),
            ('T004', 'Neha', 'Gupta', 'neha.gupta@college.edu', 'EMP004'),
            ('T005', 'Vikram', 'Patel', 'vikram.patel@college.edu', 'EMP005'),
        ]
        
        self.teachers = {}
        for username, first_name, last_name, email, emp_id in teacher_data:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': Role.TEACHER,
                    'is_verified': True,
                    'is_approved': True,
                    'is_active': True,
                    'password': make_password('teacher123'),
                }
            )
            
            # Create or get teacher profile
            teacher_profile, _ = TeacherProfile.objects.get_or_create(
                user=user,
                defaults={'employee_id': emp_id}
            )
            self.teachers[username] = teacher_profile
        
        # Create Students
        student_data = []
        for i in range(1, 31):  # 30 students
            section_key = 'Y1A' if i <= 15 else 'Y1B'
            student_data.append((
                f'S{i:03d}',
                f'Student{i}',
                f'Name{i}',
                f'student{i}@college.edu',
                f'ADM{2024}{i:03d}',
                f'ENR{2024}{i:03d}',
                f'{i:02d}',
                section_key
            ))
        
        self.students = {}
        for username, first_name, last_name, email, adm_no, enr_no, roll_no, section_key in student_data:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': Role.STUDENT,
                    'is_verified': True,
                    'is_approved': True,
                    'is_active': True,
                    'password': make_password('student123'),
                }
            )
            
            # Create or get student profile
            student_profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'section': self.sections[section_key],
                    'admission_number': adm_no,
                    'application_number': f'APP-{adm_no}',
                    'enrollment_number': enr_no,
                    'roll_number': roll_no,
                    'father_name': f'Father of {first_name}',
                    'mother_name': f'Mother of {first_name}',
                    'gender': 'Male' if int(username[1:]) % 2 else 'Female',
                    'city': 'Agra',
                    'state': 'Uttar Pradesh',
                    'pincode': '282001',
                    'guardian_phone': f'98{int(username[1:]):08d}'[:10],
                }
            )
            self.students[username] = student_profile
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created/Updated {CustomUser.objects.count()} users '
            f'({TeacherProfile.objects.count()} teachers, {StudentProfile.objects.count()} students)'
        ))

    def create_teacher_assignments(self):
        self.stdout.write('\n[3/10] Creating teacher assignments...')
        
        # Assign teachers to subjects and sections
        assignments = [
            ('T001', 'Programming in C', 'Y1A'),
            ('T001', 'Programming in C', 'Y1B'),
            ('T002', 'Engineering Mathematics I', 'Y1A'),
            ('T002', 'Engineering Mathematics I', 'Y1B'),
            ('T003', 'Data Structures', 'Y2A'),
            ('T004', 'Database Management Systems', 'Y3A'),
            ('T005', 'Web Technologies', 'Y4A'),
        ]
        
        for teacher_code, subject_name, section_key in assignments:
            if subject_name in self.subjects:
                TeacherAssignment.objects.get_or_create(
                    teacher=self.teachers[teacher_code],
                    subject=self.subjects[subject_name],
                    section=self.sections[section_key],
                )

        # Assign section incharge (one teacher per section)
        section_incharge_map = {
            'Y1A': 'T001',
            'Y1B': 'T002',
            'Y2A': 'T003',
            'Y3A': 'T004',
            'Y4A': 'T005',
        }
        for section_key, teacher_code in section_incharge_map.items():
            if section_key in self.sections and teacher_code in self.teachers:
                SectionIncharge.objects.get_or_create(
                    section=self.sections[section_key],
                    defaults={
                        'teacher': self.teachers[teacher_code],
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {TeacherAssignment.objects.count()} teacher assignments, '
            f'{SectionIncharge.objects.count()} section incharge assignments'
        ))

    def create_attendance_data(self):
        self.stdout.write('\n[4/10] Creating attendance data...')
        
        # Create some attendance sessions
        assignment = TeacherAssignment.objects.filter(
            teacher=self.teachers['T001']
        ).first()
        
        if assignment:
            # Create sessions for the past 10 days
            for i in range(10, 0, -1):
                session_date = timezone.now().date() - timedelta(days=i)
                session = AttendanceSession.objects.create(
                    teacher_assignment=assignment,
                    date=session_date,
                    is_active=False,
                    is_locked=True
                )
                
                # Mark attendance for students in this section
                students = StudentProfile.objects.filter(section=assignment.section)
                for student in students:
                    # 80% attendance rate
                    is_present = (hash(f"{student.id}{i}") % 10) < 8
                    AttendanceRecord.objects.create(
                        session=session,
                        student=student,
                        is_present=is_present
                    )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {AttendanceSession.objects.count()} sessions, '
            f'{AttendanceRecord.objects.count()} attendance records'
        ))

    def create_exam_data(self):
        self.stdout.write('\n[5/10] Creating exam data...')
        
        # Create exam types
        ExamType.objects.get_or_create(name='Mid-Term')
        ExamType.objects.get_or_create(name='End-Term')
        ExamType.objects.get_or_create(name='Internal Assessment')
        
        # Create grade scale
        grade_scales = [
            ('A+', 90, 100, 10.0),
            ('A', 80, 89, 9.0),
            ('B+', 70, 79, 8.0),
            ('B', 60, 69, 7.0),
            ('C', 50, 59, 6.0),
            ('D', 40, 49, 5.0),
            ('F', 0, 39, 0.0),
        ]
        
        for grade, min_marks, max_marks, gp in grade_scales:
            GradeScale.objects.get_or_create(
                grade=grade,
                defaults={
                    'min_marks': min_marks,
                    'max_marks': max_marks,
                    'grade_point': gp
                }
            )
        
        # Create an exam
        exam_type = ExamType.objects.get(name='Mid-Term')
        exam = Exam.objects.create(
            exam_type=exam_type,
            course=self.courses['btech_cs'],
            semester=self.semesters[1],
            name='Mid-Term Exam - Semester 1',
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() - timedelta(days=25),
            is_published=True
        )
        
        # Create exam schedules for subjects
        for subject_name in ['Programming in C', 'Engineering Mathematics I', 'Engineering Physics']:
            if subject_name in self.subjects:
                schedule = ExamSchedule.objects.create(
                    exam=exam,
                    subject=self.subjects[subject_name],
                    date=exam.start_date + timedelta(days=hash(subject_name) % 5),
                    start_time='09:00',
                    end_time='12:00',
                    room='Hall A',
                    max_marks=100,
                    passing_marks=40
                )
                
                # Create results for Y1A students
                y1a_students = StudentProfile.objects.filter(section=self.sections['Y1A'])
                for student in y1a_students:
                    marks = 40 + (hash(f"{student.id}{subject_name}") % 60)
                    StudentResult.objects.create(
                        exam_schedule=schedule,
                        student=student,
                        marks_obtained=marks,
                        is_absent=False
                    )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {ExamType.objects.count()} exam types, '
            f'{Exam.objects.count()} exams, '
            f'{ExamSchedule.objects.count()} schedules, '
            f'{StudentResult.objects.count()} results'
        ))

    def create_fee_data(self):
        self.stdout.write('\n[6/10] Creating fee data...')
        
        # Create fee types
        tuition = FeeType.objects.get_or_create(name='Tuition Fee')[0]
        lab = FeeType.objects.get_or_create(name='Lab Fee')[0]
        library = FeeType.objects.get_or_create(name='Library Fee')[0]
        exam = FeeType.objects.get_or_create(name='Exam Fee')[0]
        
        # Create fee structures
        for sem_num in range(1, 5):
            FeeStructure.objects.get_or_create(
                fee_type=tuition,
                course=self.courses['btech_cs'],
                semester=self.semesters[sem_num],
                defaults={'amount': 50000}
            )
            FeeStructure.objects.get_or_create(
                fee_type=lab,
                course=self.courses['btech_cs'],
                semester=self.semesters[sem_num],
                defaults={'amount': 5000}
            )
            FeeStructure.objects.get_or_create(
                fee_type=library,
                course=self.courses['btech_cs'],
                semester=self.semesters[sem_num],
                defaults={'amount': 2000}
            )
            FeeStructure.objects.get_or_create(
                fee_type=exam,
                course=self.courses['btech_cs'],
                semester=self.semesters[sem_num],
                defaults={'amount': 3000}
            )
        
        # Create student fees
        for student_key, student in self.students.items():
            # Create fee for semester 1
            student_fee = StudentFee.objects.create(
                student=student,
                semester=self.semesters[1],
                total_amount=60000,  # Sum of all fee types
                paid_amount=40000 if hash(student_key) % 2 == 0 else 60000,
                due_date=timezone.now().date() + timedelta(days=30),
                is_paid=hash(student_key) % 2 == 1
            )
            
            # Create a payment if partially paid
            if student_fee.paid_amount > 0:
                Payment.objects.create(
                    student_fee=student_fee,
                    amount=student_fee.paid_amount,
                    method='ONLINE',
                    remarks=f'Online payment'
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {FeeType.objects.count()} fee types, '
            f'{FeeStructure.objects.count()} structures, '
            f'{StudentFee.objects.count()} student fees, '
            f'{Payment.objects.count()} payments'
        ))

    def create_library_data(self):
        self.stdout.write('\n[7/10] Creating library data...')
        
        # Create book categories
        categories = {}
        for cat_name in ['Computer Science', 'Mathematics', 'Physics', 'Engineering', 'Fiction']:
            categories[cat_name] = BookCategory.objects.get_or_create(name=cat_name)[0]
        
        # Create books
        books_data = [
            ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 'Computer Science', 'MIT Press', 5),
            ('Design Patterns', 'Gang of Four', '9780201633610', 'Computer Science', 'Addison-Wesley', 3),
            ('Clean Code', 'Robert C. Martin', '9780132350884', 'Computer Science', 'Prentice Hall', 4),
            ('Database System Concepts', 'Silberschatz', '9780078022159', 'Computer Science', 'McGraw Hill', 3),
            ('Computer Networks', 'Andrew Tanenbaum', '9780132126953', 'Computer Science', 'Pearson', 4),
            ('Engineering Mathematics', 'K.A. Stroud', '9780831134709', 'Mathematics', 'Palgrave', 5),
            ('Physics for Engineers', 'Ray Serway', '9781133939580', 'Physics', 'Cengage', 3),
        ]
        
        self.books = {}
        for title, author, isbn, cat_name, publisher, copies in books_data:
            book = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                category=categories[cat_name],
                publisher=publisher,
                total_copies=copies,
                available_copies=copies
            )
            self.books[title] = book
        
        # Issue some books to students
        for i, (student_key, student) in enumerate(list(self.students.items())[:10]):
            book = list(self.books.values())[i % len(self.books)]
            if book.available_copies > 0:
                BookIssue.objects.create(
                    book=book,
                    borrower=student.user,
                    issue_date=timezone.now().date() - timedelta(days=7),
                    due_date=timezone.now().date() + timedelta(days=7),
                    status='ISSUED'
                )
                book.available_copies -= 1
                book.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {BookCategory.objects.count()} categories, '
            f'{Book.objects.count()} books, '
            f'{BookIssue.objects.count()} issues'
        ))

    def create_notice_data(self):
        self.stdout.write('\n[8/10] Creating notices and events...')
        
        # Create notice categories
        categories = {}
        for cat_name in ['Academic', 'Exam', 'Holiday', 'General']:
            categories[cat_name] = NoticeCategory.objects.get_or_create(name=cat_name)[0]
        
        # Get admin user
        admin_user = CustomUser.objects.filter(role=Role.ERP_MANAGER).first()
        
        if admin_user:
            # Create notices
            notices_data = [
                ('Semester Registration Open', 'Registration for upcoming semester is now open. Please complete your registration by end of this month.', 'Academic', 'ALL', True),
                ('Mid-Term Exam Schedule', 'Mid-term examination schedule has been published. Check the examinations section for details.', 'Exam', 'STUDENT', True),
                ('Faculty Meeting', 'All faculty members are requested to attend the departmental meeting on Friday at 3 PM.', 'General', 'TEACHER', False),
                ('Library New Arrivals', 'New books have been added to the library. Check the catalog for details.', 'General', 'ALL', False),
                ('Holiday Notice', 'College will remain closed on Monday due to public holiday.', 'Holiday', 'ALL', False),
            ]
            
            for title, content, cat_name, target, is_pinned in notices_data:
                Notice.objects.create(
                    title=title,
                    content=content,
                    category=categories[cat_name],
                    posted_by=admin_user,
                    target_role=target,
                    is_pinned=is_pinned
                )
            
            # Create events
            events_data = [
                ('Annual Tech Fest', 'College annual technical festival', 30, 'Main Auditorium'),
                ('Career Fair', 'Companies from various sectors will participate', 45, 'Convention Center'),
                ('Sports Day', 'Inter-department sports competition', 15, 'Sports Complex'),
            ]
            
            for title, description, days_ahead, venue in events_data:
                Event.objects.create(
                    title=title,
                    description=description,
                    date=timezone.now().date() + timedelta(days=days_ahead),
                    venue=venue,
                    organizer=admin_user
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {NoticeCategory.objects.count()} categories, '
            f'{Notice.objects.count()} notices, '
            f'{Event.objects.count()} events'
        ))

    def create_leave_data(self):
        self.stdout.write('\n[9/10] Creating leave data...')
        
        # Create leave types
        leave_types = {}
        for lt_name, max_days in [('Sick Leave', 10), ('Casual Leave', 15), ('Emergency Leave', 5)]:
            leave_types[lt_name] = LeaveType.objects.get_or_create(
                name=lt_name,
                defaults={'max_days_per_year': max_days}
            )[0]
        
        # Create some leave applications
        teacher_user = self.teachers['T001'].user
        erp_manager = CustomUser.objects.filter(role=Role.ERP_MANAGER).first()
        
        # Approved leave
        LeaveApplication.objects.create(
            applicant=teacher_user,
            leave_type=leave_types['Sick Leave'],
            start_date=timezone.now().date() - timedelta(days=5),
            end_date=timezone.now().date() - timedelta(days=3),
            reason='Medical emergency',
            status='APPROVED',
            reviewed_by=erp_manager,
            reviewed_at=timezone.now() - timedelta(days=6)
        )
        
        # Pending leave
        LeaveApplication.objects.create(
            applicant=teacher_user,
            leave_type=leave_types['Casual Leave'],
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=12),
            reason='Family function',
            status='PENDING'
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {LeaveType.objects.count()} leave types, '
            f'{LeaveApplication.objects.count()} applications'
        ))

    def create_timetable_data(self):
        self.stdout.write('\n[10/10] Creating timetable data...')
        
        # Create time slots
        time_slots_data = [
            (1, '09:00', '09:50', False),
            (2, '09:50', '10:40', False),
            (3, '10:40', '11:00', True),  # Break
            (4, '11:00', '11:50', False),
            (5, '11:50', '12:40', False),
            (6, '12:40', '13:30', True),  # Lunch
            (7, '13:30', '14:20', False),
            (8, '14:20', '15:10', False),
        ]
        
        time_slots = []
        for slot_num, start, end, is_break in time_slots_data:
            slot, _ = TimeSlot.objects.get_or_create(
                slot_number=slot_num,
                defaults={
                    'start_time': start,
                    'end_time': end,
                    'is_break': is_break,
                    'label': 'Break' if is_break and slot_num == 3 else ('Lunch' if is_break else '')
                }
            )
            if not is_break:
                time_slots.append(slot)
        
        # Create timetable entries for Y1A
        assignments = TeacherAssignment.objects.filter(section=self.sections['Y1A'])
        
        if assignments.exists():
            for day in range(5):  # Monday to Friday
                for slot_idx, slot in enumerate(time_slots[:5]):  # 5 periods per day
                    assignment = assignments[(day + slot_idx) % assignments.count()]
                    TimetableEntry.objects.get_or_create(
                        day=day,
                        time_slot=slot,
                        section=self.sections['Y1A'],
                        defaults={'teacher_assignment': assignment}
                    )
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✓ Created {TimeSlot.objects.count()} time slots, '
            f'{TimetableEntry.objects.count()} timetable entries'
        ))

    def print_credentials(self):
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('LOGIN CREDENTIALS'))
        self.stdout.write('=' * 70)
        self.stdout.write('\nERP Manager:')
        self.stdout.write('  Username: erp_admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('\nTeacher:')
        self.stdout.write('  Username: T001 (or T002, T003, T004, T005)')
        self.stdout.write('  Password: teacher123')
        self.stdout.write('\nDean:')
        self.stdout.write('  Username: D001 (or D002, D003)')
        self.stdout.write('  Password: dean123')
        self.stdout.write('\nStudent:')
        self.stdout.write('  Username: S001 (or S002 to S030)')
        self.stdout.write('  Password: student123')
        self.stdout.write('\n' + '=' * 70)
