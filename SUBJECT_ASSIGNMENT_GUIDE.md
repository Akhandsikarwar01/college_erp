# Subject Assignment Logic Guide

## Overview

Subject assignment links teachers with subjects across sections in a course. The system ensures data integrity by validating that all assignments maintain consistent relationships through the course hierarchy.

## Data Hierarchy

```
Department
  └─ Program
      └─ Course
          ├─ Class (Year)
          │   └─ Section (A, B, C, ...)
          │       └─ Students
          │
          └─ Semester (1, 2, 3, ..., 8)
              └─ Subject (Math, English, etc.)
                  └─ TeacherAssignment (links Teacher → Subject → Section)
```

## Model Structure

### 1. **TeacherAssignment** (`apps/faculty/models.py`)

Links a teacher to teach a specific subject for a specific section.

```python
class TeacherAssignment(TimeStampedModel):
    teacher = FK(TeacherProfile)      # Who teaches
    subject = FK(Subject)              # What subject
    section = FK(Section)              # Which section
    
    class Meta:
        unique_together = ("teacher", "subject", "section")
```

**Constraint**: `teacher`, `subject`, and `section` together must be unique.
- A teacher cannot teach the same subject to the same section twice
- A teacher CAN teach different subjects to the same section
- A teacher CAN teach the same subject to different sections

### 2. **Subject** (`apps/academics/models.py`)

Represents a course subject for a specific semester.

```python
class Subject(TimeStampedModel):
    semester = FK(Semester)  # Belongs to a semester
    name     = CharField()   # e.g., "Mathematics", "English"
    code     = CharField()   # e.g., "MATH-101"
    
    class Meta:
        unique_together = ("semester", "name")
```

Each subject belongs to exactly ONE semester.
Semester → Course relationship means: **Subject → Semester → Course**

### 3. **Section** (`apps/academics/models.py`)

Represents a batch/division of students in a class.

```python
class Section(TimeStampedModel):
    class_obj = FK(Class)  # Belongs to a class
    name      = CharField()  # e.g., "A", "B", "C"
    
    class Meta:
        unique_together = ("class_obj", "name")
```

Each section belongs to exactly ONE class.
Class → Course relationship means: **Section → Class → Course**

## Validation Logic ✅

### Critical Rule: **Subject & Section Must Be From Same Course**

When creating a `TeacherAssignment`, the system validates:

```python
subject_course = subject.semester.course
section_course = section.class_obj.course

if subject_course != section_course:
    raise ValidationError("Mismatch!")
```

**Why?** A subject from Course A cannot be assigned to a section from Course B.

### Example ✅ Valid Assignment
```
Teacher: John (ERP_MANAGER)
Subject: "Mathematics" (Sem 1 of B.Tech CS)
Section: Section A, Year 1, B.Tech CS
→ VALID ✅ (all from B.Tech CS course)
```

### Example ❌ Invalid Assignment
```
Teacher: John
Subject: "Mathematics" (Sem 1 of B.Tech CS)
Section: Section A, Year 1, B.Tech ME
→ INVALID ❌ (subject from CS, section from ME)
```

## How to Assign a Subject to a Teacher

### Method 1: Django Admin Interface

1. Go to `/admin/faculty/teacherassignment/`
2. Click "Add Teacher Assignment"
3. Select:
   - **Teacher**: Choose from list of teachers
   - **Subject**: Choose by course → semester → subject
   - **Section**: Choose by course → year → section
4. System automatically validates course match ✅
5. Save

### Admin Validation Display

The admin shows a "Course Match" indicator:
- **✅ Match**: Green checkmark = valid assignment
- **❌ Mismatch**: Red X = validation error (save fails)

The validation display shows:
```
Course Validation: ✅ Match
Subject course = B.Tech CS, Section course = B.Tech CS
```

### Method 2: Programmatic Assignment

```python
from apps.faculty.models import TeacherAssignment
from apps.accounts.models import TeacherProfile
from apps.academics.models import Subject, Section

teacher = TeacherProfile.objects.get(user__username='T001')
subject = Subject.objects.get(name='Mathematics', semester__number=1)
section = Section.objects.get(name='A', class_obj__name='Year 1')

# System validates automatically in save()
assignment = TeacherAssignment.objects.create(
    teacher=teacher,
    subject=subject,
    section=section
)
# ValidationError raised if courses don't match
```

