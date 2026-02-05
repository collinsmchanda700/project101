# student_manager.py - wrapper for student operations (includes term attendance wrapper)
from datetime import datetime
import os
import pandas as pd

class StudentManager:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def add_new_student(self, name, class_name, parent_contact="", parent_email="", dob="", address="", health_status="Good", allergies="", emergency_contact=""):
        if not name or not class_name:
            return False, "Name and class are required"
        students = self.data_handler.get_all_students()
        if any(student['name'].lower() == name.lower() and student['class'] == class_name for student in students):
            return False, "Student with this name already exists in this class"
        age = self.data_handler.calculate_age(dob) if dob else 0
        success = self.data_handler.add_student(name=name, class_name=class_name, parent_contact=parent_contact, parent_email=parent_email, dob=dob, age=age, address=address, health_status=health_status, allergies=allergies, emergency_contact=emergency_contact)
        if success:
            return True, f"Student '{name}' added to {class_name}"
        return False, "Failed to add student"

    def update_student_results(self, student_id, term, subject, score):
        if not 0 <= score <= 100:
            return False, "Score must be between 0 and 100"
        success = self.data_handler.update_student_results(student_id, term, subject, score)
        if success:
            return True, f"Updated {subject} result for Term {term}"
        return False, "Failed to update results"

    def get_student_full_info(self, student_id):
        students = self.data_handler.get_all_students()
        student = next((s for s in students if s['id'] == student_id), None)
        if not student:
            return None
        student["photo_path"] = self.data_handler.get_student_photo(student_id)
        return student

    def get_students_by_grade_teacher(self, grade, teacher_id):
        students = self.data_handler.get_students_by_class(grade)
        teacher_grades = self.data_handler.get_employee_assigned_grades(teacher_id)
        if grade not in teacher_grades:
            return []
        return students

    def record_student_attendance(self, student_id, status="present"):
        success = self.data_handler.update_student_attendance(student_id, status)
        if success:
            return True, f"Attendance recorded as {status}"
        return False, "Failed to record attendance"

    def get_student_attendance_summary(self, student_id):
        student = self.get_student_full_info(student_id)
        if not student:
            return "Student not found"
        attendance = student.get("attendance_record", {"present": 0, "absent": 0, "late": 0})
        total = sum(attendance.values())
        if total == 0:
            return "No attendance records"
        summary = f"Attendance Summary for {student['name']}:\n"
        summary += f"Present: {attendance['present']} ({attendance['present']/total*100:.1f}%)\n"
        summary += f"Absent: {attendance['absent']} ({attendance['absent']/total*100:.1f}%)\n"
        summary += f"Late: {attendance['late']} ({attendance['late']/total*100:.1f}%)\n"
        summary += f"Total Days: {total}"
        return summary

    def get_academic_summary(self, student_id):
        results = self.data_handler.get_student_results(student_id)
        if not results:
            return "No academic results available"
        summary = f"Academic Results:\n"
        for term, subjects in results.items():
            if subjects:
                summary += f"\n{term}:\n"
                for subject, score in subjects.items():
                    summary += f"  {subject}: {score}/100\n"
        return summary

    def export_student_results_to_excel(self, student_id):
        student = self.get_student_full_info(student_id)
        if not student:
            return None, "Student not found"
        results = student.get("academic_results", {})
        data = []
        for term, subjects in results.items():
            if subjects:
                for subject, score in subjects.items():
                    data.append({"Term": term, "Subject": subject, "Score": score, "Grade": self.get_grade_from_score(score), "Remarks": self.get_remarks_from_score(score)})
        if not data:
            return None, "No academic results available"
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{student['name'].replace(' ', '_')}_{timestamp}.xlsx"
        filepath = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
                info_data = {"Field": ["Student Name", "Student ID", "Class", "Date of Birth", "Age"], "Value": [student['name'], student['id'], student['class'], student.get('dob', 'N/A'), student.get('age', 'N/A')]}
                info_df = pd.DataFrame(info_data)
                info_df.to_excel(writer, sheet_name='Student Info', index=False)
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
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
            return filepath, f"Student results exported to Excel: {filename}"
        except Exception as e:
            return None, f"Failed to export results: {str(e)}"

    def get_grade_from_score(self, score):
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def get_remarks_from_score(self, score):
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Satisfactory"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Fail"

    def record_student_monthly_attendance(self, student_id, month_key, present_dates):
        try:
            success = self.data_handler.save_student_monthly_attendance(student_id, month_key, present_dates)
            if success:
                return True, "Monthly attendance saved"
            return False, "Failed to save monthly attendance"
        except Exception as e:
            return False, str(e)

    # Term attendance wrapper
    def record_student_term_attendance(self, student_id, term_key, present_days):
        try:
            success = self.data_handler.save_student_term_attendance(student_id, term_key, present_days)
            if success:
                return True, "Term attendance saved"
            return False, "Failed to save term attendance"
        except Exception as e:
            return False, str(e)