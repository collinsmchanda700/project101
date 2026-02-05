# report_generator.py - ENHANCED VERSION (added employee period report wrapper)
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class ReportGenerator:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self.reports_dir = "reports"
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    # NEW: Enhanced Employee Report with Working Hours
    def generate_employee_working_hours_report(self, employee_id, start_date, end_date):
        """Generate detailed employee report with working hours analysis"""
        employee = self.data_handler.get_employee_full_info(employee_id)
        if not employee:
            return None, "Employee not found"
        
        # Get attendance records for date range
        records = self.data_handler.get_employee_attendance(employee_id, start_date, end_date)
        
        # Calculate working hours and overtime
        hours_analysis = self.data_handler.calculate_overtime(employee_id, start_date, end_date)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employee_hours_report_{employee['name'].replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Employee Working Hours Report", 0, 1, 'C')
        pdf.ln(3)
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Name: {employee['name']}", 0, 1, 'C')
        pdf.cell(0, 10, f"Period: {start_date} to {end_date}", 0, 1, 'C')
        pdf.ln(5)
        
        # Employee Information
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Employee Information", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        info_lines = [
            f"Employee ID: {employee['id']}",
            f"Department: {employee.get('department', 'N/A')}",
            f"Role: {employee.get('role', 'N/A')}",
            f"Email: {employee.get('email', 'N/A')}",
            f"Phone: {employee.get('phone', 'N/A')}"
        ]
        
        for line in info_lines:
            pdf.cell(0, 6, line, 0, 1)
        
        pdf.ln(5)
        
        # Hours Summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Working Hours Summary", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        summary_lines = [
            f"Total Hours Worked: {hours_analysis['total_hours']:.2f} hours",
            f"Regular Hours: {hours_analysis['regular_hours']:.2f} hours",
            f"Overtime Hours: {hours_analysis['overtime_hours']:.2f} hours",
            f"Overtime Pay Rate: 1.5x",
            f"Overtime Pay Amount: ${hours_analysis['overtime_pay']:.2f}",
            f"Average Daily Hours: {hours_analysis['total_hours'] / max(len(records), 1):.2f} hours"
        ]
        
        for line in summary_lines:
            pdf.cell(0, 6, line, 0, 1)
        
        pdf.ln(5)
        
        if records:
            # Daily Attendance Details
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Daily Attendance Details", 0, 1)
            
            # Table header
            pdf.set_font("Arial", 'B', 9)
            col_widths = [30, 25, 25, 25, 25, 25]
            headers = ["Date", "Check-in", "Check-out", "Hours", "Status", "Overtime"]
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
            pdf.ln()
            
            # Table content
            pdf.set_font("Arial", '', 8)
            for record in records:
                hours = "N/A"
                overtime = "No"
                
                if record.get('check_in') and record.get('check_out'):
                    try:
                        check_in = datetime.strptime(record['check_in'], "%H:%M:%S")
                        check_out = datetime.strptime(record['check_out'], "%H:%M:%S")
                        hours = (check_out - check_in).seconds / 3600
                        
                        # Get employee's daily hours
                        hours_settings = self.data_handler.get_working_hours_settings()
                        employee_settings = hours_settings.get("employee_settings", {}).get(str(employee_id), {})
                        daily_hours = employee_settings.get("daily", hours_settings.get("standard_daily_hours", 8))
                        
                        if hours > daily_hours:
                            overtime = f"Yes (+{hours - daily_hours:.1f}h)"
                        else:
                            overtime = "No"
                        
                        hours = f"{hours:.2f}"
                    except:
                        hours = "N/A"
                        overtime = "N/A"
                
                row_data = [
                    record.get('date', ''),
                    record.get('check_in', 'N/A'),
                    record.get('check_out', 'N/A') if record.get('check_out') else "Not checked out",
                    hours,
                    record.get('status', ''),
                    overtime
                ]
                
                for i, data in enumerate(row_data):
                    pdf.cell(col_widths[i], 8, str(data), 1, 0, 'C')
                pdf.ln()
        
        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        
        pdf.output(filepath)
        return filepath, f"Employee working hours report generated: {filename}"
    
    # NEW: Generate Excel report for all students
    def generate_students_excel_report(self, class_filter=None):
        """Generate Excel report of all students"""
        df = self.data_handler.export_students_to_excel(class_filter)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if class_filter:
            filename = f"students_{class_filter.replace(' ', '_')}_{timestamp}.xlsx"
        else:
            filename = f"all_students_{timestamp}.xlsx"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Students']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filepath, f"Students Excel report generated: {filename}"
    
    # NEW: Generate detailed employee attendance report as Excel
    def generate_employee_attendance_excel(self, employee_id, start_date, end_date):
        """Generate Excel report for employee attendance"""
        employee = self.data_handler.get_employee_full_info(employee_id)
        if not employee:
            return None, "Employee not found"
        
        records = self.data_handler.get_employee_attendance(employee_id, start_date, end_date)
        
        # Prepare data for DataFrame
        data = []
        total_hours = 0
        present_days = 0
        absent_days = 0
        late_days = 0
        
        for i, record in enumerate(records, 1):
            hours_worked = 0
            overtime = 0
            
            if record.get('check_in') and record.get('check_out'):
                try:
                    check_in = datetime.strptime(record['check_in'], "%H:%M:%S")
                    check_out = datetime.strptime(record['check_out'], "%H:%M:%S")
                    hours_worked = (check_out - check_in).seconds / 3600
                    total_hours += hours_worked
                except:
                    pass
            
            status = record.get('status', '')
            if status == 'Present':
                present_days += 1
            elif status == 'Absent':
                absent_days += 1
            elif status == 'Late':
                late_days += 1
            
            data.append({
                "No.": i,
                "Date": record.get('date', ''),
                "Check-in": record.get('check_in', 'N/A'),
                "Check-out": record.get('check_out', 'N/A'),
                "Hours Worked": f"{hours_worked:.2f}",
                "Status": status,
                "Remarks": ""
            })
        
        # Summary row
        data.append({
            "No.": "SUMMARY",
            "Date": f"{start_date} to {end_date}",
            "Check-in": "",
            "Check-out": "",
            "Hours Worked": f"Total: {total_hours:.2f}h",
            "Status": f"Present:{present_days} Absent:{absent_days} Late:{late_days}",
            "Remarks": ""
        })
        
        df = pd.DataFrame(data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employee_attendance_{employee['name'].replace(' ', '_')}_{start_date}_to_{end_date}_{timestamp}.xlsx"
        filepath = os.path.join(self.reports_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance', index=False)
            worksheet = writer.sheets['Attendance']
            # Set basic column widths
            for col in worksheet.columns:
                max_length = 0
                column_letter = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 30)
        
        return filepath, f"Employee attendance report generated: {filename}"
    
    # Keep existing methods
    def export_to_excel(self, records, filename=None):
        """Export attendance records to Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_report_{timestamp}.xlsx"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Prepare data for DataFrame
        data = []
        for record in records:
            hours_worked = ""
            if record.get("check_in") and record.get("check_out"):
                try:
                    check_in = datetime.strptime(record["check_in"], "%H:%M:%S")
                    check_out = datetime.strptime(record["check_out"], "%H:%M:%S")
                    hours = (check_out - check_in).seconds / 3600
                    hours_worked = f"{hours:.2f}"
                except:
                    hours_worked = "N/A"
            
            data.append({
                "Date": record.get("date", ""),
                "Employee ID": record.get("employee_id", ""),
                "Employee Name": record.get("employee_name", ""),
                "Department": record.get("department", ""),
                "Check-in": record.get("check_in", ""),
                "Check-out": record.get("check_out", ""),
                "Hours Worked": hours_worked,
                "Status": record.get("status", "")
            })
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        
        return filepath
    
    def generate_pdf_report(self, records, title="Attendance Report"):
        """Generate PDF report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_report_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
        
        # Report generation date
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Summary statistics
        total_employees = len(set(r['employee_id'] for r in records))
        present_count = sum(1 for r in records if r.get('status') == 'Present')
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Summary", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"Total Records: {len(records)}", 0, 1)
        pdf.cell(0, 8, f"Total Employees: {total_employees}", 0, 1)
        pdf.cell(0, 8, f"Present: {present_count}", 0, 1)
        pdf.ln(10)
        
        # Table header
        pdf.set_font("Arial", 'B', 10)
        col_widths = [25, 40, 30, 25, 25, 20]
        headers = ["Date", "Employee", "Department", "Check-in", "Check-out", "Status"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()
        
        # Table content
        pdf.set_font("Arial", '', 8)
        for record in records:
            hours_worked = ""
            if record.get("check_in") and record.get("check_out"):
                try:
                    check_in = datetime.strptime(record["check_in"], "%H:%M:%S")
                    check_out = datetime.strptime(record["check_out"], "%H:%M:%S")
                    hours = (check_out - check_in).seconds / 3600
                    hours_worked = f"{hours:.2f}h"
                except:
                    hours_worked = "N/A"
            
            row_data = [
                record.get("date", ""),
                record.get("employee_name", ""),
                record.get("department", ""),
                record.get("check_in", "N/A"),
                record.get("check_out", "N/A") if record.get("check_out") else "Not checked out",
                record.get("status", "")
            ]
            
            for i, data in enumerate(row_data):
                if i == 1 and len(data) > 15:
                    data = data[:12] + "..."
                pdf.cell(col_widths[i], 8, str(data), 1, 0, 'C')
            pdf.ln()
        
        # Save PDF
        pdf.output(filepath)
        return filepath
    
    def print_summary_report(self, start_date, end_date):
        """Generate and return a summary report for date range"""
        records = self.data_handler.get_attendance_by_range(start_date, end_date)
        
        if not records:
            return "No records found for the specified period."
        
        summary = f"Attendance Report: {start_date} to {end_date}\n"
        summary += "=" * 50 + "\n"
        summary += f"Total Records: {len(records)}\n"
        
        # Group by employee
        employees = {}
        for record in records:
            emp_id = record['employee_id']
            if emp_id not in employees:
                employees[emp_id] = {
                    'name': record['employee_name'],
                    'department': record['department'],
                    'days_present': 0,
                    'total_hours': 0
                }
            
            if record.get('status') == 'Present':
                employees[emp_id]['days_present'] += 1
            
            if record.get('check_in') and record.get('check_out'):
                try:
                    check_in = datetime.strptime(record['check_in'], "%H:%M:%S")
                    check_out = datetime.strptime(record['check_out'], "%H:%M:%S")
                    hours = (check_out - check_in).seconds / 3600
                    employees[emp_id]['total_hours'] += hours
                except:
                    pass
        
        summary += "\nEmployee Summary:\n"
        for emp_id, data in employees.items():
            summary += f"\n{data['name']} ({data['department']}):\n"
            summary += f"  Days Present: {data['days_present']}\n"
            summary += f"  Total Hours: {data['total_hours']:.2f}\n"
        
        return summary
    
    # Other existing methods...
    def generate_student_report(self, student_id):
        """Generate comprehensive student report"""
        student = self.data_handler.get_student_full_info(student_id)
        if not student:
            return None, "Student not found"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"student_report_{student['name'].replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Student Report: {student['name']}", 0, 1, 'C')
        pdf.ln(5)
        
        # Student Information
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Personal Information", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        info_lines = [
            f"Student ID: {student['id']}",
            f"Class: {student['class']}",
            f"Date of Birth: {student.get('dob', 'N/A')}",
            f"Age: {student.get('age', 'N/A')}",
            f"Address: {student.get('address', 'N/A')}",
            f"Health Status: {student.get('health_status', 'N/A')}",
            f"Allergies: {student.get('allergies', 'None')}",
            f"Enrollment Date: {student.get('enrollment_date', 'N/A')}"
        ]
        
        for line in info_lines:
            pdf.cell(0, 6, line, 0, 1)
        pdf.ln(5)
        
        # Parent Information
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Parent/Guardian Information", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        parent_lines = [
            f"Parent Contact: {student.get('parent_contact', 'N/A')}",
            f"Parent Email: {student.get('parent_email', 'N/A')}",
            f"Emergency Contact: {student.get('emergency_contact', 'N/A')}"
        ]
        
        for line in parent_lines:
            pdf.cell(0, 6, line, 0, 1)
        pdf.ln(5)
        
        # Attendance Summary
        attendance = student.get('attendance_record', {})
        total = sum(attendance.values())
        if total > 0:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Attendance Summary", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            pdf.cell(0, 6, f"Total Days: {total}", 0, 1)
            pdf.cell(0, 6, f"Present: {attendance.get('present', 0)} ({attendance.get('present', 0)/total*100:.1f}%)", 0, 1)
            pdf.cell(0, 6, f"Absent: {attendance.get('absent', 0)} ({attendance.get('absent', 0)/total*100:.1f}%)", 0, 1)
            pdf.cell(0, 6, f"Late: {attendance.get('late', 0)} ({attendance.get('late', 0)/total*100:.1f}%)", 0, 1)
            pdf.ln(5)
        
        # Academic Results
        results = student.get('academic_results', {})
        if results:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Academic Results", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            for term, subjects in results.items():
                if subjects:
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 8, f"{term}:", 0, 1)
                    pdf.set_font("Arial", '', 9)
                    
                    for subject, score in subjects.items():
                        pdf.cell(0, 6, f"  {subject}: {score}/100", 0, 1)
                    pdf.ln(2)
        
        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        
        pdf.output(filepath)
        return filepath, f"Student report generated: {filename}"
    
    def generate_class_report(self, class_name):
        """Generate report for entire class"""
        students = self.data_handler.get_students_by_class(class_name)
        if not students:
            return None, "No students in this class"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"class_report_{class_name.replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Class Report: {class_name}", 0, 1, 'C')
        pdf.ln(5)
        
        # Class Statistics
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Class Statistics", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        total_students = len(students)
        pdf.cell(0, 6, f"Total Students: {total_students}", 0, 1)
        
        # Age distribution
        ages = [s.get('age', 0) for s in students if s.get('age')]
        if ages:
            avg_age = sum(ages) / len(ages)
            pdf.cell(0, 6, f"Average Age: {avg_age:.1f} years", 0, 1)
            pdf.cell(0, 6, f"Age Range: {min(ages)} - {max(ages)} years", 0, 1)
        
        # Health status summary
        health_counts = {}
        for student in students:
            status = student.get('health_status', 'Unknown')
            health_counts[status] = health_counts.get(status, 0) + 1
        
        pdf.ln(3)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, "Health Status Distribution:", 0, 1)
        pdf.set_font("Arial", '', 9)
        
        for status, count in health_counts.items():
            percentage = (count / total_students) * 100
            pdf.cell(0, 6, f"  {status}: {count} students ({percentage:.1f}%)", 0, 1)
        
        pdf.ln(5)
        
        # Student List
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Student List", 0, 1)
        
        # Table header
        pdf.set_font("Arial", 'B', 10)
        col_widths = [15, 50, 20, 25, 30]
        headers = ["ID", "Name", "Age", "Health", "Parent Contact"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
        pdf.ln()
        
        # Student data
        pdf.set_font("Arial", '', 9)
        for student in students:
            pdf.cell(col_widths[0], 8, str(student.get('id', '')), 1, 0, 'C')
            
            name = student.get('name', '')
            if len(name) > 20:
                name = name[:17] + "..."
            pdf.cell(col_widths[1], 8, name, 1, 0, 'L')
            
            pdf.cell(col_widths[2], 8, str(student.get('age', '')), 1, 0, 'C')
            
            health = student.get('health_status', '')
            if len(health) > 10:
                health = health[:7] + "..."
            pdf.cell(col_widths[3], 8, health, 1, 0, 'C')
            
            contact = student.get('parent_contact', '')
            if len(contact) > 15:
                contact = contact[:12] + "..."
            pdf.cell(col_widths[4], 8, contact, 1, 0, 'L')
            pdf.ln()
        
        # Academic Performance Summary (if available)
        has_results = any('academic_results' in s and s['academic_results'] for s in students)
        if has_results:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Academic Performance Summary", 0, 1)
            
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, "Detailed academic analysis would require individual student reports.", 0, 1)
        
        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        
        pdf.output(filepath)
        return filepath, f"Class report generated: {filename}"
    
    # NEW: Wrapper used by GUI when user asks to generate an employee report (period specified)
    def generate_employee_report(self, employee_id, start_date, end_date):
        """
        Generate an Excel attendance report for an employee in a date range.
        Returns (filepath, message) or (None, error_message)
        """
        # Validate dates
        try:
            # ensure start_date <= end_date
            if start_date > end_date:
                return None, "Start date must be before or equal to end date"
        except:
            return None, "Invalid date format"
        
        return self.generate_employee_attendance_excel(employee_id, start_date, end_date)