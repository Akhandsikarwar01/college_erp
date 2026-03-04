# Subject Code & Assignment Guide

## Subject Fundamentals

### What is a Subject?

A **Subject** is a course or module taught in a specific **semester** of a **course**. Each subject:
- Belongs to **exactly ONE semester** (and therefore ONE course, ONE specific semester number)
- Has a **globally unique code** (e.g., `CS301`, `MATH-201`)
- Can be taught by **multiple teachers** to **different sections**
- Cannot be duplicated in the same semester with the same name

## Subject Code Rules

### Requirement: Subject Code is REQUIRED

Every subject MUST have a code. The code field is:
- **Not optional** (no blank=True)
- **Globally unique** across all courses and semesters
- **Permanent** (cannot be changed once set)
- **Used as primary identifier** in reports, transcripts, registrations

### Code Format & Validation

Subject codes must follow these rules:

✅ **Valid Format**:
```
CS301       ← Department code + number (most common)
MATH-201    ← With hyphen
DA_101      ← With underscore  
PHY4        ← Short format
ENG-LIT-01  ← Complex identifier
```

❌ **Invalid Format**:
```
C S 301     ← Spaces not allowed
CS 301      ← Spaces not allowed
CS-301.1    ← Special chars (periods) not allowed
@#$%        ← Non-alphanumeric not allowed
```

**Code Validation Rules**:
1. **Alphanumeric only**: Letters (A-Z, a-z) and numbers (0-9)
2. **Hyphens and underscores allowed**: `-` and `_`
3. **Max 20 characters**: `CS301` (5 chars) ← Good
4. **No spaces, periods, or special characters**
5. **Case-sensitive**: `CS301` ≠ `cs301` (they are different codes)
6. **Globally unique**: Each code can only exist once across entire system

## Data Hierarchy with Subject Codes

```
Department (IT)
  └─ Program (B.Tech)
      └─ Course (Computer Science)
          ├─ Semester 1
          │   ├─ Subject: CS101 – Programming Fundamentals
          │   ├─ Subject: MATH-101 – Discrete Math
          │   └─ Subject: ENG-101 – English Communication
          │
          ├─ Semester 2
          │   ├─ Subject: CS201 – Data Structures
          │   ├─ Subject: CS202 – Web Development
          │   └─ Subject: MATH-201 – Discrete Mathematics II
          │
          └─ ... Semesters 3-8
          
+
├─ Class (Year 1)
│   ├─ Section A (60 students)
│   ├─ Section B (60 students)
│   └─ Section C (60 students)
│
└─ Class (Year 2)
    ├─ Section A
    └─ Section B
```

## How Subjects Are Taught

### One Subject = One Semester

Each subject is **taught only once per semester**:

```
Subject: CS301 (Data Structures)
├─ Semester 3 of B.Tech CS  ✅
│   ├─ Taught to Section A (Year 2, Group 1)
│   ├─ Taught to Section B (Year 2, Group 2)
│   └─ Taught to Section C (Year 2, Group 3)
│
└─ Repeated in Semester 3 of next year?
    ← Different course instance
```

### Multi-Teacher Assignment

One subject can be taught by **multiple teachers**:

```
Subject: CS301 (Data Structures)
├─ Teacher 1 (Dr. Sharma) → Section A + C
├─ Teacher 2 (Prof. Singh) → Section B
└─ Teacher 3 (Ms. Patel) → Practical Lab Section
```

Each teacher-subject-section combination is **one TeacherAssignment**.

### Unique Constraint

```python
class Subject:
    semester = FK(Semester)  # One subject per semester
    name = CharField()
    code = CharField(unique=True)  # Globally unique
    
    class Meta:
        unique_together = ("semester", "name")
        # Cannot have same name twice in same semester
```

This means:
| Scenario | Allowed? | Reason |
|----------|----------|--------|
| Same subject code in different semesters | ❌ NO | Code globally unique |
| Same subject name in different semesters | ✅ YES | Different semesters |
| Same subject name in same semester | ❌ NO | unique_together constraint |
| Same subject code in same semester | ❌ NO | Code globally unique |

