"""
Management command to create courses, classes, and sections for all programs.

Creates:
- Courses under each program
- Classes (years) under each course (based on program type)
- Sections (15+ per class) with numeric names (1, 2, 3, etc.)
- Starting from batch 2022

Usage:
    python manage.py create_program_structure
    python manage.py create_program_structure --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academics.models import Department, Program, Course, Class, Section


class Command(BaseCommand):
    help = 'Create courses, classes, and sections for all programs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing courses, classes, and sections before importing',
        )

    def get_program_structure(self, program_name, program_code):
        """
        Determine structure based on program type (Duration, number of courses, class names)
        Returns: {
            'num_courses': int,
            'course_names': [list of course names],
            'num_classes': int,  # Years per course
            'class_names': [list of class year names],
            'num_sections': int
        }
        """
        
        # Determine program type and structure
        program_lower = program_name.lower()
        
        # Doctoral programs: 1 course, 4 years, 15 sections
        if 'doctor of philosophy' in program_lower or 'ph.d' in program_lower:
            return {
                'num_courses': 1,
                'course_names': [f'{program_code}-PHD'],
                'num_classes': 4,
                'class_names': ['Year 1', 'Year 2', 'Year 3', 'Year 4'],
                'num_sections': 15
            }
        
        # Master's programs: 1-2 courses, 2 years, 20 sections
        elif program_lower.startswith('m.'):
            num_courses = 1
            if 'integrated' in program_lower:
                num_courses = 2
            
            courses = [f'{program_code}-M{i+1}' for i in range(num_courses)]
            return {
                'num_courses': num_courses,
                'course_names': courses,
                'num_classes': 2,
                'class_names': ['Year 1', 'Year 2'],
                'num_sections': 20
            }
        
        # Diploma programs: 1 course, 2 years, 20 sections
        elif 'diploma' in program_lower:
            return {
                'num_courses': 1,
                'course_names': [f'{program_code}-DIP'],
                'num_classes': 2,
                'class_names': ['Year 1', 'Year 2'],
                'num_sections': 20
            }
        
        # Certificate programs: 1 course, 1 year, 15 sections
        elif 'certificate' in program_lower:
            return {
                'num_courses': 1,
                'course_names': [f'{program_code}-CERT'],
                'num_classes': 1,
                'class_names': ['Year 1'],
                'num_sections': 15
            }
        
        # Bachelor's/Integrated programs: 1-2 courses, 4 years, 25 sections
        else:
            num_courses = 1
            if 'integrated' in program_lower or 'b.ed' in program_lower:
                num_courses = 1
                num_years = 4 if 'b.ed' in program_lower else 4
            else:
                num_years = 4
            
            courses = [f'{program_code}-B{i+1}' for i in range(num_courses)]
            class_names = ['Year 1', 'Year 2', 'Year 3', 'Year 4']
            
            return {
                'num_courses': num_courses,
                'course_names': courses,
                'num_classes': num_years,
                'class_names': class_names,
                'num_sections': 25
            }

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Section.objects.all().delete()
            Class.objects.all().delete()
            Course.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared'))

        programs = Program.objects.all()
        total_courses = 0
        total_classes = 0
        total_sections = 0

        self.stdout.write(self.style.HTTP_INFO('━' * 100))
        self.stdout.write(self.style.HTTP_INFO('Creating Courses, Classes, and Sections'))
        self.stdout.write(self.style.HTTP_INFO('━' * 100))

        with transaction.atomic():
            for program in programs:
                dept_code = program.department.code
                prog_code = dept_code
                
                # Get structure for this program
                structure = self.get_program_structure(program.name, prog_code)
                
                # Create courses
                for course_idx, course_name in enumerate(structure['course_names']):
                    course, created = Course.objects.get_or_create(
                        program=program,
                        name=course_name,
                        defaults={'name': course_name}
                    )
                    
                    if created:
                        total_courses += 1

                    # Create classes for this course
                    for class_idx, class_name in enumerate(structure['class_names']):
                        class_obj, created = Class.objects.get_or_create(
                            course=course,
                            name=class_name,
                            defaults={'name': class_name}
                        )
                        
                        if created:
                            total_classes += 1

                        # Create sections for this class
                        for section_num in range(1, structure['num_sections'] + 1):
                            section, created = Section.objects.get_or_create(
                                class_obj=class_obj,
                                name=str(section_num),
                                defaults={'name': str(section_num)}
                            )
                            
                            if created:
                                total_sections += 1

                # Progress indicator
                if program.id % 10 == 0:
                    self.stdout.write(
                        f"  Processed {program.id}/{programs.count()} programs... "
                        f"({total_courses} courses, {total_classes} classes, {total_sections} sections)"
                    )

            # Summary
            self.stdout.write(self.style.HTTP_INFO('━' * 100))
            self.stdout.write(self.style.SUCCESS('✅ Structure creation completed successfully!'))
            self.stdout.write(self.style.SUCCESS(f'   Courses created: {total_courses}'))
            self.stdout.write(self.style.SUCCESS(f'   Classes created: {total_classes}'))
            self.stdout.write(self.style.SUCCESS(f'   Sections created: {total_sections}'))
            self.stdout.write(self.style.HTTP_INFO('━' * 100))
            
            # Show sample structure
            self.stdout.write(f"\n{self.style.HTTP_INFO('📋 Sample Structure (First CSE Program):')}")
            cse_program = Program.objects.filter(department__code='CSE').first()
            if cse_program:
                courses = cse_program.courses.all()[:1]
                for course in courses:
                    self.stdout.write(f"  Program: {cse_program.name}")
                    self.stdout.write(f"    └─ Course: {course.name}")
                    for cls in course.classes.all()[:2]:
                        sections = cls.sections.all()
                        section_nums = ', '.join([s.name for s in sections[:5]]) + ', ...'
                        self.stdout.write(
                            f"       └─ {cls.name} ({sections.count()} sections): {section_nums}"
                        )
