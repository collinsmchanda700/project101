# data_handler.py - updated with term attendance and base64 photo saving
import json
import os
import shutil
from datetime import datetime, date, timedelta
import hashlib
import base64
import io
import pandas as pd
import calendar

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow (PIL) not installed. Photo features will be disabled.")

class DataHandler:
    def __init__(self):
        self.data_dir = "data"
        self.employees_file = os.path.join(self.data_dir, "employees.json")
        self.database_file = os.path.join(self.data_dir, "database.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.students_file = os.path.join(self.data_dir, "students.json")
        self.correction_requests_file = os.path.join(self.data_dir, "correction_requests.json")
        self.dashboard_file = os.path.join(self.data_dir, "dashboard.json")
        self.working_hours_file = os.path.join(self.data_dir, "working_hours.json")
        self.photos_dir = os.path.join(self.data_dir, "photos")

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(self.photos_dir):
            os.makedirs(self.photos_dir)

        self.initialize_files()

    def initialize_files(self):
        # -- employees.json
        if not os.path.exists(self.employees_file):
            default_employees = {
                "departments": ["Teaching", "Administration", "Support Staff", "Management", "Library"],
                "employees": [
                    {
                        "id": 1,
                        "name": "John Smith",
                        "department": "Teaching",
                        "assigned_grades": ["Grade 10", "Grade 11"],
                        "role": "Math Teacher",
                        "password": self.hash_password("teacher123"),
                        "email": "john.smith@school.edu",
                        "phone": "555-0101",
                        "address": "123 Main St",
                        "working_hours": {"daily": 8, "weekly": 40}
                    },
                    {
                        "id": 2,
                        "name": "Jane Doe",
                        "department": "Teaching",
                        "assigned_grades": ["Grade 9", "Grade 12"],
                        "role": "Science Teacher",
                        "password": self.hash_password("teacher123"),
                        "email": "jane.doe@school.edu",
                        "phone": "555-0102",
                        "address": "456 Oak Ave",
                        "working_hours": {"daily": 8, "weekly": 40}
                    },
                    {
                        "id": 3,
                        "name": "Bob Johnson",
                        "department": "Administration",
                        "assigned_grades": [],
                        "role": "Registrar",
                        "password": self.hash_password("admin123"),
                        "email": "bob.johnson@school.edu",
                        "phone": "555-0103",
                        "address": "789 Pine Rd",
                        "working_hours": {"daily": 8, "weekly": 40}
                    }
                ]
            }
            self.save_json(self.employees_file, default_employees)

        # -- database.json
        if not os.path.exists(self.database_file):
            default_database = {"attendance": []}
            self.save_json(self.database_file, default_database)

        # -- settings.json
        if not os.path.exists(self.settings_file):
            default_password = self.hash_password("admin123")
            default_settings = {
                "admin_password": default_password,
                "auto_backup": True,
                "backup_days": 7,
                "school_name": "Greenwood High School",
                "school_year": "2024-2025",
                "terms": ["Term 1", "Term 2", "Term 3"],
                "subjects": ["Math", "Science", "English", "History", "Geography", "Art", "Music", "PE"],
                "standard_working_hours": {"daily": 8, "weekly": 40, "overtime_rate": 1.5},
                "term_days_default": 60,  # default number of days in a term (Mon-Fri count approx)
                "term_days": {}  # optional explicit per-term mapping
            }
            self.save_json(self.settings_file, default_settings)

        # -- students.json
        if not os.path.exists(self.students_file):
            default_students = {
                "classes": ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
                           "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"],
                "students": [
                    {
                        "id": 1,
                        "name": "Michael Chen",
                        "class": "Grade 10",
                        "parent_contact": "555-0101",
                        "parent_email": "parent.chen@email.com",
                        "dob": "2008-05-15",
                        "age": self.calculate_age("2008-05-15"),
                        "address": "123 Student St, City",
                        "health_status": "Good",
                        "allergies": "None",
                        "emergency_contact": "555-9999",
                        "enrollment_date": date.today().isoformat(),
                        "photo": None,
                        "academic_results": {"Term 1": {}, "Term 2": {}, "Term 3": {}},
                        "attendance_record": {"present": 0, "absent": 0, "late": 0},
                        "monthly_attendance": {},
                        "term_attendance": {}
                    }
                ]
            }
            self.save_json(self.students_file, default_students)

        # -- correction_requests.json
        if not os.path.exists(self.correction_requests_file):
            default_requests = {"requests": []}
            self.save_json(self.correction_requests_file, default_requests)

        # -- dashboard.json
        if not os.path.exists(self.dashboard_file):
            default_dashboard = {
                "announcements": [
                    {
                        "id": 1,
                        "title": "Welcome to New School Year",
                        "content": "Welcome all staff and students to the 2024-2025 academic year!",
                        "author": "Admin",
                        "author_id": 0,
                        "date": datetime.now().isoformat(),
                        "priority": "High",
                        "visible_to": ["All"],
                        "attachments": [],
                        "read_by": []
                    }
                ],
                "events": []
            }
            self.save_json(self.dashboard_file, default_dashboard)

        # -- working_hours.json
        if not os.path.exists(self.working_hours_file):
            default_hours = {
                "standard_daily_hours": 8,
                "standard_weekly_hours": 40,
                "overtime_rate": 1.5,
                "employee_settings": {}
            }
            self.save_json(self.working_hours_file, default_hours)

    # Basic JSON helpers
    def load_json(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # return sensible default based on file
            if "employees" in filepath:
                return {"departments": [], "employees": []}
            if "students" in filepath:
                return {"classes": [], "students": []}
            if "database" in filepath:
                return {"attendance": []}
            if "settings" in filepath:
                return {}
            if "dashboard" in filepath:
                return {"announcements": [], "events": []}
            if "working_hours" in filepath:
                return {"standard_daily_hours": 8, "standard_weekly_hours": 40, "overtime_rate": 1.5, "employee_settings": {}}
            return {}

    def save_json(self, filepath, data):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
            return False

    # Password hashing
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def calculate_age(self, dob):
        try:
            birth = datetime.strptime(dob, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 0

    # Working hours (existing functions kept)
    def set_working_hours(self, daily_hours=8, weekly_hours=40, overtime_rate=1.5):
        data = self.load_json(self.working_hours_file)
        data.update({"standard_daily_hours": daily_hours, "standard_weekly_hours": weekly_hours, "overtime_rate": overtime_rate})
        return self.save_json(self.working_hours_file, data)

    def get_working_hours_settings(self):
        return self.load_json(self.working_hours_file)

    def set_employee_working_hours(self, employee_id, daily_hours=None, weekly_hours=None):
        data = self.load_json(self.working_hours_file)
        if "employee_settings" not in data:
            data["employee_settings"] = {}
        if str(employee_id) not in data["employee_settings"]:
            data["employee_settings"][str(employee_id)] = {}
        if daily_hours is not None:
            data["employee_settings"][str(employee_id)]["daily"] = daily_hours
        if weekly_hours is not None:
            data["employee_settings"][str(employee_id)]["weekly"] = weekly_hours
        return self.save_json(self.working_hours_file, data)

    def calculate_overtime(self, employee_id, date_range_start, date_range_end):
        attendance_records = self.get_employee_attendance(employee_id, date_range_start, date_range_end)
        hours_settings = self.get_working_hours_settings()
        employee_settings = hours_settings.get("employee_settings", {}).get(str(employee_id), {})
        daily_hours = employee_settings.get("daily", hours_settings.get("standard_daily_hours", 8))
        overtime_rate = hours_settings.get("overtime_rate", 1.5)
        total_hours = 0.0
        overtime_hours = 0.0
        overtime_pay = 0.0
        for record in attendance_records:
            if record.get('check_in') and record.get('check_out'):
                try:
                    ci = datetime.strptime(record['check_in'], "%H:%M:%S")
                    co = datetime.strptime(record['check_out'], "%H:%M:%S")
                    hours = (co - ci).seconds / 3600.0
                    total_hours += hours
                    if hours > daily_hours:
                        ot = hours - daily_hours
                        overtime_hours += ot
                        overtime_pay += ot * overtime_rate
                except:
                    pass
        return {"total_hours": round(total_hours, 2), "overtime_hours": round(overtime_hours, 2), "overtime_pay": round(overtime_pay, 2), "regular_hours": round(total_hours - overtime_hours, 2)}

    # Announcement methods omitted for brevity (kept as before)
    def add_announcement(self, title, content, author, author_id, priority="Medium", visible_to=None):
        data = self.load_json(self.dashboard_file)
        announcements = data.get("announcements", [])
        new_id = max([ann.get("id", 0) for ann in announcements], default=0) + 1
        announcement = {"id": new_id, "title": title, "content": content, "author": author, "author_id": author_id, "date": datetime.now().isoformat(), "priority": priority, "visible_to": visible_to if visible_to else ["All"], "attachments": [], "read_by": []}
        announcements.append(announcement)
        data["announcements"] = announcements
        return self.save_json(self.dashboard_file, data)

    def get_announcements_for_employee(self, employee_id, employee_department="All"):
        data = self.load_json(self.dashboard_file)
        announcements = data.get("announcements", [])
        visible_announcements = []
        for ann in announcements:
            visible_to = ann.get("visible_to", ["All"])
            if "All" in visible_to or employee_department in visible_to or str(employee_id) in [str(x) for x in visible_to]:
                visible_announcements.append(ann)
        visible_announcements.sort(key=lambda x: x.get("date", ""), reverse=True)
        return visible_announcements

    def mark_announcement_as_read(self, announcement_id, employee_id):
        data = self.load_json(self.dashboard_file)
        announcements = data.get("announcements", [])
        for ann in announcements:
            if ann.get("id") == announcement_id:
                if "read_by" not in ann:
                    ann["read_by"] = []
                if employee_id not in ann["read_by"]:
                    ann["read_by"].append(employee_id)
                break
        data["announcements"] = announcements
        return self.save_json(self.dashboard_file, data)

    def get_announcements(self, limit=None):
        data = self.load_json(self.dashboard_file)
        announcements = data.get("announcements", [])
        announcements.sort(key=lambda x: x.get("date", ""), reverse=True)
        if limit:
            return announcements[:limit]
        return announcements

    # Export students to DataFrame (used by admin manager/report generator)
    def export_students_to_excel(self, class_filter=None):
        students = self.get_all_students()
        if class_filter:
            students = [s for s in students if s.get('class') == class_filter]
        data = []
        for i, student in enumerate(students, 1):
            data.append({
                "No.": i,
                "Student ID": student.get('id', ''),
                "Full Name": student.get('name', ''),
                "Class": student.get('class', ''),
                "Age": student.get('age', ''),
                "Date of Birth": student.get('dob', ''),
                "Parent Contact": student.get('parent_contact', ''),
                "Parent Email": student.get('parent_email', ''),
                "Health Status": student.get('health_status', ''),
                "Allergies": student.get('allergies', ''),
                "Address": student.get('address', ''),
                "Emergency Contact": student.get('emergency_contact', ''),
                "Enrollment Date": student.get('enrollment_date', '')
            })
        return pd.DataFrame(data)

    def get_students_grouped_by_class(self):
        students = self.get_all_students()
        classes = self.get_all_classes()
        grouped = {}
        for class_name in classes:
            class_students = [s for s in students if s.get('class') == class_name]
            if class_students:
                class_students.sort(key=lambda x: x.get('name', ''))
                grouped[class_name] = class_students
        return grouped

    # Employee methods
    def get_all_employees(self):
        data = self.load_json(self.employees_file)
        return data.get("employees", [])

    def get_employees_by_department(self, department):
        data = self.load_json(self.employees_file)
        return [emp for emp in data.get("employees", []) if emp.get("department") == department]

    def get_all_departments(self):
        data = self.load_json(self.employees_file)
        return data.get("departments", [])

    def add_employee(self, name, department):
        data = self.load_json(self.employees_file)
        employees = data.get("employees", [])
        new_id = max([emp.get("id", 0) for emp in employees], default=0) + 1
        employees.append({"id": new_id, "name": name, "department": department, "role": "", "email": "", "phone": "", "address": "", "password": self.hash_password("default123"), "assigned_grades": [], "photo": None, "working_hours": {"daily": 8, "weekly": 40}})
        data["employees"] = employees
        return self.save_json(self.employees_file, data)

    def update_employee(self, employee_id, **updates):
        data = self.load_json(self.employees_file)
        for employee in data.get("employees", []):
            if employee.get("id") == employee_id:
                employee.update(updates)
                break
        return self.save_json(self.employees_file, data)

    def remove_employee(self, employee_id):
        data = self.load_json(self.employees_file)
        employees = [emp for emp in data.get("employees", []) if emp.get("id") != employee_id]
        data["employees"] = employees
        return self.save_json(self.employees_file, data)

    # Password methods
    def verify_employee_password(self, employee_id, password):
        employees = self.get_all_employees()
        employee = next((emp for emp in employees if emp.get('id') == employee_id), None)
        if not employee:
            return False
        return self.hash_password(password) == employee.get("password", "")

    def change_employee_password(self, employee_id, old_password, new_password):
        if self.verify_employee_password(employee_id, old_password):
            return self.update_employee(employee_id, password=self.hash_password(new_password))
        return False

    def verify_password(self, password):
        settings = self.load_json(self.settings_file)
        return self.hash_password(password) == settings.get("admin_password", "")

    def change_password(self, old_password, new_password):
        if self.verify_password(old_password):
            settings = self.load_json(self.settings_file)
            settings["admin_password"] = self.hash_password(new_password)
            return self.save_json(self.settings_file, settings)
        return False

    # Student methods
    def get_all_students(self):
        data = self.load_json(self.students_file)
        return data.get("students", [])

    def get_students_by_class(self, class_name):
        data = self.load_json(self.students_file)
        return [s for s in data.get("students", []) if s.get("class") == class_name]

    def get_all_classes(self):
        data = self.load_json(self.students_file)
        return data.get("classes", [])

    def add_student(self, name, class_name, parent_contact="", parent_email="", dob="", age=0, address="", health_status="Good", allergies="", emergency_contact=""):
        data = self.load_json(self.students_file)
        students = data.get("students", [])
        if class_name and class_name not in data.get("classes", []):
            data["classes"].append(class_name)
        new_id = max([s.get("id", 0) for s in students], default=0) + 1
        student = {"id": new_id, "name": name, "class": class_name, "parent_contact": parent_contact, "parent_email": parent_email, "dob": dob, "age": age, "address": address, "health_status": health_status, "allergies": allergies, "emergency_contact": emergency_contact, "enrollment_date": date.today().isoformat(), "photo": None, "academic_results": {"Term 1": {}, "Term 2": {}, "Term 3": {}}, "attendance_record": {"present": 0, "absent": 0, "late": 0}, "monthly_attendance": {}, "term_attendance": {}}
        students.append(student)
        data["students"] = students
        return self.save_json(self.students_file, data)

    def update_student(self, student_id, **updates):
        data = self.load_json(self.students_file)
        for student in data.get("students", []):
            if student.get("id") == student_id:
                student.update(updates)
                break
        return self.save_json(self.students_file, data)

    def remove_student(self, student_id):
        data = self.load_json(self.students_file)
        students = [s for s in data.get("students", []) if s.get("id") != student_id]
        data["students"] = students
        return self.save_json(self.students_file, data)

    # Attendance methods (employee)
    def record_check_in(self, employee_id, employee_name, department):
        now = datetime.now()
        today = date.today().isoformat()
        current_time = now.strftime("%H:%M:%S")
        rec = {"employee_id": employee_id, "employee_name": employee_name, "department": department, "date": today, "check_in": current_time, "check_out": None, "status": "Present", "timestamp": now.isoformat()}
        data = self.load_json(self.database_file)
        data.setdefault("attendance", []).append(rec)
        return self.save_json(self.database_file, data)

    def record_check_out(self, employee_id):
        today = date.today().isoformat()
        current_time = datetime.now().strftime("%H:%M:%S")
        data = self.load_json(self.database_file)
        for record in reversed(data.get("attendance", [])):
            if record.get("employee_id") == employee_id and record.get("date") == today and record.get("check_out") is None:
                record["check_out"] = current_time
                break
        return self.save_json(self.database_file, data)

    def get_today_attendance(self):
        today = date.today().isoformat()
        data = self.load_json(self.database_file)
        return [r for r in data.get("attendance", []) if r.get("date") == today]

    def get_attendance_by_date(self, target_date):
        data = self.load_json(self.database_file)
        return [r for r in data.get("attendance", []) if r.get("date") == target_date]

    def get_attendance_by_range(self, start_date, end_date):
        data = self.load_json(self.database_file)
        result = []
        for record in data.get("attendance", []):
            record_date = record.get("date")
            if start_date <= record_date <= end_date:
                result.append(record)
        return result

    def get_employee_attendance(self, employee_id, start_date=None, end_date=None):
        data = self.load_json(self.database_file)
        result = []
        for record in data.get("attendance", []):
            if record.get("employee_id") == employee_id:
                if start_date and end_date:
                    rdate = record.get("date")
                    if start_date <= rdate <= end_date:
                        result.append(record)
                else:
                    result.append(record)
        return result

    def has_checked_in_today(self, employee_id):
        today = date.today().isoformat()
        data = self.load_json(self.database_file)
        for record in data.get("attendance", []):
            if record.get("employee_id") == employee_id and record.get("date") == today and record.get("check_out") is None:
                return True
        return False

    # Photo helpers
    def save_student_photo_from_base64(self, student_id, image_base64):
        """Save base64 image for student and update student.photo with filename"""
        if not image_base64:
            return None
        try:
            header, _, b64 = image_base64.partition(',')
            # Some browsers include "data:image/png;base64,..." header; remove if present
            if b64 == "":
                b64 = header  # no header
            data = base64.b64decode(b64)
            # Use safe filename
            filename = f"student_{student_id}.jpg"
            save_path = os.path.join(self.photos_dir, filename)
            with open(save_path, "wb") as f:
                f.write(data)
            # Optionally resize using PIL
            if PIL_AVAILABLE:
                try:
                    img = Image.open(save_path)
                    img.thumbnail((300, 300))
                    img.save(save_path, "JPEG")
                except Exception:
                    pass
            # Update student record
            self.update_student(student_id, photo=filename)
            return filename
        except Exception as e:
            print(f"Error saving base64 photo: {e}")
            return None

    def save_employee_photo(self, employee_id, photo_path):
        """Save employee photo from path (if PIL available)"""
        if not PIL_AVAILABLE:
            print("PIL not available")
            return False
        try:
            if os.path.exists(photo_path):
                filename = f"employee_{employee_id}.jpg"
                save_path = os.path.join(self.photos_dir, filename)
                img = Image.open(photo_path)
                img.thumbnail((150, 150))
                img.save(save_path, "JPEG")
                return self.update_employee(employee_id, photo=filename)
        except Exception as e:
            print(f"Error saving employee photo: {e}")
        return False

    def get_employee_photo(self, employee_id):
        employees = self.get_all_employees()
        employee = next((e for e in employees if e.get("id") == employee_id), None)
        if employee and employee.get("photo"):
            path = os.path.join(self.photos_dir, employee["photo"])
            if os.path.exists(path):
                return path
        return None

    def get_student_photo(self, student_id):
        students = self.get_all_students()
        student = next((s for s in students if s.get("id") == student_id), None)
        if student and student.get("photo"):
            path = os.path.join(self.photos_dir, student["photo"])
            if os.path.exists(path):
                return path
        return None

    # Update student results
    def update_student_results(self, student_id, term, subject, score):
        data = self.load_json(self.students_file)
        for s in data.get("students", []):
            if s.get("id") == student_id:
                if "academic_results" not in s:
                    s["academic_results"] = {}
                if term not in s["academic_results"]:
                    s["academic_results"][term] = {}
                s["academic_results"][term][subject] = score
                break
        return self.save_json(self.students_file, data)

    def get_student_results(self, student_id):
        students = self.get_all_students()
        student = next((s for s in students if s.get("id") == student_id), None)
        if student:
            return student.get("academic_results", {})
        return {}

    # Student attendance update (single day marking)
    def update_student_attendance(self, student_id, status="present"):
        data = self.load_json(self.students_file)
        for s in data.get("students", []):
            if s.get("id") == student_id:
                if "attendance_record" not in s:
                    s["attendance_record"] = {"present": 0, "absent": 0, "late": 0}
                if status == "present":
                    s["attendance_record"]["present"] += 1
                elif status == "absent":
                    s["attendance_record"]["absent"] += 1
                elif status == "late":
                    s["attendance_record"]["late"] += 1
                break
        return self.save_json(self.students_file, data)

    # MONTHLY attendance preserved for backwards compatibility (kept)
    def save_student_monthly_attendance(self, student_id, month_key, present_dates):
        # existing monthly attendance logic (kept simple)
        data = self.load_json(self.students_file)
        updated = False
        try:
            year, month = [int(x) for x in month_key.split('-')]
            num_days = calendar.monthrange(year, month)[1]
        except:
            return False
        normalized = []
        for d in present_dates:
            try:
                if isinstance(d, int):
                    day = d
                else:
                    day = int(str(d).split('-')[-1])
                if 1 <= day <= num_days:
                    normalized.append(date(year, month, day).isoformat())
            except:
                continue
        for s in data.get("students", []):
            if s.get("id") == student_id:
                if "monthly_attendance" not in s:
                    s["monthly_attendance"] = {}
                s["monthly_attendance"][month_key] = {"present_dates": normalized, "summary": {"present": len(normalized), "absent": num_days - len(normalized), "month_days": num_days}}
                # For simplicity, we do not try to reconcile attendance_record deltas here
                updated = True
                break
        if updated:
            data["students"] = data.get("students", [])
            return self.save_json(self.students_file, data)
        return False

    def get_student_monthly_attendance(self, student_id, month_key):
        students = self.get_all_students()
        student = next((s for s in students if s.get("id") == student_id), None)
        if not student:
            return {}
        return student.get("monthly_attendance", {}).get(month_key, {})

    # NEW: Term attendance (per-term summary)
    def save_student_term_attendance(self, student_id, term_key, present_days):
        """
        Save a student's term attendance summary.
        term_key: arbitrary string identifying term (e.g. "2024-Term1" or "Term 1 2024")
        present_days: integer number of days present in that term (teacher supplied)
        """
        data = self.load_json(self.students_file)
        settings = self.load_json(self.settings_file)
        default_term_days = settings.get("term_days_default", 60)
        term_days_map = settings.get("term_days", {})
        total_days = term_days_map.get(term_key, default_term_days)
        try:
            pdays = int(present_days)
            pdays = max(0, min(pdays, total_days))
        except:
            return False
        updated = False
        for s in data.get("students", []):
            if s.get("id") == student_id:
                if "term_attendance" not in s:
                    s["term_attendance"] = {}
                s["term_attendance"][term_key] = {"present": pdays, "absent": total_days - pdays, "total_days": total_days}
                # We don't automatically add to cumulative attendance_record to avoid double counting — term entries remain canonical
                updated = True
                break
        if updated:
            data["students"] = data.get("students", [])
            return self.save_json(self.students_file, data)
        return False

    # Grade/employee helpers (kept as before)
    def assign_employee_grade(self, employee_id, grade):
        data = self.load_json(self.employees_file)
        for emp in data.get("employees", []):
            if emp.get("id") == employee_id:
                if "assigned_grades" not in emp:
                    emp["assigned_grades"] = []
                if grade not in emp["assigned_grades"]:
                    emp["assigned_grades"].append(grade)
                break
        return self.save_json(self.employees_file, data)

    def remove_employee_grade(self, employee_id, grade):
        data = self.load_json(self.employees_file)
        for emp in data.get("employees", []):
            if emp.get("id") == employee_id:
                if "assigned_grades" in emp and grade in emp["assigned_grades"]:
                    emp["assigned_grades"].remove(grade)
                break
        return self.save_json(self.employees_file, data)

    def get_employee_assigned_grades(self, employee_id):
        emps = self.get_all_employees()
        emp = next((e for e in emps if e.get("id") == employee_id), None)
        if emp:
            return emp.get("assigned_grades", [])
        return []

    def get_employees_by_grade(self, grade):
        employees = self.get_all_employees()
        return [e for e in employees if grade in e.get("assigned_grades", [])]

    # Correction request flows
    def submit_correction_request(self, employee_id, employee_name, original_date, original_status, requested_correction, reason):
        data = self.load_json(self.correction_requests_file)
        new_id = max([req.get("id", 0) for req in data.get("requests", [])], default=0) + 1
        request = {"id": new_id, "employee_id": employee_id, "employee_name": employee_name, "original_date": original_date, "original_status": original_status, "requested_correction": requested_correction, "reason": reason, "status": "Pending", "submitted_date": datetime.now().isoformat(), "processed_by": None, "processed_date": None, "notes": ""}
        data.setdefault("requests", []).append(request)
        return self.save_json(self.correction_requests_file, data)

    def get_correction_requests(self, employee_id=None):
        data = self.load_json(self.correction_requests_file)
        reqs = data.get("requests", [])
        if employee_id:
            return [r for r in reqs if r.get("employee_id") == employee_id]
        return reqs

    def update_correction_request(self, request_id, status, processed_by, notes=""):
        data = self.load_json(self.correction_requests_file)
        for req in data.get("requests", []):
            if req.get("id") == request_id:
                req["status"] = status
                req["processed_by"] = processed_by
                req["processed_date"] = datetime.now().isoformat()
                req["notes"] = notes
                if status == "Approved":
                    self.apply_attendance_correction(req)
                break
        return self.save_json(self.correction_requests_file, data)

    def apply_attendance_correction(self, request):
        data = self.load_json(self.database_file)
        for rec in data.get("attendance", []):
            if rec.get("employee_id") == request.get("employee_id") and rec.get("date") == request.get("original_date"):
                if "status" in request["requested_correction"]:
                    rec["status"] = request["requested_correction"]["status"]
                if "check_in" in request["requested_correction"]:
                    rec["check_in"] = request["requested_correction"]["check_in"]
                if "check_out" in request["requested_correction"]:
                    rec["check_out"] = request["requested_correction"]["check_out"]
                rec["correction_applied"] = True
                rec["correction_date"] = datetime.now().isoformat()
                break
        return self.save_json(self.database_file, data)

    # Dashboard events
    def get_dashboard_data(self):
        return self.load_json(self.dashboard_file)

    def add_event(self, title, event_date, description=""):
        data = self.load_json(self.dashboard_file)
        events = data.get("events", [])
        events.append({"title": title, "date": event_date, "description": description})
        data["events"] = events
        return self.save_json(self.dashboard_file, data)

    # School info
    def get_school_info(self):
        settings = self.load_json(self.settings_file)
        return {"name": settings.get("school_name", "School"), "year": settings.get("school_year", ""), "total_employees": len(self.get_all_employees()), "total_students": len(self.get_all_students())}

    def get_available_subjects(self):
        settings = self.load_json(self.settings_file)
        return settings.get("subjects", [])

    def get_available_terms(self):
        settings = self.load_json(self.settings_file)
        return settings.get("terms", [])

    def create_backup(self):
        backup_dir = os.path.join(self.data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{ts}.json")
        data = self.load_json(self.database_file)
        return self.save_json(backup_file, data)

    def get_student_full_info(self, student_id):
        students = self.get_all_students()
        student = next((s for s in students if s.get("id") == student_id), None)
        if student:
            student["photo_path"] = self.get_student_photo(student_id)
            return student
        return None

    def get_employee_full_info(self, employee_id):
        employees = self.get_all_employees()
        emp = next((e for e in employees if e.get("id") == employee_id), None)
        if emp:
            emp["photo_path"] = self.get_employee_photo(employee_id)
            return emp
        return None