## Creating Subjects in Admin

### Step 1: Navigate to Admin
```
Go to: /admin/academics/subject/
```

### Step 2: Click "Add Subject"
Shows form with fields:
- **Code** ⭐ (REQUIRED) - Globally unique identifier
- **Name** - Subject full name
- **Semester** - Which semester (has attached course auto-shown)

### Step 3: Fill in Details

Example 1: Programming Fundamentals
```
Code:     CS101
Name:     Programming Fundamentals
Semester: Computer Science - Semester 1
```

Example 2: Database Management
```
Code:     CS301
Name:     Database Management Systems
Semester: Computer Science - Semester 3
```

Example 3: Engineering Mathematics
```
Code:     MATH-201
Name:     Advanced Engineering Mathematics
Semester: Computer Science - Semester 2
```

### Step 4: Admin Shows Course Information

The admin interface displays:
```
Code:              CS301
Name:              Database Management
Semester:          CS - Semester 3
Course (Semester): B.Tech CS (Sem 3)
Full Path:         IT → B.Tech → CS → Semester 3
```

### Step 5: System Validates

Before saving, system checks:
✅ Code is not empty  
✅ Code format is valid (alphanumeric + hyphens/underscores)  
✅ Code is globally unique  
✅ Subject name + semester combination is unique

If validation fails:
```
Error: Subject code 'CS301' already exists. 
       Codes must be globally unique.
```

## Common Subject Code Formats

### By Institution
```
IIT Style:        CS101, MATH201, PHY301
University Style: CS-101, MATH-201, PHY-301
IT Company Style: ITC101, INS102, PRJ103
```

### By Discipline
```
Computer Science:  CS xxx or CSE-xxx
Mathematics:       MATH-xxx or MTH-xxx
Physics:           PHY-xxx or PHYSICS-xxx
Chemistry:         CHEM-xxx or CHM-xxx
Electronics:       EC-xxx or ELEC-xxx
Mechanical:        ME-xxx or MECH-xxx
```

### Best Practice
```
Pattern: [Department Code][Semester*10][Number]

CS101  = CS (Dept) + 1 (Sem 1) + 01 (Subject 1)
CS201  = CS (Dept) + 2 (Sem 2) + 01 (Subject 1)
CS301  = CS (Dept) + 3 (Sem 3) + 01 (Subject 1)
MATH201 = MATH (Dept) + 2 (Sem 2) + 01 (Subject 1)
```

## API Serializer Integration

All serializers now correctly handle subject codes:

```python
class SubjectSerializer(serializers.ModelSerializer):
    semester_display = serializers.CharField(source='semester.number', read_only=True)
    course_name = serializers.CharField(source='semester.course.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'semester', 'semester_display', 'course_name']
```

Example API response:
```json
{
    "id": 5,
    "code": "CS301",
    "name": "Database Management Systems",
    "semester": 3,
    "semester_display": "3",
    "course_name": "B.Tech Computer Science"
}
```

## Subject Assignment Workflow

### Phase 1: Create Subject (Admin)
```
Semester selected: B.Tech CS - Semester 3
Add Subject:
  Code: CS301
  Name: Database Management
Status: ✅ Created (Saved to DB)
```

### Phase 2: Assign Teachers (Admin)
```
Go to TeacherAssignment
Add assignment for:
  Teacher: Dr. Sharma
  Subject: CS301 (Database Management)
  Section: Section A (Year 2)
Status: ✅ Assigned (Validation checks: CS301 course = Section A course ✅)
```

### Phase 3: Create Attendance Sessions (Teacher)
```
Teacher goes to /attendance/sessions/create/
Select:
  Subject: CS301
  Date: 2026-03-05
Status: ✅ Session created (QR tokens generated for this subject)
```

### Phase 4: Student Attendance (Student)
```
Student scans QR at /attendance/scan/
System records:
  Subject: CS301
  Attendance: Present
  Date: 2026-03-05
Status: ✅ Recorded (linked to subject code)
```

## Database Schema

