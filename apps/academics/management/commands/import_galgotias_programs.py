"""
Management command to import Galgotias University's complete program structure.

Usage:
    python manage.py import_galgotias_programs
    python manage.py import_galgotias_programs --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academics.models import Department, Program


class Command(BaseCommand):
    help = 'Import Galgotias University departments and programs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing departments and programs before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Program.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared'))

        # Structured data: School → Department → Programs
        data = {
            "School of Computer Science and Engineering": {
                "Department of Computer Science & Engineering": {
                    "code": "CSE",
                    "programs": [
                        "B.Tech in Computer Science and Engineering (NBA Accredited)",
                        "B.Tech in Computer Science and Engineering (Artificial Intelligence & Machine Learning)",
                        "B.Tech in Computer Science and Engineering (Artificial Intelligence)",
                        "B.Tech in Computer Science and Engineering (Data Science)",
                        "B.Tech in Computer Science and Engineering (Computer Network and Cyber Security)",
                        "B.Tech in Computer Science and Engineering (Data Analytics)",
                        "B.Tech in Computer Science and Engineering (Cyber Security)",
                        "B.Tech in Computer Science and Engineering (Cyber Security and Digital Forensic)",
                        "B.Tech in Computer Science and Engineering (Gaming Technology)",
                        "B.Tech in Computer Science and Engineering (Cloud Computing and Virtualization)",
                        "B.Tech in Computer Science and Engineering (Full Stack Development)",
                        "B.Tech in Computer Science and Engineering (Internet of Things and Cyber Security Including Block Chain Technology)",
                        "B.Tech in Computer Science and Engineering (Business Analytics and Optimization)",
                        "B.Tech in Artificial Intelligence and Machine Learning",
                        "B.Tech in Artificial Intelligence and Data Science",
                        "B.Tech in Computer Science and Engineering (For Working Professionals Only)",
                        "M.Tech in Computer Science and Engineering (Data Science)",
                        "M.Tech in Computer Science and Engineering",
                        "M.Tech in Computer Science and Engineering (Cyber Security)",
                        "M.Tech in Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
                        "M.Tech in Computer Science and Engineering - For Working Professionals Only",
                        "M.Tech in Computer Science and Engineering (Cyber Security) - For Working Professionals Only",
                        "M.Tech in Computer Science and Engineering (Data Science) - For Working Professionals Only",
                        "M.Tech in Computer Science and Engineering (Artificial Intelligence and Machine Learning) - For Working Professionals Only",
                        "Doctor of Philosophy (Ph.D.) in Artificial Intelligence & Machine Learning",
                        "Doctor of Philosophy (Ph.D.) in Artificial Intelligence and Data Science",
                        "Doctor of Philosophy (Ph.D.) in Cyber Security",
                        "Doctor of Philosophy (Ph.D.) in Computer Science Engineering",
                    ]
                }
            },
            "School of Artificial Intelligence": {
                "Department of Artificial Intelligence": {
                    "code": "AI",
                    "programs": [
                        "Bachelor of Business Administration (BBA) Artificial Intelligence In Fintech and Banking Innovation",
                        "Bachelor of Business Administration (BBA) Artificial Intelligence In Human Resource Management",
                        "Bachelor of Business Administration (BBA) Artificial Intelligence In Digital Marketing and Consumer Insights",
                        "Bachelor of Business Administration (BBA) Artificial Intelligence In MediaTech and Content Intelligence",
                        "Bachelor of Business Administration (BBA) Artificial Intelligence In Supply Chain and Operations Management",
                        "Bachelor of Science (B.Sc) Artificial Intelligence In Digital Twin and Extended Reality (XR)",
                        "Bachelor of Science (B.Sc) Artificial Intelligence In Agentic AI (Autonomous Intelligent Systems)",
                        "Bachelor of Science (B.Sc) Artificial Intelligence In Agritech and Smart Farming",
                        "Bachelor of Science (B.Sc) Artificial Intelligence In Robotics and Intelligent Systems",
                        "Bachelor of Science (B.Sc) Artificial Intelligence In Healthcare AI and Bioinformatics",
                        "Bachelor of Science (B.Sc) Artificial Intelligence In Data Science and Advanced Analytics",
                    ]
                }
            },
            "School of Aviation, Logistics & Tourism Management": {
                "Department of Aviation, Logistics & Tourism Management": {
                    "code": "ALTM",
                    "programs": [
                        "BBA Aviation Management",
                        "BBA (Hons. With Research) Aviation Management",
                        "BBA Logistics and Supply Chain Management",
                        "BBA (Hons. With Research) Logistics and Supply Chain Management",
                        "Bachelor of Business Administration (BBA) Tourism and Travel",
                        "BBA (Hons. with Research) Tourism and Travel",
                        "MBA in Aviation Management",
                        "MBA in Logistics and Supply Chain Management",
                        "Master of Business Administration (MBA) – Tourism and Travel Management",
                    ]
                }
            },
            "School Of Forensic Sciences": {
                "Department of Forensic Sciences": {
                    "code": "FORS",
                    "programs": [
                        "B.Sc. (Hons.) Forensic Science",
                        "B.Sc. (Hons. with Research) Forensic Science",
                        "B.Sc. (Hons) Forensic Science with specialization in Questioned Documents and Fingerprints",
                        "B.Sc. (Hons with Research) Forensic Science with specialization in Questioned Documents and Fingerprints",
                        "B.Sc. (Hons) Forensic Science with specialization in Forensic Biology and Serology",
                        "B.Sc. (Hons with Research) Forensic Science with specialization in Forensic Biology and Serology",
                        "B.Sc. (Hons) Forensic Science with specialization in Forensic Toxicology and Explosives",
                        "B.Sc. (Hons with Research) Forensic Science with specialization in Forensic Toxicology and Explosives",
                        "B.Sc. (Hons) Forensic Science with specialization in Cyber and Multimedia Forensics",
                        "B.Sc. (Hons with Research) Forensic Science with specialization in Cyber and Multimedia Forensics",
                        "B.Sc. (Hons) Forensic Science with specialization in Forensic Physics and Ballistics",
                        "B.Sc. (Hons with Research) Forensic Science with specialization in Forensic Physics and Ballistics",
                        "Integrated B.Sc. and M.Sc. Forensic Science",
                        "M.Sc. Forensic Science",
                        "M.Sc. Forensic Sciences with specialization in Questioned Documents and Fingerprints",
                        "M.Sc. Forensic Science with specialization in Forensic Biology and Serology",
                        "M.Sc. Forensic Science with specialization in Forensic Toxicology and Explosives",
                        "M.Sc. Forensic Science with specialization in Cyber and Multimedia Forensics",
                        "M.Sc. Forensic Science with specialization in Forensic Physics and Ballistics",
                        "Post-Graduate Diploma in Questioned Documents and Fingerprints",
                        "Post-Graduate Diploma in Crime Scene Management",
                        "Post-Graduate Diploma in Forensic Photography",
                        "Post-Graduate Diploma in Forensic Toxicology and Explosives",
                        "Post-Graduate Diploma in Forensic Biology and Serology",
                        "Post-Graduate Diploma in Forensic Ballistics",
                        "Post-Graduate Diploma in Multimedia Forensics",
                        "Post-Graduate Diploma in Cyber and Digital Forensics",
                        "Certificate course in Social Media Crimes",
                        "Certificate course in Advanced crime scene management",
                        "Certificate course in Forensic photography",
                        "Certificate course in Graphology and personality profiling",
                        "Doctor of Philosophy (Ph.D.) in Forensic Science",
                    ]
                }
            },
            "School of Computer Applications & Technology": {
                "Department of Computer Applications and Technology": {
                    "code": "CAT",
                    "programs": [
                        "B.Sc (Hons) Computer Science",
                        "B.Sc. (Hons. with Research) Computer Science",
                        "B.Sc. (Hons.) Computer Science (Cloud Computing)",
                        "B.Sc (Hons. with Research) Computer Science (Cloud Computing)",
                        "B.Sc (Hons ) Computer Science (Cyber Security)",
                        "B.Sc. (Hons. with Research) Computer Science (Cyber Security)",
                        "B.Sc. (Hons.) Computer Science (Data Science)",
                        "B.Sc. (Hons. with Research) Computer Science (Data Science)",
                        "B.Sc. (Hons.) Computer Science (Game Design and Development)",
                        "B.Sc (Hons. with Research) Computer Science (Game Design and Development)",
                        "BCA",
                        "BCA (Hons. with Research)",
                        "B.C.A. in Industry Oriented Specialization (Artificial Intelligence and Machine Learning)",
                        "BCA (Hons. with Research) in Industry Oriented Specialization (Artificial Intelligence and Machine Learning)",
                        "B.C.A. in Industry Oriented Specialization (Cloud Computing and Virtualization)",
                        "BCA (Hons. with Research) in Industry Oriented Specialization (Cloud Computing and Virtualization)",
                        "B.C.A. in Industry Oriented Specialization (Computer Networks and Cyber Security)",
                        "BCA (Hons. with Research) in Industry Oriented Specialization (Computer Networks and Cyber Security)",
                        "B.C.A. in Industry Oriented Specialization (Data Analytics)",
                        "B.C.A. (Hons. with Research) in Industry Oriented Specialization (Data Analytics)",
                        "BCA in Industry Oriented Specialization ( Multimedia and Animation)",
                        "BCA (Hons. with Research) in Industry Oriented Specialization (Multimedia and Animation)",
                        "Integrated BCA + MCA",
                        "Bachelor of Science (BSc) in Cognitive Computing",
                        "M. Sc. Computer Science",
                        "M.C.A.",
                        "M.C.A. (Industry Oriented Specialization in Web Designing & Security)",
                        "M.C.A. ( Industry Oriented Specialization in Cloud Computing )",
                        "M.C.A. (Industry Oriented Specialization in Computer Network & Cyber Security)",
                        "M.C.A. (Industry Oriented Specialization in Artificial Intelligence & Machine Learning)",
                        "M.C.A. (Industry Oriented Specialization in Data Analytics)",
                        "M.Sc in Data Science",
                        "Doctor of Philosophy (Ph.D.) in Computer Applications",
                        "Doctor of Philosophy (Ph.D.) in Computer Science",
                    ]
                }
            },
            "School of Engineering": {
                "Department of Civil Engineering": {
                    "code": "CE",
                    "programs": [
                        "B.Tech in Civil Engineering",
                        "B.Tech (Hons) in Civil Engineering (Smart Cities)",
                        "B.Tech in Civil Engineering (Geographical Information Systems and Remote Sensing)",
                        "M.Tech in Geotechnical Engineering",
                        "M.Tech in Structural Engineering",
                        "M.Tech in Transportation Engineering",
                        "M.Tech in Structural Engineering (For Working Professionals Only)",
                        "M.Tech in Transportation Engineering (For Working Professionals Only)",
                        "Doctor of Philosophy (Ph.D.) in Civil Engineering",
                    ]
                },
                "Department of Electrical, Electronics and Communication Engineering": {
                    "code": "EECE",
                    "programs": [
                        "B.Tech in Electronics & Communication Engineering (NBA Accredited)",
                        "B.Tech. in Electronics and Computer Engineering",
                        "B.Tech in Electronics and Communication Engineering (Artificial Intelligence and Machine Learning)",
                        "B.Tech in Electrical Engineering",
                        "B.Tech in Electrical Engineering (Electric Vehicle)",
                        "B.Tech. in Electrical and Computer Engineering",
                        "B.Tech in Electrical and Electronics Engineering",
                        "B.Tech Electronics Engineering (VLSI Design and Technology)",
                        "Bachelor of Technology in Embedded Systems",
                        "B.Tech Electronics and Communication (Advanced Communication Technology)",
                        "B.Tech in Electronics and Communication Engineering (For Working Professionals Only)",
                        "M.Tech in Power System Engineering",
                        "M.Tech Communication Engineering (Satellite Communication)",
                        "M.Tech Electronics Engineering (VLSI Design and Technology)",
                        "M.Tech Electronics and Communication (Advanced Communication Technology)",
                        "M.Tech in Power System Engineering (For Working Professionals Only)",
                        "Doctor of Philosophy (Ph.D.) in Electronics & Communication Engineering",
                        "Doctor of Philosophy (Ph.D.) in Electrical Engineering",
                    ]
                },
                "Department of Mechanical Engineering": {
                    "code": "ME",
                    "programs": [
                        "B.Tech Mechanical Engineering (NBA Accredited)",
                        "B.Tech Mechanical Engineering with specialization in E-Vehicles & Autonomous Vehicles",
                        "B.Tech in Mechanical Engineering (For Working Professionals Only)",
                        "B.Tech in Mechanical Engineering with Artificial Intelligence and Machine Learning",
                        "Bachelor of Technology in Mechatronics",
                        "Bachelor of Technology in Robotics",
                        "M.Tech in Industrial & Production Engineering",
                        "M.Tech in Mechanical Engineering with specialization in CAD/CAM and Robotics",
                        "Doctor of Philosophy (Ph.D.) in Mechanical Engineering",
                    ]
                }
            },
            "School of Business": {
                "Department of Management": {
                    "code": "MGT",
                    "programs": [
                        "BBA",
                        "BBA (Hons with Research)",
                        "BBA (Digital Marketing)",
                        "BBA (Business Analytics)",
                        "BBA (Hons. With Research) Business Analytics",
                        "BBA Marketing and Automobile Management",
                        "BBA (Hons. With Research) Marketing and Automobile Management",
                        "BBA International Accounting and Finance",
                        "Integrated MBA (BBA with MBA)",
                        "MBA with Dual Specialization",
                        "MBA (Digital Marketing)",
                        "Doctor of Philosophy (Ph.D.) in Management",
                    ]
                }
            },
            "School of Law": {
                "Department of Legal Studies": {
                    "code": "LAW",
                    "programs": [
                        "Integrated BA +LL.B (Hons)",
                        "Integrated BBA +LL.B (Hons)",
                        "Bachelor of Laws (LL.B.) (Hons.)",
                        "Master of Laws in Constitutional Law and Governance",
                        "Master of Laws in Corporate Law",
                        "Master of Laws in Criminal Law and Criminal Justice",
                        "Master of Laws in Environmental Law",
                        "Master of Laws in Intellectual Property Law",
                        "Master of Laws in Law and Emerging Technology",
                        "Doctor of Philosophy (Ph.D.) in Law",
                    ]
                }
            },
            "School of Finance and Commerce": {
                "Department of Finance and Commerce": {
                    "code": "FIN",
                    "programs": [
                        "B.Com (Hons.)",
                        "B.Com. (Hons. with Research)",
                        "B.Com. (Hons) International Accounting and Finance with ACCA",
                        "B.Com (Hons. with Research) International Accounting and Finance with ACCA",
                        "B.Com (Honours) Applied Finance and Analytics",
                        "B.Com (Honours with research) Applied Finance and Analytics",
                        "B.Com (Hons.) Financial Markets",
                        "BBA Financial Investment Analysis",
                        "BBA Banking, Financial Services and Insurance",
                        "BBA (Hons. With Research) Banking, Financial Services and Insurance",
                        "BBA (Hons. With Research) Financial Investment Analysis",
                        "B.Com (Hons. with Research) Financial Markets",
                        "M.Com",
                        "Master in Finance & Control",
                        "MBA Financial Management",
                    ]
                }
            },
            "School of Liberal Education": {
                "Department of Humanities": {
                    "code": "HUM",
                    "programs": [
                        "B.A. (Hons.) in Psychology",
                        "BA (Hons. with Research) Psychology",
                        "B.A. (Hons.) in Economics",
                        "B.A. (Hons. with Research) Economics",
                        "B.A. (Hons.) in Political Science",
                        "B.A. (Hons. with Research) Political Science",
                        "B.A. (Hons.) in Sociology",
                        "B.A. (Hons. with Research) Sociology",
                        "B.A. (Hons.) Liberal Arts",
                        "B. Sc. (Hons. With Research) Economics",
                        "BA (Hons) Social Work",
                        "B.A. (Hons with research) Public Policy & Governance",
                        "M.A. Psychology",
                        "M.A. in Economics",
                        "M.A. in Political Science",
                        "M.A in Sociology",
                        "MA Public Policy",
                        "MSc Cognitive Sciences, Learning & Technology",
                        "Master of Social Work",
                        "PG Diploma in Counselling Psychology",
                        "M.A. (Politics and International Relations)",
                        "Doctor of Philosophy (Ph.D.) in Psychology",
                        "Doctor of Philosophy (Ph.D.) in Political Science",
                        "Doctor of Philosophy (Ph.D.) in Economics",
                        "Doctor of Philosophy (Ph.D.) in Sociology",
                    ]
                }
            },
            "School of Languages": {
                "Department of Languages": {
                    "code": "LANG",
                    "programs": [
                        "Certificate in Japanese",
                        "Certificate in French",
                        "B.A. (Hons.) Japanese",
                        "B.A. (Hons.) French",
                        "B.A. (Hons.) in English",
                        "B.A. (Hons. with Research) English",
                        "M.A. French",
                        "M.A. in English",
                        "M.A. (Linguistics)",
                        "Doctor of Philosophy (Ph.D.) in English",
                    ]
                }
            },
            "School of Medical and Allied Sciences": {
                "Department of Pharmacy": {
                    "code": "PHAR",
                    "programs": [
                        "D. Pharm (Diploma in Pharmacy) (Approved by Pharmacy Council of India)",
                        "Bachelor of Pharmacy (Approved by Pharmacy Council of India) (NBA Accredited)",
                        "Master of Pharmacy (Pharmaceutical Chemistry) (Approved by Pharmacy Council of India)",
                        "Master of Pharmacy (Pharmaceutics) (Approved by Pharmacy Council of India)",
                        "Master of Pharmacy (Pharmacology) (Approved by Pharmacy Council of India)",
                        "MBA (Pharmaceutical Management)",
                        "M.pharma (Regulatory Affairs) (Approved by Pharmacy Council of India)",
                        "M.pharma (Pharmaceutical Analysis) (Approved by Pharmacy Council of India)",
                        "Doctor of Philosophy (Ph.D.) in Pharmacy",
                    ]
                },
                "Department of Nursing": {
                    "code": "NURS",
                    "programs": [
                        "B.Sc in Nursing",
                    ]
                },
                "Department of Allied Health Sciences": {
                    "code": "AHS",
                    "programs": [
                        "Yoga Instructor Course (YIC)",
                        "Diploma in Advanced Music Therapy",
                        "B.Sc (Yoga Therapy)",
                        "Bachelor of Physiotherapy (B.P.T.)",
                        "Bachelor of Medical Lab Science",
                        "Bachelor In Anaesthesia and Operation Theatre Technology",
                        "Bachelor of Optometry",
                        "Bachelor of Cardiovascular Technology",
                        "Bachelor In Medical Radiology and Imaging Technology",
                        "Bachelor of Emergency Medical Technology",
                        "Bachelor of Respiratory Technology",
                        "Bachelor of Science in Health Information Management",
                        "Master of Physiotherapy in Cardio- Pulmonary Sciences",
                        "Master of Physiotherapy in Obstetrics and Gynaecology Sciences",
                        "Master of Physiotherapy in Sports Sciences",
                        "Master of Physiotherapy in Muskuloskeletal Sciences",
                        "Master of Physiotherapy in Neuro Sciences",
                        "Master of Optometry",
                        "M.Sc in Cardiovascular Technology",
                        "M.Sc. in Medical Laboratory Technology (Medical Biochemistry)",
                        "M.Sc. in Medical Laboratory Technology (Medical Microbiology)",
                        "M.Sc. in Medical Laboratory Technology (Histology and Cytology)",
                        "M.Sc. in Medical Laboratory Technology (Hematology and Transfusion Medicine)",
                        "M.Sc (Yoga Therapy)",
                        "MBA in Healthcare Management",
                        "PG Diploma in Advanced Music Therapy",
                        "Doctor of Philosophy (Ph.D.) in Physiotherapy",
                        "Doctor of Philosophy (Ph.D.) in Medical Lab Technology",
                        "Doctor of Philosophy (Ph.D.) in Optometry",
                    ]
                }
            },
            "School of Agriculture": {
                "Department of Agriculture": {
                    "code": "AGRI",
                    "programs": [
                        "B.Sc. (Hons.) Agriculture",
                        "M.Sc (Agriculture) Agronomy",
                        "M.Sc (Agriculture ) Entomology",
                        "M.Sc (Agriculture) Soil Science",
                        "M.Sc (Hort.) Fruit Science",
                        "MBA (Agribusiness Management)",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Agri Economics)",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Agronomy)",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Entomology)",
                        "Doctor of Philosophy (Ph.D.) in ( Horticulture ) Fruit Science",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Genetics and Plant Breeding)",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Plant Pathology)",
                        "Doctor of Philosophy (Ph.D.) in Agricultural Biotechnology",
                        "Doctor of Philosophy (Ph.D.) in Agribusiness Management",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Soil Science)",
                        "Doctor of Philosophy (Ph.D.) in Agriculture (Agricultural Extension)",
                    ]
                }
            },
            "School of Basic Sciences": {
                "Department of Physics": {
                    "code": "PHY",
                    "programs": [
                        "B.Sc (General) PCM",
                        "B.Sc (Hons. with Research) (General) PCM",
                        "B.Sc (Hons.) Physics",
                        "B.Sc. (Hons. with Research) Physics",
                        "M.Sc. in Physics",
                        "Doctor of Philosophy (Ph.D.) in Physics",
                    ]
                },
                "Department of Chemistry & Sustainability": {
                    "code": "CHEM",
                    "programs": [
                        "B.Sc (Hons) Chemistry",
                        "B.Sc (Hons. with Research) Chemistry",
                        "B.Sc. (Hons) in Climate Change and Sustainability",
                        "B.Sc. (Hons with Research) in Climate Change and Sustainability",
                        "B.Sc. (Hons) in Chemistry with Specialization in Synthetic Chemistry",
                        "B.Sc. (Hons with Research) in Chemistry with Specialization in Synthetic Chemistry",
                        "Bachelor of Science (Hons) in Green Hydrogen",
                        "Bachelor of Science (Hons with Research) in Green Hydrogen",
                        "M.Sc. Chemistry",
                        "Master of Science (M.Sc.) in Green Hydrogen",
                        "M.Sc. in Sustainability",
                        "Doctor of Philosophy (Ph.D.) in Chemistry",
                        "Doctor of Philosophy (Ph.D.) in Environmental Sciences",
                        "Doctor of Philosophy (Ph.D.) in Sustainability",
                    ]
                },
                "Department of Mathematics & Statistics": {
                    "code": "MATH",
                    "programs": [
                        "B.Sc. (Hons.) in Mathematics",
                        "B.Sc. (Hons. with Research) Mathematics",
                        "B.Sc. (Hons) in Statistics & Data Science",
                        "B.Sc. (Hons with Research) in Statistics & Data Science",
                        "B.Sc. (Hons) in Mathematics with Specialization in Computational Mathematics",
                        "B.Sc. (Hons with Research) in Mathematics with Specialization in Computational Mathematics",
                        "M.Sc. in Mathematics",
                        "Doctor of Philosophy (Ph.D.) in Mathematics",
                    ]
                }
            },
            "School of Media & Communication Studies": {
                "Department of Mass Communication": {
                    "code": "MEDIA",
                    "programs": [
                        "Certificate Course in Art of Anchoring & Presentation (In association with India Today Media Institute)",
                        "Certificate Course in Event Management (In association with India Today Media Institute)",
                        "Certificate Course in Data Journalism (In association with India Today Media Institute)",
                        "Certificate Course in Media Graphics and Visualization (In association with India Today Media Institute)",
                        "Certificate Course in Integrated Marketing Communication (In association with India Today Media Institute)",
                        "Certificate Course in AI in Newsroom (In association with India Today Media Institute)",
                        "B.A. Journalism and Mass Communication",
                        "BA (Hons. with Research) Journalism and Mass Communication",
                        "B.A. Film Production & Theatre",
                        "BA (Hons. with Research) Film Production and Theatre",
                        "B.A. Strategic Communication",
                        "BA (Hons. with Research) Strategic Communication",
                        "B.Sc. Cinema in association with GKFTII",
                        "Bachelor of Arts (Journalism and Media)",
                        "BA (Hons.) in Digital Media and Communication (In association with India Today Media Institute)",
                        "M.A. Journalism and Mass Communication",
                        "M.Sc. Cinema in association with GKFTII",
                        "Doctor of Philosophy (Ph.D.) in Mass Communication",
                    ]
                }
            },
            "School of Design": {
                "Department of Design": {
                    "code": "DES",
                    "programs": [
                        "Bachelor of Design (Fashion Design) (In Association with GKFTII)",
                        "Bachelor of Design in Interior and Spatial Design",
                        "Bachelor of Design in Advertising, Graphics & Web Design",
                        "B.Sc. Fashion Design (In Association with GKFTII)",
                        "Bachelor of Design (B. Des) in Communication Design",
                        "Bachelor of Design (B.Des.) in Product Design",
                        "Master of Design (M.Des.) in Interior and Spatial Design",
                        "M.Sc. In Fashion Design(In Association with GKFTII)",
                        "M. Design in Interaction Design",
                        "M. Design in Design Research & Insights",
                    ]
                }
            },
            "School of Hospitality": {
                "Department of Hospitality": {
                    "code": "HOSP",
                    "programs": [
                        "Bachelor of Hotel Management",
                        "B.Sc. Hotel Management",
                        "Bachelor of Science (Hons) in Culinary Arts",
                        "Bachelor of Business Administration (BBA) Hospitality and Service Management",
                        "Bachelor of Science (Hons with Research)in Culinary Arts",
                        "B.Sc. (Hons. with Research) Hotel Management",
                        "Masters in Hospitality Management",
                        "Masters in Culinary Management & Food Entrepreneurship",
                        "MBA Hospitality and Service Management",
                        "Doctor of Philosophy in Hospitality Management",
                        "Doctor of Philosophy in Hotel and Tourism Management",
                    ]
                }
            },
            "School of Biosciences and Technology": {
                "Department of Biotechnology & Bioengineering": {
                    "code": "BIO",
                    "programs": [
                        "B.Tech in Biotechnology",
                        "B.Tech in Biomedical Engineering",
                        "B. Tech. Chemical & Biochemical Engineering",
                        "B.Tech in Bioinformatics (Specialization in Artifical Intelligence)",
                        "M.Tech Biotechnology & Biochemical Engineering",
                        "M. Tech. Biomedical Engineering",
                        "M.Tech in Bioinformatics",
                    ]
                },
                "Department of Life Sciences": {
                    "code": "LIFE",
                    "programs": [
                        "B.Sc. (General) ZBC",
                        "B.Sc. (Hons.) Biomedical Science",
                        "B.Sc. (Hons. with Research) Biomedical Science",
                        "B.Sc. (Hons.) Microbiology",
                        "B.Sc (Hons. with Research) Microbiology",
                        "B.Sc. (Hons.) Zoology",
                        "B.Sc(Hons. with Research) in Zoology",
                        "B.Sc. (Hons.) Biochemistry",
                        "B.Sc (Hons. with Research) in Biochemistry",
                        "B.Sc. (Hons.) Biological Sciences",
                        "B.Sc. (Hons. with Research) Biological Science",
                        "B.Sc (Hons) Biotechnology",
                        "B.Sc. (Hons) Bioinformatics",
                        "B.Sc. (Hons with Research) Bioinformatics",
                        "B.Sc. (Honors with Research) Biotechnology",
                        "M.Sc. Biotechnology",
                        "M.Sc. Biological Science",
                        "M.Sc. Microbiology",
                        "M.Sc. Biochemistry",
                        "M.Sc. Biomedical Science",
                        "M.Sc. Computational Biology and Bioinformatics",
                        "M.Sc. Zoology",
                        "Doctor of Philosophy (Ph.D.) in Bio-Chemistry",
                        "Doctor of Philosophy (Ph.D.) in Microbiology",
                        "Doctor of Philosophy (Ph.D) in Zoology",
                        "Doctor of Philosophy (Ph.D.) in Biotechnology",
                        "Doctor of Philosophy (Ph.D.) in Biological Sciences",
                    ]
                },
                "Department of Food Technology": {
                    "code": "FOOD",
                    "programs": [
                        "B.Sc Food Science And Dietetics",
                        "B.Tech in Food Technology",
                        "B.Sc (Hons.) Food Science And Technology",
                        "B.Sc (Hons. with Research) Food Science And Technology",
                        "B.Sc (Hons. with Research) Food Science and Dietetics",
                        "M.Sc Food Science And Technology",
                        "M.Sc. Food safety and Quality Assurance",
                        "M.Sc. in Food Science and Dietetics",
                    ]
                },
                "Department of Biomedical Sciences": {
                    "code": "BIOMED",
                    "programs": [
                        "B.Sc. Healthcare and Hospital Management",
                        "B.Sc (Hons. with Research) Healthcare and Hospital Management",
                        "B.Sc Healthcare and Clinical Research",
                        "B.Sc (Hons. with Research) Healthcare and Clinical Research",
                        "B.Sc. (Hons. with Research) Medical Biotechnology",
                        "B.Sc. In Medical Biotechnology",
                        "B.Sc (Hons. with Research) Medical Microbiology",
                        "B.Sc. Medical Biotechnology (Specialization in Bioinformatics)",
                        "B.Sc. Clinical Nutrition & Dietetics",
                        "B.Sc. (Hons. with Research) Clinical Nutrition and Dietetics",
                        "M.Sc Neuroscience with specialization in Cognitive Computing",
                        "M.Sc Nanoscience and Technology",
                        "M.Sc in Healthcare and Clinical Research",
                        "M.Sc. Medical Biotechnology",
                        "M.Sc Medical Microbiology",
                        "M.Sc. Medical Biotechnology (Specialization in Bioinformatics)",
                        "M.Sc. Public Health Administration",
                        "M.Sc. Clinical Nutrition and Dietetics",
                        "M.Sc. Industrial Biotechnology",
                        "Doctor of Philosophy (Ph.D.) in Clinical Research",
                        "Doctor of Philosophy (Ph.D.) in Medical Biotechnology",
                        "Doctor of Philosophy (Ph.D.) in Clinical Nutrition & Dietetics",
                    ]
                }
            },
            "Galgotias Polytechnic": {
                "University Polytechnic": {
                    "code": "POLY",
                    "programs": [
                        "Diploma in Computer Science & Engineering",
                        "Diploma in Computer Science & Engineering (Network Essential)",
                        "Diploma in Computer Science & Engineering (Web Designing)",
                        "Diploma in Computer Science & Engineering (Cloud Computing & IT Infrastructure)",
                        "Diploma in Computer Science & Engineering (AI & ML)",
                        "Diploma in Computer Science & Engineering (Data Analytics)",
                        "Diploma in Electrical Engineering (Electric Vehicle)",
                        "Diploma in Electrical Engineering (Renewable Energy)",
                        "Diploma in Electronics & Communication Engineering",
                        "Diploma in Mechanical Engineering",
                        "Diploma in Mechanical Engineering (Electric Vehicle)",
                        "Diploma in IC Manufacturing Engineering",
                        "Diploma in Civil Engineering",
                        "Diploma in Electrical Engineering",
                    ]
                }
            },
            "School of Vocational Education": {
                "Department of Vocational Education": {
                    "code": "VOC",
                    "programs": [
                        "Bachelor of Vocation (Banking, Insurance & Financial Services) in association with The George Telegraph Institute of Accounts",
                        "Bachelor of Vocation (Graphic Design & Multimedia Technologies) in association with Dice Academy",
                        "Bachelor of Vocation (Multimedia and Visual Communication) in association with Ecole Intuit Lab",
                        "Bachelor of Vocation (Multimedia and Digital Product Design) in association with Ecole Intuit Lab",
                        "Bachelor of Vocation (Multimedia and Game Art and Design) in association with Ecole Intuit Lab",
                        "Bachelor of Vocation (Multimedia and Animation and Motion Design) in association with Ecole Intuit Lab",
                        "B.Sc. (Industrial Automation) – Apprenticeship Embedded Degree Programme (in collaboration with Instrumentation Automation Surveillance & Communication Sector Skill Council – IASC SSC)",
                    ]
                }
            },
            "School of Education": {
                "Department of Education": {
                    "code": "EDU",
                    "programs": [
                        "B.A. B.Ed (approved by NCTE)",
                        "B.Sc. B.Ed (approved by NCTE)",
                        "B.Ed (Bachelor of Education)",
                        "M.Ed (Master of Education)",
                        "Doctor of Philosophy (Ph.D.) in Education",
                    ]
                }
            },
            "School of Defence Technology": {
                "Department of Defence Technology": {
                    "code": "DEF",
                    "programs": [
                        "Bachelor of Technology in Defence Technology (Aerospace Technology)",
                        "Bachelor of Technology in Defence Technology (Communication Systems & Sensors)",
                        "Bachelor of Technology in Defence Technology (AI & Cyber Security)",
                        "Bachelor of Technology in Defence Technology (Directed Energy Technology)",
                        "Master of Technology in Defence Technology (Communication Systems & Sensors)",
                        "Master of Technology in Defence Technology (AI & Cyber Security)",
                        "Master of Technology in Defence Technology (Directed Energy Technology)",
                        "Master of Technology in Defence Technology (Aerospace Technology)",
                    ]
                }
            }
        }

        with transaction.atomic():
            total_departments = 0
            total_programs = 0

            for school_name, departments in data.items():
                self.stdout.write(f"\n{self.style.HTTP_INFO('━' * 80)}")
                self.stdout.write(self.style.HTTP_INFO(f"📚 {school_name}"))
                self.stdout.write(self.style.HTTP_INFO('━' * 80))

                for dept_name, dept_data in departments.items():
                    code = dept_data['code']
                    programs_list = dept_data['programs']

                    # Create or get department
                    department, created = Department.objects.get_or_create(
                        code=code,
                        defaults={'name': dept_name}
                    )

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Created department: {code} - {dept_name}")
                        )
                        total_departments += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ Department exists: {code} - {dept_name}")
                        )

                    # Create programs
                    programs_created = 0
                    for program_name in programs_list:
                        program, prog_created = Program.objects.get_or_create(
                            department=department,
                            name=program_name
                        )
                        
                        if prog_created:
                            programs_created += 1
                            total_programs += 1

                    self.stdout.write(
                        self.style.SUCCESS(f"    → Added {programs_created} programs")
                    )

            # Summary
            self.stdout.write(f"\n{self.style.HTTP_INFO('━' * 80)}")
            self.stdout.write(self.style.SUCCESS(f"✅ Import completed successfully!"))
            self.stdout.write(self.style.SUCCESS(f"   Departments created: {total_departments}"))
            self.stdout.write(self.style.SUCCESS(f"   Programs created: {total_programs}"))
            self.stdout.write(self.style.HTTP_INFO('━' * 80))