### Method 3: API Endpoint (Future)

Currently no API endpoint exists for subject assignment (admin-only feature).
To add:
```python
# In apps/api/viewsets.py
class TeacherAssignmentViewSet(ModelViewSet):
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticatedAsErpManager]
```

## Common Issues & Solutions

### ❌ "Cannot save TeacherAssignment"
**Error**: `ValidationError: Subject is from course X, but section is in course Y`

**Solution**: 
- Verify subject's course matches section's course
- Check subject's semester's course
- Check section's class's course

### ❌ QuerySet is empty when filtering assignments
**Issue**: Assignment exists but not returned by filter

**Solution**: Use `select_related()` for performance:
```python
assignments = TeacherAssignment.objects.select_related(
    'teacher__user', 
    'subject__semester__course', 
    'section__class_obj__course'
).filter(teacher=teacher)
```

### ❌ Attendance session creation fails
**Issue**: `TeacherAssignment` exists but attendance `session` not created

**Solution**: Check `TeacherAssignment` exists:
```python
from apps.faculty.models import TeacherAssignment

assignment = TeacherAssignment.objects.filter(
    teacher__user=request.user.teacher_profile,
    subject=subject,
    section=section
).first()

if not assignment:
    return "Assignment not found"
```

## API Serializer Fixes (Recent)

All serializers now correctly reference the actual model fields:

### Before ❌
```python
class AttendanceSessionSerializer:
    subject_name = serializers.CharField(source='subject.name')  # ❌ No field
    teacher_name = serializers.SerializerMethodField()
    
    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name()  # ❌ No field
```

### After ✅
```python
class AttendanceSessionSerializer:
    subject_name = serializers.CharField(source='teacher_assignment.subject.name')  # ✅
    teacher_name = serializers.SerializerMethodField()
    
    def get_teacher_name(self, obj):
        return obj.teacher_assignment.teacher.user.get_full_name()  # ✅
```

## Attendance Session Creation Flow

```
Teacher creates AttendanceSession:
1. Selects TeacherAssignment (or auto-populated)
2. System retrieves: subject, section, teacher from assignment
3. Creates session for that assignment, date, section
4. QR tokens generated based on session ID
5. Students scan from that section only
```

## Data Integrity Checkpoints

| Checkpoint | Validates | Error If |
|---|---|---|
| TeacherAssignment.clean() | Subject ↔ Section courses | Mismatch detected |
| AttendanceSession creation | Assignment exists | Section has no QR session |
| Student QR scan | Student in section | Unauthorized scan rejected |
| Attendance export | Records match session | Missing attendance records |

## Testing Subject Assignments

### Create Test Data
```bash
python manage.py shell << 'EOF'
from apps.academics.models import *
from apps.accounts.models import TeacherProfile
from apps.faculty.models import TeacherAssignment

# Get or create course, semester, subject
course = Course.objects.first()
sem = course.semesters.first()
subject = sem.subjects.first()

# Get section
section = course.classes.first().sections.first()

# Get teacher
teacher = TeacherProfile.objects.first()

# Try assignment
try:
    assignment = TeacherAssignment.objects.create(
        teacher=teacher,
        subject=subject,
        section=section
    )
    print(f"✅ Created: {assignment}")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

### Verify Validation
```bash
python manage.py shell << 'EOF'
from apps.faculty.models import TeacherAssignment

# List all assignments with course validation
for a in TeacherAssignment.objects.select_related(
    'subject__semester__course', 'section__class_obj__course'
):
    subject_course = a.subject.semester.course
    section_course = a.section.class_obj.course
    match = "✅" if subject_course == section_course else "❌"
    print(f"{match} {a.teacher.user.username}: {a.subject.name} → {a.section.name}")
EOF
```

## Summary

- ✅ **Subject assignment** links teacher → subject → section with automatic course validation
- ✅ **Course integrity** enforced: subject must belong to same course as section
- ✅ **Database constraint**: unique(teacher, subject, section)
- ✅ **Admin display** shows course match indicator
- ✅ **API serializers** now correctly reference actual model fields
- ✅ **Validation** happens at save time via `clean()` method

Version: 1.0
Last Updated: 4 March 2026
Commit: c06e4d8