### Subject Table
```
id (PK)          | INTEGER
semester_id (FK) | INTEGER  → Semester table
name             | VARCHAR(100)
code             | VARCHAR(20) UNIQUE
created_at       | DATETIME
updated_at       | DATETIME

INDEXES:
  - code (unique)
  - (semester_id, name) (unique together)
```

## Testing Subject Creation

### Test 1: Valid Subject Creation
```bash
python manage.py shell << 'EOF'
from apps.academics.models import Subject, Semester

# Get a semester
semester = Semester.objects.filter(number=1).first()

# Create subject
subject = Subject.objects.create(
    code="CS101",
    name="Programming Fundamentals",
    semester=semester
)
print(f"✅ Created: {subject}")
EOF
```

### Test 2: Code Validation
```bash
python manage.py shell << 'EOF'
from apps.academics.models import Subject, Semester

semester = Semester.objects.filter(number=2).first()

# Valid code with hyphen
subject = Subject.objects.create(
    code="MATH-201",
    name="Advanced Mathematics",
    semester=semester
)
print(f"✅ Valid: {subject}")

# Invalid code with spaces (will fail)
try:
    bad_subject = Subject.objects.create(
        code="C S 301",  # ❌ Spaces not allowed
        name="Invalid",
        semester=semester
    )
except Exception as e:
    print(f"✅ Caught error: {e}")
EOF
```

### Test 3: Unique Code Constraint
```bash
python manage.py shell << 'EOF'
from apps.academics.models import Subject, Semester

# Create first subject
semester1 = Semester.objects.filter(number=1).first()
s1 = Subject.objects.create(code="CS101", name="Prog", semester=semester1)
print(f"✅ Created: {s1}")

# Try to create with same code but different semester
semester2 = Semester.objects.filter(number=2).first()
try:
    s2 = Subject.objects.create(
        code="CS101",  # ❌ Same code, different semester = FAILS
        name="Different Name",
        semester=semester2
    )
except Exception as e:
    print(f"✅ Caught constraint: Code must be globally unique")
EOF
```

## Troubleshooting

### ❌ "Subject code is required"
**Cause**: Trying to save subject without code  
**Fix**: Always provide a code value
```python
Subject.objects.create(
    code="CS301",  # ← Required
    name="Database",
    semester=semester
)
```

### ❌ "Subject code 'CS301' already exists"
**Cause**: Code is globally unique, trying to create duplicate  
**Fix**: Use a different code
```python
Subject.objects.create(code="CS302", ...)  # ← Different code
```

### ❌ "Subject code must be alphanumeric"
**Cause**: Code contains invalid characters (spaces, periods, etc.)  
**Fix**: Use only alphanumeric + hyphens/underscores
```python
Subject.objects.create(code="CS-301", ...)  # ← Valid
Subject.objects.create(code="C S 301", ...)  # ← Invalid (spaces)
```

### ❌ "Cannot create separate subject with same name in same semester"
**Cause**: Already have "Programming Fundamentals" in Semester 1  
**Fix**: Use different name or different semester
```python
# Fix 1: Different name
Subject.objects.create(code="CS102", name="Advanced Programming", semester=s1)

# Fix 2: Different semester
Subject.objects.create(code="CS102", name="Programming Fundamentals", semester=s2)
```

## Summary

✅ **Subject Code** is required, globally unique, and identifies each subject  
✅ **Subject** belongs to exactly ONE semester (hence one course & semester number)  
✅ **Code Format** is alphanumeric + hyphens/underscores, max 20 chars  
✅ **Validation** happens at save time via `code` unique constraint and `clean()` method  
✅ **Admin Display** shows full course hierarchy and validates code  
✅ **Database Indexes** on code and (semester, name) for fast lookups  
✅ **Uniqueness** enforced both at DB level (unique constraint) and application level (clean method)

### Key Rule
One subject = One semester. A subject cannot appear in multiple semesters. But the same subject can be taught to multiple sections by different teachers.

Version: 1.0  
Last Updated: 4 March 2026  
Commit: [pending]
