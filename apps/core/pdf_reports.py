"""
PDF report generation for parent portal
Generates attendance reports, fee receipts, and leave letters
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from apps.academics.models import AttendanceRecord, StudentFee, LeaveApplication


class PDFReportGenerator:
    """Generate PDF reports for parents"""

    @staticmethod
    def generate_attendance_report(student_profile, output_format='letter'):
        """Generate attendance report as PDF"""
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter if output_format == 'letter' else A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )
        
        elements.append(Paragraph("📋 Attendance Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Student Info
        info_data = [
            ["Student Name", student_profile.user.full_name],
            ["Admission No.", student_profile.admission_number],
            ["Enrollment No.", student_profile.enrollment_number],
            ["Section", str(student_profile.section)],
            ["Report Generated", datetime.now().strftime("%d %B %Y")],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Attendance Summary
        attendance_records = AttendanceRecord.objects.filter(
            student=student_profile
        ).order_by('-date')
        
        total = attendance_records.count()
        present = attendance_records.filter(status='present').count()
        absent = attendance_records.filter(status='absent').count()
        late = attendance_records.filter(status='late').count()
        
        if total > 0:
            percentage = (present / total) * 100
        else:
            percentage = 0
        
        summary_data = [
            ["Total Classes", "Present", "Absent", "Late", "Attendance %"],
            [str(total), str(present), str(absent), str(late), f"{percentage:.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed Records
        elements.append(Paragraph("Attendance Records", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        record_data = [["Date", "Subject", "Status", "Remarks"]]
        for record in attendance_records[:50]:  # Last 50 records
            record_data.append([
                record.date.strftime("%d/%m/%Y"),
                record.subject.name[:20],
                record.status.upper(),
                record.remarks[:30] if record.remarks else '-',
            ])
        
        record_table = Table(record_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
        record_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        elements.append(record_table)
        
        # Footer
        elements.append(Spacer(1, 0.4*inch))
        footer_text = f"This is an official attendance report. Generated on {datetime.now().strftime('%d %B %Y at %H:%M')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_fee_receipt(student_profile, fee_id=None):
        """Generate fee payment receipt as PDF"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )
        
        elements.append(Paragraph("💳 Fee Summary Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Student Info
        info_data = [
            ["Student Name", student_profile.user.full_name],
            ["Admission No.", student_profile.admission_number],
            ["Report Date", datetime.now().strftime("%d %B %Y")],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Fee Details
        fees = StudentFee.objects.filter(student=student_profile)
        
        fee_data = [["Fee Type", "Total Amount", "Paid", "Pending", "Status"]]
        total_amount = 0
        total_paid = 0
        total_pending = 0
        
        for fee in fees:
            fee_data.append([
                fee.fee_type.name,
                f"₹{fee.amount:.2f}",
                f"₹{fee.paid_amount:.2f}",
                f"₹{fee.pending_amount:.2f}",
                fee.status.upper(),
            ])
            total_amount += fee.amount
            total_paid += fee.paid_amount
            total_pending += fee.pending_amount
        
        fee_data.append([
            "TOTAL",
            f"₹{total_amount:.2f}",
            f"₹{total_paid:.2f}",
            f"₹{total_pending:.2f}",
            "—",
        ])
        
        fee_table = Table(fee_data, colWidths=[1.8*inch, 1.4*inch, 1.4*inch, 1.4*inch, 1.2*inch])
        fee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ]))
        
        elements.append(fee_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Note
        note_text = "For fee payment details and to make online payments, please log in to your Parent Portal."
        elements.append(Paragraph(note_text, ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )))
        
        # Footer
        elements.append(Spacer(1, 0.2*inch))
        footer_text = f"Generated on {datetime.now().strftime('%d %B %Y at %H:%M')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
