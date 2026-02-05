# admin_manager.py - ENHANCED VERSION
from datetime import datetime, timedelta
import pandas as pd
import os

class AdminManager:
    def __init__(self, data_handler, student_manager):
        self.data_handler = data_handler
        self.student_manager = student_manager

    # Get system stats
    def get_system_stats(self):
        """Get comprehensive system statistics for dashboard"""
        today = datetime.now().date().isoformat()
        attendance = self.data_handler.get_attendance_by_date(today)
        present_today = len([r for r in attendance if r.get('status') == 'Present'])
        late_today = len([r for r in attendance if r.get('status') == 'Late'])
        total_employees = len(self.data_handler.get_all_employees())
        total_students = len(self.data_handler.get_all_students())
        classes = self.data_handler.get_all_classes()
        class_counts = {}
        for class_name in classes:
            students = self.data_handler.get_students_by_class(class_name)
            class_counts[class_name] = len(students)
        return {
            'total_employees': total_employees,
            'total_students': total_students,
            'present_today': present_today,
            'late_today': late_today,
            'class_counts': class_counts,
            'total_classes': len(classes)
        }

    # Working hours management
    def set_standard_working_hours(self, daily_hours=8, weekly_hours=40, overtime_rate=1.5):
        success = self.data_handler.set_working_hours(daily_hours, weekly_hours, overtime_rate)
        if success:
            return True, f"Standard working hours set to {daily_hours} hours/day, {weekly_hours} hours/week"
        return False, "Failed to set working hours"

    def set_employee_working_hours(self, employee_id, daily_hours=None, weekly_hours=None):
        success = self.data_handler.set_employee_working_hours(employee_id, daily_hours, weekly_hours)
        if success:
            message = "Employee working hours updated"
            if daily_hours:
                message += f" - Daily: {daily_hours} hours"
            if weekly_hours:
                message += f" - Weekly: {weekly_hours} hours"
            return True, message
        return False, "Failed to update employee working hours"

    def get_employee_working_hours_report(self, employee_id, start_date, end_date):
        hours_analysis = self.data_handler.calculate_overtime(employee_id, start_date, end_date)
        return hours_analysis

    # Announcement management
    def create_announcement(self, title, content, author, author_id, priority="Medium", visible_to=None, attachments=None):
        if not title or not content:
            return False, "Title and content are required"
        success = self.data_handler.add_announcement(
            title=title,
            content=content,
            author=author,
            author_id=author_id,
            priority=priority,
            visible_to=visible_to
        )
        if success:
            return True, "Announcement created successfully"
        return False, "Failed to create announcement"

    def get_all_announcements(self):
        return self.data_handler.get_announcements()

    def delete_announcement(self, announcement_id):
        data = self.data_handler.load_json(self.data_handler.dashboard_file)
        announcements = data.get("announcements", [])
        announcements = [ann for ann in announcements if ann.get("id") != announcement_id]
        data["announcements"] = announcements
        success = self.data_handler.save_json(self.data_handler.dashboard_file, data)
        if success:
            return True, "Announcement deleted successfully"
        return False, "Failed to delete announcement"

    # Export students to Excel
    def export_students_to_excel(self, class_filter=None, include_photos=False):
        df = self.data_handler.export_students_to_excel(class_filter)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if class_filter:
            filename = f"students_{class_filter.replace(' ', '_')}_{timestamp}.xlsx"
        else:
            filename = f"all_students_{timestamp}.xlsx"
        filepath = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Students', index=False)
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
            return True, f"Excel report generated: {filename}", filepath
        except Exception as e:
            return False, f"Failed to generate Excel report: {str(e)}", None

    def get_students_grouped_by_class(self):
        return self.data_handler.get_students_grouped_by_class()

    # Add/update employee
    def add_employee_with_details(self, name, department, role, email, phone, address, password="default123", assigned_grades=None, daily_hours=8, weekly_hours=40):
        if not name or not department:
            return False, "Name and department are required"
        employees = self.data_handler.get_all_employees()
        if any(emp['name'].lower() == name.lower() for emp in employees):
            return False, "Employee with this name already exists"
        success = self.data_handler.add_employee(name, department)
        if not success:
            return False, "Failed to add employee"
        employees = self.data_handler.get_all_employees()
        new_employee = next((emp for emp in employees if emp['name'] == name), None)
        if new_employee:
            updates = {
                "role": role,
                "email": email,
                "phone": phone,
                "address": address,
                "password": self.data_handler.hash_password(password),
                "assigned_grades": assigned_grades or [],
                "working_hours": {"daily": daily_hours, "weekly": weekly_hours}
            }
            success = self.data_handler.update_employee(new_employee['id'], **updates)
            if success:
                self.set_employee_working_hours(new_employee['id'], daily_hours, weekly_hours)
                return True, f"Employee '{name}' added successfully with all details"
        return False, "Failed to add employee details"

    def update_employee_details(self, employee_id, **updates):
        success = self.data_handler.update_employee(employee_id, **updates)
        if success:
            return True, "Employee details updated successfully"
        return False, "Failed to update employee"

    def assign_grade_to_employee(self, employee_id, grade):
        if not grade:
            return False, "Grade is required"
        success = self.data_handler.assign_employee_grade(employee_id, grade)
        if success:
            return True, f"Grade {grade} assigned to employee"
        return False, "Failed to assign grade"

    def remove_grade_from_employee(self, employee_id, grade):
        success = self.data_handler.remove_employee_grade(employee_id, grade)
        if success:
            return True, f"Grade {grade} removed from employee"
        return False, "Failed to remove grade assignment"

    def get_employee_full_info(self, employee_id):
        employees = self.data_handler.get_all_employees()
        employee = next((emp for emp in employees if emp.get('id') == employee_id), None)
        if employee:
            employee["photo_path"] = self.data_handler.get_employee_photo(employee_id)
            hours_settings = self.data_handler.get_working_hours_settings()
            employee_settings = hours_settings.get("employee_settings", {}).get(str(employee_id), {})
            employee["custom_working_hours"] = employee_settings
            return employee
        return None

    def reset_employee_password(self, employee_id, new_password):
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        updates = {"password": self.data_handler.hash_password(new_password)}
        success = self.data_handler.update_employee(employee_id, **updates)
        if success:
            return True, "Employee password reset successfully"
        return False, "Failed to reset password"

    def get_employee_statistics(self):
        employees = self.data_handler.get_all_employees()
        stats = {
            "total_employees": len(employees),
            "by_department": {},
            "with_grade_assignments": 0,
            "teaching_staff": 0,
            "working_hours_summary": {
                "total_daily_hours": 0,
                "total_weekly_hours": 0,
                "average_daily_hours": 0
            }
        }
        total_daily = 0
        total_weekly = 0
        for emp in employees:
            dept = emp.get("department", "Unknown")
            stats["by_department"][dept] = stats["by_department"].get(dept, 0) + 1
            if dept == "Teaching":
                stats["teaching_staff"] += 1
            if emp.get("assigned_grades"):
                stats["with_grade_assignments"] += 1
            working_hours = emp.get("working_hours", {"daily": 8, "weekly": 40})
            total_daily += working_hours.get("daily", 8)
            total_weekly += working_hours.get("weekly", 40)
        if employees:
            stats["working_hours_summary"]["average_daily_hours"] = total_daily / len(employees)
            stats["working_hours_summary"]["average_weekly_hours"] = total_weekly / len(employees)
        return stats

    def validate_grade_assignment(self, employee_id, grade):
        employee = self.get_employee_full_info(employee_id)
        if not employee:
            return False, "Employee not found"
        if employee.get("department") != "Teaching":
            return False, "Only teaching staff can be assigned grades"
        if grade in employee.get("assigned_grades", []):
            return False, f"Employee already assigned to {grade}"
        return True, "Valid assignment"

    def get_unread_announcements_count(self, employee_id, employee_department="All"):
        announcements = self.data_handler.get_announcements_for_employee(employee_id, employee_department)
        unread_count = 0
        for ann in announcements:
            read_by = ann.get("read_by", [])
            if employee_id not in read_by:
                unread_count += 1
        return unread_count