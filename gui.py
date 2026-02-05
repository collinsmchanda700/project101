# gui.py - COMPLETE WORKING VERSION WITH ALL FIXES (UPDATED)
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, date, timedelta
import os
from PIL import Image, ImageTk
import calendar
import webbrowser

class AttendanceGUI:
    def __init__(self, root, data_handler, report_generator, admin_manager, student_manager):
        self.root = root
        self.data_handler = data_handler
        self.report_generator = report_generator
        self.admin_manager = admin_manager
        self.student_manager = student_manager
        
        # Initialize variables
        self.current_employee = None
        self.current_grade = None
        self.admin_logged_in = False
        self.student_photo_path = None
        self.employee_photo_path = None
        
        # Set up main window
        self.root.title("School Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#f0f0f0')
        self.main_container.pack(fill='both', expand=True)
        
        # Create content frame
        self.content_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Show login screen immediately
        self.show_login_screen()
    
    def clear_content_frame(self):
        """Clear all widgets from content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Show login/selection screen"""
        self.clear_content_frame()
        
        # Center the login frame
        login_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            login_frame,
            text="School Attendance System",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 30))
        
        # Employee login button
        emp_login_btn = tk.Button(
            login_frame,
            text="Employee Login",
            font=('Arial', 14),
            bg='#3498db',
            fg='white',
            width=25,
            height=2,
            command=self.show_employee_login
        )
        emp_login_btn.pack(pady=10)
        
        # Admin login button
        admin_btn = tk.Button(
            login_frame,
            text="Admin Panel",
            font=('Arial', 14),
            bg='#e74c3c',
            fg='white',
            width=25,
            height=2,
            command=self.show_admin_login
        )
        admin_btn.pack(pady=10)
        
        # System status - FIXED: Use get_system_stats() which now exists
        try:
            stats = self.admin_manager.get_system_stats()
            status_text = f"Total Staff: {stats['total_employees']} | "
            status_text += f"Total Students: {stats['total_students']} | "
            status_text += f"Present Today: {stats['present_today']}"
        except Exception as e:
            status_text = f"System status: Initializing..."
        
        tk.Label(
            login_frame,
            text=status_text,
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#555'
        ).pack(pady=20)
    
    def show_admin_login(self):
        """Show admin login screen"""
        self.clear_content_frame()
        
        login_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            login_frame,
            text="Admin Login",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))
        
        tk.Label(login_frame, text="Password:", bg='#f0f0f0').pack(anchor='w')
        self.admin_pass_var = tk.StringVar()
        password_entry = tk.Entry(
            login_frame,
            textvariable=self.admin_pass_var,
            show='*',
            width=30
        )
        password_entry.pack(pady=5)
        
        def attempt_admin_login():
            password = self.admin_pass_var.get()
            if self.data_handler.verify_password(password):
                self.admin_logged_in = True
                self.show_admin_panel()
            else:
                messagebox.showerror("Login Failed", "Incorrect password")
        
        tk.Button(
            login_frame,
            text="Login",
            font=('Arial', 12),
            bg='#27ae60',
            fg='white',
            command=attempt_admin_login,
            width=15
        ).pack(pady=20)
        
        tk.Button(
            login_frame,
            text="Back",
            command=self.show_login_screen
        ).pack()
    
    def show_employee_login(self):
        """Show employee login screen"""
        self.clear_content_frame()
        
        login_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            login_frame,
            text="Employee Login",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))
        
        # Department selection
        tk.Label(login_frame, text="Select Department:", bg='#f0f0f0').pack(anchor='w')
        departments = self.data_handler.get_all_departments()
        self.login_dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(
            login_frame,
            textvariable=self.login_dept_var,
            values=departments,
            state='readonly',
            width=25
        )
        dept_combo.pack(pady=5)
        dept_combo.bind('<<ComboboxSelected>>', self.on_login_dept_selected)
        
        # Employee selection
        tk.Label(login_frame, text="Select Employee:", bg='#f0f0f0').pack(anchor='w', pady=(10, 0))
        self.login_emp_var = tk.StringVar()
        self.login_emp_combo = ttk.Combobox(
            login_frame,
            textvariable=self.login_emp_var,
            values=[],
            state='readonly',
            width=25
        )
        self.login_emp_combo.pack(pady=5)
        
        # Password entry
        tk.Label(login_frame, text="Password:", bg='#f0f0f0').pack(anchor='w', pady=(10, 0))
        self.login_password_var = tk.StringVar()
        password_entry = tk.Entry(
            login_frame,
            textvariable=self.login_password_var,
            show='*',
            width=27
        )
        password_entry.pack(pady=5)
        
        def attempt_employee_login():
            department = self.login_dept_var.get()
            employee_name = self.login_emp_var.get()
            password = self.login_password_var.get()
            
            if not department or not employee_name or not password:
                messagebox.showwarning("Input Required", "Please fill in all fields")
                return
            
            # Find employee
            employees = self.data_handler.get_employees_by_department(department)
            employee = next((emp for emp in employees if emp['name'] == employee_name), None)
            
            if not employee:
                messagebox.showerror("Login Failed", "Employee not found")
                return
            
            # Verify password
            if self.data_handler.verify_employee_password(employee['id'], password):
                self.current_employee = employee
                self.show_employee_dashboard()
            else:
                messagebox.showerror("Login Failed", "Incorrect password")
        
        tk.Button(
            login_frame,
            text="Login",
            font=('Arial', 12),
            bg='#27ae60',
            fg='white',
            command=attempt_employee_login,
            width=15
        ).pack(pady=20)
        
        tk.Button(
            login_frame,
            text="Back",
            command=self.show_login_screen
        ).pack()
    
    def on_login_dept_selected(self, event=None):
        """Update employee list when department is selected in login"""
        department = self.login_dept_var.get()
        if department:
            employees = self.data_handler.get_employees_by_department(department)
            employee_names = [emp['name'] for emp in employees]
            self.login_emp_combo['values'] = employee_names
            self.login_emp_var.set('')
    
    def show_employee_dashboard(self):
        """Show employee dashboard with announcements and options"""
        self.clear_content_frame()
        
        # Get school info
        school_info = self.data_handler.get_school_info()
        
        # Header with school info
        header_frame = tk.Frame(self.content_frame, bg='#2c3e50')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            header_frame,
            text=f"{school_info['name']} - Employee Portal",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(pady=10)
        
        tk.Label(
            header_frame,
            text=f"Welcome, {self.current_employee['name']} ({self.current_employee.get('role', 'Employee')})",
            font=('Arial', 12),
            fg='white',
            bg='#2c3e50'
        ).pack(pady=(0, 10))
        
        # Main container with two columns
        main_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left column - Quick Actions
        left_frame = tk.Frame(main_frame, bg='#f0f0f0')
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        
        tk.Label(
            left_frame,
            text="Quick Actions",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))
        
        # Action buttons - Different for teaching vs non-teaching
        if self.current_employee.get("department") == "Teaching":
            actions = [
                ("📅 Check-in/out", self.show_employee_screen),
                ("🏫 Manage Grades", self.show_teaching_grade_selection),
                ("📊 View My Attendance", self.show_my_attendance),
                ("📝 Request Correction", self.show_correction_request_form),
                ("📅 Record Monthly Student Attendance", self.show_record_monthly_attendance),
                ("⚙️ Settings", self.show_employee_settings),
                ("📢 View Announcements", self.show_all_announcements)
            ]
        else:
            actions = [
                ("📅 Check-in/out", self.show_employee_screen),
                ("📊 View My Attendance", self.show_my_attendance),
                ("📝 Request Correction", self.show_correction_request_form),
                ("⚙️ Settings", self.show_employee_settings),
                ("📢 View Announcements", self.show_all_announcements)
            ]
        
        for text, command in actions:
            btn = tk.Button(
                left_frame,
                text=text,
                font=('Arial', 12),
                bg='#3498db',
                fg='white',
                width=28,
                height=2,
                command=command
            )
            btn.pack(pady=5)
        
        # Right column - Recent Announcements
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', expand=True)
        
        tk.Label(
            right_frame,
            text="Recent Announcements",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 10))
        
        # Get announcements for this employee only
        announcements = self.data_handler.get_announcements_for_employee(
            self.current_employee['id'],
            self.current_employee.get('department', 'All')
        )[:3]
        
        if not announcements:
            tk.Label(
                right_frame,
                text="No recent announcements",
                font=('Arial', 12),
                bg='#f0f0f0'
            ).pack(pady=20)
        else:
            announcements_frame = tk.Frame(right_frame, bg='#f0f0f0')
            announcements_frame.pack(fill='both', expand=True)
            
            for ann in announcements:
                ann_frame = tk.Frame(announcements_frame, bg='white', relief='solid', borderwidth=1)
                ann_frame.pack(fill='x', pady=5, padx=5)
                
                tk.Label(
                    ann_frame,
                    text=f"📢 {ann['title'][:30]}",
                    font=('Arial', 10, 'bold'),
                    bg='white'
                ).pack(anchor='w', padx=10, pady=(5, 0))
                
                tk.Label(
                    ann_frame,
                    text=ann['content'][:80] + ("..." if len(ann['content'])>80 else ""),
                    font=('Arial', 9),
                    bg='white'
                ).pack(anchor='w', padx=10, pady=(0, 5))
                
                tk.Label(
                    ann_frame,
                    text=f"By: {ann['author']} | {ann['date'][:10]}",
                    font=('Arial', 8),
                    bg='white',
                    fg='#666'
                ).pack(anchor='w', padx=10, pady=(0, 5))
        
        # Logout button at bottom
        tk.Button(
            self.content_frame,
            text="Logout",
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            command=self.logout_employee,
            width=15
        ).pack(pady=20)
    
    def logout_employee(self):
        """Logout employee and return to login screen"""
        self.current_employee = None
        self.show_login_screen()
    
    def show_employee_screen(self):
        """Show employee check-in/out screen"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text="Employee Check-in/out",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        if not self.current_employee:
            tk.Label(
                self.content_frame,
                text="Please login first",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
            tk.Button(
                self.content_frame,
                text="Go to Login",
                command=self.show_employee_login
            ).pack()
            return
        
        # Check if already checked in
        has_checked_in = self.data_handler.has_checked_in_today(self.current_employee['id'])
        
        if has_checked_in:
            tk.Label(
                self.content_frame,
                text=f"You are checked in today, {self.current_employee['name']}",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
            
            def check_out():
                self.data_handler.record_check_out(self.current_employee['id'])
                messagebox.showinfo("Success", "Checked out successfully!")
                self.show_employee_dashboard()
            
            tk.Button(
                self.content_frame,
                text="Check Out",
                bg='#e74c3c',
                fg='white',
                font=('Arial', 14, 'bold'),
                command=check_out,
                width=20,
                height=3
            ).pack(pady=20)
        else:
            tk.Label(
                self.content_frame,
                text=f"Welcome, {self.current_employee['name']}",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
            
            def check_in():
                self.data_handler.record_check_in(
                    self.current_employee['id'],
                    self.current_employee['name'],
                    self.current_employee.get('department', '')
                )
                messagebox.showinfo("Success", "Checked in successfully!")
                self.show_employee_dashboard()
            
            tk.Button(
                self.content_frame,
                text="Check In",
                bg='#27ae60',
                fg='white',
                font=('Arial', 14, 'bold'),
                command=check_in,
                width=20,
                height=3
            ).pack(pady=20)
        
        tk.Button(
            self.content_frame,
            text="Back to Dashboard",
            command=self.show_employee_dashboard
        ).pack(pady=10)
    
    def show_my_attendance(self):
        """Show current employee's attendance"""
        self.clear_content_frame()
        
        if not self.current_employee:
            self.show_employee_login()
            return
        
        tk.Label(
            self.content_frame,
            text=f"My Attendance - {self.current_employee['name']}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get attendance records
        records = self.data_handler.get_employee_attendance(self.current_employee['id'])
        
        if not records:
            tk.Label(
                self.content_frame,
                text="No attendance records found",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=50)
        else:
            # Create treeview
            columns = ('Date', 'Check-in', 'Check-out', 'Status', 'Hours Worked')
            tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            tree.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Add records (show most recent first)
            for record in reversed(records[-50:]):  # Show last 50 records
                hours = "N/A"
                if record.get('check_in') and record.get('check_out'):
                    try:
                        check_in = datetime.strptime(record['check_in'], "%H:%M:%S")
                        check_out = datetime.strptime(record['check_out'], "%H:%M:%S")
                        hours = f"{(check_out - check_in).seconds / 3600:.2f}h"
                    except:
                        hours = "N/A"
                
                tree.insert('', 'end', values=(
                    record.get('date', ''),
                    record.get('check_in', 'N/A'),
                    record.get('check_out', 'N/A'),
                    record.get('status', ''),
                    hours
                ))
        
        tk.Button(
            self.content_frame,
            text="Back to Dashboard",
            command=self.show_employee_dashboard
        ).pack(pady=20)
    
    def show_correction_request_form(self):
        """Show form to request attendance correction"""
        self.clear_content_frame()
        
        if not self.current_employee:
            self.show_employee_login()
            return
        
        tk.Label(
            self.content_frame,
            text="Request Attendance Correction",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Form frame
        form_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        form_frame.pack(pady=20, padx=20)
        
        # Date selection
        tk.Label(form_frame, text="Date to Correct (YYYY-MM-DD):", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        date_entry = tk.Entry(form_frame, width=25)
        date_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Original status
        tk.Label(form_frame, text="Original Status:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        original_var = tk.StringVar(value="Absent")
        original_combo = ttk.Combobox(form_frame, textvariable=original_var, 
                                     values=["Present", "Absent", "Late"], width=22)
        original_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Requested correction
        tk.Label(form_frame, text="Requested Correction:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        requested_var = tk.StringVar(value="Present")
        requested_combo = ttk.Combobox(form_frame, textvariable=requested_var, 
                                      values=["Present", "Absent", "Late"], width=22)
        requested_combo.grid(row=2, column=1, padx=10, pady=5)
        
        # Reason
        tk.Label(form_frame, text="Reason for Correction:", bg='#f0f0f0').grid(row=3, column=0, sticky='w', pady=5)
        reason_text = scrolledtext.ScrolledText(form_frame, width=30, height=4)
        reason_text.grid(row=3, column=1, padx=10, pady=5)
        
        def submit_request():
            correction_date = date_entry.get().strip()
            reason = reason_text.get("1.0", "end-1c").strip()
            
            if not correction_date:
                messagebox.showwarning("Input Required", "Please enter the date")
                return
            
            if not reason:
                messagebox.showwarning("Input Required", "Please enter a reason")
                return
            
            # Submit correction request
            success = self.data_handler.submit_correction_request(
                employee_id=self.current_employee['id'],
                employee_name=self.current_employee['name'],
                original_date=correction_date,
                original_status=original_var.get(),
                requested_correction={"status": requested_var.get()},
                reason=reason
            )
            
            if success:
                messagebox.showinfo("Success", "Correction request submitted successfully!")
                self.show_employee_dashboard()
            else:
                messagebox.showerror("Error", "Failed to submit request")
        
        tk.Button(
            form_frame,
            text="Submit Request",
            bg='#3498db',
            fg='white',
            command=submit_request,
            width=15
        ).grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(
            self.content_frame,
            text="Back to Dashboard",
            command=self.show_employee_dashboard
        ).pack(pady=10)
    
    def show_all_announcements(self):
        """Show all announcements for current user (and mark them read)"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text="School Announcements",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        if self.current_employee:
            announcements = self.data_handler.get_announcements_for_employee(
                self.current_employee['id'], self.current_employee.get('department', 'All')
            )
        else:
            announcements = self.data_handler.get_announcements()
        
        if not announcements:
            tk.Label(
                self.content_frame,
                text="No announcements available",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=50)
        else:
            # Create scrollable frame
            canvas = tk.Canvas(self.content_frame, bg='#f0f0f0', height=400)
            scrollbar = tk.Scrollbar(self.content_frame, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Display announcements
            for ann in announcements:
                frame = tk.Frame(scrollable_frame, bg='white', relief='solid', borderwidth=1)
                frame.pack(fill='x', pady=5, padx=10)
                
                # Priority color
                priority = ann.get('priority', 'Medium')
                if priority == 'High':
                    frame.configure(bg='#ffebee')
                elif priority == 'Low':
                    frame.configure(bg='#e8f5e9')
                
                tk.Label(
                    frame,
                    text=f"📢 {ann['title']}",
                    font=('Arial', 12, 'bold'),
                    bg=frame['bg']
                ).pack(anchor='w', padx=10, pady=(10, 0))
                
                tk.Label(
                    frame,
                    text=ann['content'],
                    font=('Arial', 10),
                    bg=frame['bg'],
                    wraplength=800,
                    justify='left'
                ).pack(anchor='w', padx=10, pady=5)
                
                tk.Label(
                    frame,
                    text=f"By: {ann['author']} | {ann['date'][:10]}",
                    font=('Arial', 9),
                    bg=frame['bg'],
                    fg='#666'
                ).pack(anchor='w', padx=10, pady=(0, 10))
                
                # Mark read for current employee
                if self.current_employee:
                    try:
                        self.data_handler.mark_announcement_as_read(ann.get('id'), self.current_employee['id'])
                    except:
                        pass
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
        
        if self.current_employee:
            tk.Button(
                self.content_frame,
                text="Back to Dashboard",
                command=self.show_employee_dashboard
            ).pack(pady=20)
        else:
            tk.Button(
                self.content_frame,
                text="Back",
                command=self.show_login_screen
            ).pack(pady=20)
    
    def show_record_monthly_attendance(self):
        """Dialog to record monthly attendance by a teacher for students in current_grade"""
        if not self.current_employee:
            self.show_employee_login()
            return
        if self.current_employee.get("department") != "Teaching":
            messagebox.showinfo("Access Denied", "Only teaching staff can record monthly pupil attendance")
            return
        if not self.current_grade:
            # If no current grade selected, show grade selection first
            self.show_teaching_grade_selection()
            return
        
        students = self.data_handler.get_students_by_class(self.current_grade)
        if not students:
            messagebox.showinfo("No Students", "No students in this grade")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Record Monthly Attendance")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Record Monthly Attendance - {self.current_grade}", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Student selection
        frame_top = tk.Frame(dialog)
        frame_top.pack(pady=5)
        tk.Label(frame_top, text="Select Student:", font=('Arial', 10)).pack(side='left', padx=5)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(frame_top, textvariable=student_var, values=[f"{s['id']}: {s['name']}" for s in students], width=50)
        student_combo.pack(side='left', padx=5)
        
        # Month selection
        tk.Label(frame_top, text="Month (YYYY-MM):", font=('Arial', 10)).pack(side='left', padx=5)
        month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        month_entry = tk.Entry(frame_top, textvariable=month_var, width=10)
        month_entry.pack(side='left', padx=5)
        
        days_frame = tk.Frame(dialog)
        days_frame.pack(fill='both', expand=True, pady=10, padx=10)
        
        check_vars = {}
        
        def load_days_for_student():
            # Clear existing
            for w in days_frame.winfo_children():
                w.destroy()
            sid_sel = student_var.get()
            month_key = month_var.get().strip()
            if not sid_sel or not month_key:
                return
            try:
                sid = int(sid_sel.split(':')[0])
            except:
                messagebox.showerror("Error", "Invalid student selection")
                return
            
            # Determine year and month
            try:
                year, month = month_key.split('-')
                year = int(year); month = int(month)
            except:
                messagebox.showerror("Error", "Month must be in YYYY-MM format")
                return
            
            # Number of days in the month
            num_days = calendar.monthrange(year, month)[1]
            # Load existing month map if any
            existing = self.data_handler.get_student_monthly_attendance(sid, month_key)
            
            canvas = tk.Canvas(days_frame)
            scrollbar = tk.Scrollbar(days_frame, orient='vertical', command=canvas.yview)
            inner = tk.Frame(canvas)
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0,0), window=inner, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            for d in range(1, num_days+1):
                day_date = date(year, month, d)
                date_str = day_date.isoformat()
                status = existing.get(date_str, "Absent")
                var = tk.IntVar(value=1 if status=="Present" else 0)
                check_vars[date_str] = var
                row = tk.Frame(inner, bg='white', pady=2)
                row.pack(fill='x', padx=5, pady=2)
                chk = tk.Checkbutton(row, text=f"{date_str} ({day_date.strftime('%A')}) - Present", variable=var, bg='white')
                chk.pack(side='left', anchor='w')
        
        def submit_month():
            sid_sel = student_var.get()
            month_key = month_var.get().strip()
            if not sid_sel or not month_key:
                messagebox.showwarning("Input Required", "Select student and month")
                return
            try:
                sid = int(sid_sel.split(':')[0])
            except:
                messagebox.showerror("Error", "Invalid student selection")
                return
            # Build map
            attendance_map = {}
            for date_str, var in check_vars.items():
                attendance_map[date_str] = "Present" if var.get()==1 else "Absent"
            success, message = self.student_manager.record_monthly_attendance(sid, month_key, attendance_map)
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                # refresh grade attendance view if open
                self.show_grade_attendance()
            else:
                messagebox.showerror("Error", message)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Load Days", command=load_days_for_student, width=12, bg='#3498db', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Submit Month", command=submit_month, width=12, bg='#27ae60', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12).pack(side='left', padx=5)
    
    def show_teaching_grade_selection(self):
        """Show grade selection for teaching staff"""
        if not self.current_employee:
            self.show_employee_login()
            return
        
        if self.current_employee.get("department") != "Teaching":
            messagebox.showinfo("Access Denied", "This feature is only for teaching staff")
            self.show_employee_dashboard()
            return
        
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Grade Management - {self.current_employee['name']}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text="Select a grade to manage:",
            font=('Arial', 14),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))
        
        # Get assigned grades for this teacher
        assigned_grades = self.current_employee.get("assigned_grades", [])
        
        if not assigned_grades:
            tk.Label(
                self.content_frame,
                text="No grades assigned to you. Please contact admin.",
                font=('Arial', 12),
                bg='#f0f0f0',
                fg='#e74c3c'
            ).pack(pady=20)
            
            tk.Button(
                self.content_frame,
                text="Back to Dashboard",
                font=('Arial', 12),
                command=self.show_employee_dashboard
            ).pack(pady=10)
            return
        
        # Display grade buttons in a grid
        grades_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        grades_frame.pack(pady=20)
        
        for i, grade in enumerate(assigned_grades):
            btn = tk.Button(
                grades_frame,
                text=grade,
                font=('Arial', 14, 'bold'),
                bg='#9b59b6',
                fg='white',
                width=15,
                height=3,
                command=lambda g=grade: self.show_grade_management(g)
            )
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
        
        # Back button
        tk.Button(
            self.content_frame,
            text="Back to Dashboard",
            font=('Arial', 12),
            command=self.show_employee_dashboard
        ).pack(pady=20)
    
    def show_grade_management(self, grade):
        """Show management interface for a specific grade"""
        self.current_grade = grade
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Grade {grade} Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text=f"Teacher: {self.current_employee['name']}",
            font=('Arial', 14),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))
        
        # Management options
        options_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        options_frame.pack(pady=20)
        
        options = [
            ("👨‍🎓 View Students", self.show_grade_students),
            ("➕ Add Student", self.show_add_student_to_grade),
            ("📊 Attendance", self.show_grade_attendance),
            ("📚 Academic Results", self.show_grade_results),
            ("🏥 Health Records", self.show_health_records),
            ("📸 Update Photos", self.show_photo_management)
        ]
        
        for i, (text, command) in enumerate(options):
            btn = tk.Button(
                options_frame,
                text=text,
                font=('Arial', 12),
                bg='#3498db',
                fg='white',
                width=20,
                height=2,
                command=command
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        
        # Back button
        tk.Button(
            self.content_frame,
            text=f"Back to Grade Selection",
            font=('Arial', 12),
            command=self.show_teaching_grade_selection
        ).pack(pady=20)
    
    def show_grade_students(self):
        """Show students in the selected grade"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Students in Grade {self.current_grade}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get students for this grade
        students = self.data_handler.get_students_by_class(self.current_grade)
        
        if not students:
            tk.Label(
                self.content_frame,
                text="No students in this grade yet.",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
            
            tk.Button(
                self.content_frame,
                text="Add Student",
                bg='#27ae60',
                fg='white',
                command=self.show_add_student_to_grade
            ).pack(pady=10)
        else:
            # Create notebook for different views
            notebook = ttk.Notebook(self.content_frame)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Basic info tab
            basic_tab = tk.Frame(notebook, bg='#f0f0f0')
            notebook.add(basic_tab, text="Basic Info")
            
            # Treeview
            columns = ('No.', 'ID', 'Name', 'Age', 'Parent Contact', 'Health Status')
            tree = ttk.Treeview(basic_tab, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            tree.column('Name', width=180)
            tree.column('Parent Contact', width=120)
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add students to tree with numbering
            for idx, student in enumerate(students, start=1):
                tree.insert('', 'end', values=(
                    idx,
                    student.get('id', ''),
                    student.get('name', ''),
                    student.get('age', ''),
                    student.get('parent_contact', ''),
                    student.get('health_status', '')
                ))
            
            # Detailed info tab
            detail_tab = tk.Frame(notebook, bg='#f0f0f0')
            notebook.add(detail_tab, text="Full Details")
            
            # Scrollable frame for details
            canvas = tk.Canvas(detail_tab, bg='#f0f0f0')
            scrollbar = tk.Scrollbar(detail_tab, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Display detailed info for each student
            for student in students:
                frame = tk.Frame(scrollable_frame, bg='white', relief='solid', borderwidth=1)
                frame.pack(fill='x', pady=5, padx=5)
                
                # Student photo if available
                photo_path = self.data_handler.get_student_photo(student['id'])
                if photo_path and os.path.exists(photo_path):
                    try:
                        img = Image.open(photo_path)
                        img.thumbnail((80, 80))
                        photo = ImageTk.PhotoImage(img)
                        photo_label = tk.Label(frame, image=photo, bg='white')
                        photo_label.image = photo
                        photo_label.pack(side='left', padx=10, pady=10)
                    except:
                        pass
                
                # Student info
                info_frame = tk.Frame(frame, bg='white')
                info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
                
                tk.Label(
                    info_frame,
                    text=f"📌 {student['name']} (ID: {student['id']})",
                    font=('Arial', 12, 'bold'),
                    bg='white'
                ).pack(anchor='w')
                
                info_text = f"Age: {student.get('age', 'N/A')} | DOB: {student.get('dob', 'N/A')}\n"
                info_text += f"Health: {student.get('health_status', 'N/A')}"
                if student.get('allergies'):
                    info_text += f" | Allergies: {student['allergies']}\n"
                else:
                    info_text += "\n"
                info_text += f"Address: {student.get('address', 'N/A')}\n"
                info_text += f"Parent: {student.get('parent_contact', 'N/A')}"
                if student.get('parent_email'):
                    info_text += f" | Email: {student['parent_email']}"
                info_text += f"\nEmergency: {student.get('emergency_contact', 'N/A')}"
                
                tk.Label(
                    info_frame,
                    text=info_text,
                    font=('Arial', 10),
                    bg='white',
                    justify='left'
                ).pack(anchor='w')
                
                # Action buttons
                btn_frame = tk.Frame(frame, bg='white')
                btn_frame.pack(side='right', padx=10, pady=10)
                
                tk.Button(
                    btn_frame,
                    text="Edit",
                    command=lambda sid=student['id']: self.edit_student_details(sid),
                    width=10
                ).pack(pady=2)
                
                tk.Button(
                    btn_frame,
                    text="Results",
                    command=lambda sid=student['id']: self.show_student_results(sid),
                    width=10
                ).pack(pady=2)
                
                tk.Button(
                    btn_frame,
                    text="Attendance",
                    command=lambda sid=student['id']: self.show_student_attendance(sid),
                    width=10
                ).pack(pady=2)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
        
        # Back button
        tk.Button(
            self.content_frame,
            text="Back to Grade Management",
            command=lambda: self.show_grade_management(self.current_grade)
        ).pack(pady=20)
    
    def show_add_student_to_grade(self):
        """Show form to add student to current grade"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Add Student to Grade {self.current_grade}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Personal Info Tab
        personal_tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(personal_tab, text="Personal Information")
        
        form_frame = tk.Frame(personal_tab, bg='#f0f0f0')
        form_frame.pack(pady=20, padx=20)
        
        # Name
        tk.Label(form_frame, text="Full Name:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Date of Birth
        tk.Label(form_frame, text="Date of Birth (YYYY-MM-DD):", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        dob_entry = tk.Entry(form_frame, width=30)
        dob_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Address
        tk.Label(form_frame, text="Address:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        address_entry = tk.Entry(form_frame, width=30)
        address_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Health Info Tab
        health_tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(health_tab, text="Health Information")
        
        health_frame = tk.Frame(health_tab, bg='#f0f0f0')
        health_frame.pack(pady=20, padx=20)
        
        # Health Status
        tk.Label(health_frame, text="Health Status:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        health_var = tk.StringVar(value="Good")
        health_combo = ttk.Combobox(health_frame, textvariable=health_var, 
                                   values=["Excellent", "Good", "Fair", "Poor"], width=27)
        health_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Allergies
        tk.Label(health_frame, text="Allergies:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        allergies_entry = tk.Entry(health_frame, width=30)
        allergies_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Emergency Contact
        tk.Label(health_frame, text="Emergency Contact:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        emergency_entry = tk.Entry(health_frame, width=30)
        emergency_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Contact Info Tab
        contact_tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(contact_tab, text="Contact Information")
        
        contact_frame = tk.Frame(contact_tab, bg='#f0f0f0')
        contact_frame.pack(pady=20, padx=20)
        
        # Parent Contact
        tk.Label(contact_frame, text="Parent Phone:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        parent_phone_entry = tk.Entry(contact_frame, width=30)
        parent_phone_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Parent Email
        tk.Label(contact_frame, text="Parent Email:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        parent_email_entry = tk.Entry(contact_frame, width=30)
        parent_email_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Photo Tab
        photo_tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(photo_tab, text="Photo")
        
        photo_frame = tk.Frame(photo_tab, bg='#f0f0f0')
        photo_frame.pack(pady=20, padx=20)
        
        self.student_photo_path = None
        photo_label = tk.Label(photo_frame, text="No photo selected", bg='#f0f0f0')
        photo_label.pack(pady=10)
        
        def select_photo():
            filepath = filedialog.askopenfilename(
                title="Select Student Photo",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )
            if filepath:
                self.student_photo_path = filepath
                try:
                    img = Image.open(filepath)
                    img.thumbnail((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    photo_label.config(image=photo, text="")
                    photo_label.image = photo
                except:
                    messagebox.showerror("Error", "Could not load image")
        
        tk.Button(
            photo_frame,
            text="Select Photo",
            command=select_photo
        ).pack(pady=10)
        
        def add_student():
            name = name_entry.get().strip()
            dob = dob_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Input Required", "Please enter student name")
                return
            
            # Add student
            success, message = self.student_manager.add_new_student(
                name=name,
                class_name=self.current_grade,
                parent_contact=parent_phone_entry.get(),
                parent_email=parent_email_entry.get(),
                dob=dob,
                address=address_entry.get(),
                health_status=health_var.get(),
                allergies=allergies_entry.get(),
                emergency_contact=emergency_entry.get()
            )
            
            if success:
                # Save photo if selected
                if self.student_photo_path:
                    # Get the new student ID
                    students = self.data_handler.get_students_by_class(self.current_grade)
                    new_student = next((s for s in students if s['name'] == name), None)
                    if new_student:
                        self.data_handler.save_student_photo(new_student['id'], self.student_photo_path)
                
                messagebox.showinfo("Success", message)
                self.show_grade_students()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(
            self.content_frame,
            text="Add Student",
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            command=add_student,
            width=15
        ).pack(pady=20)
        
        tk.Button(
            self.content_frame,
            text="Cancel",
            command=lambda: self.show_grade_management(self.current_grade)
        ).pack()
    
    def show_employee_settings(self):
        """Show employee settings (change password)"""
        if not self.current_employee:
            self.show_employee_login()
            return
        
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text="Employee Settings",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text=f"Employee: {self.current_employee['name']}",
            font=('Arial', 14),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))
        
        # Change password frame
        pass_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        pass_frame.pack(pady=20)
        
        tk.Label(
            pass_frame,
            text="Change Password",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 10))
        
        tk.Label(pass_frame, text="Current Password:", bg='#f0f0f0').pack(anchor='w')
        current_pass_entry = tk.Entry(pass_frame, show='*', width=25)
        current_pass_entry.pack(pady=(0, 5))
        
        tk.Label(pass_frame, text="New Password:", bg='#f0f0f0').pack(anchor='w')
        new_pass_entry = tk.Entry(pass_frame, show='*', width=25)
        new_pass_entry.pack(pady=(0, 5))
        
        tk.Label(pass_frame, text="Confirm New Password:", bg='#f0f0f0').pack(anchor='w')
        confirm_pass_entry = tk.Entry(pass_frame, show='*', width=25)
        confirm_pass_entry.pack(pady=(0, 10))
        
        status_label = tk.Label(pass_frame, text="", bg='#f0f0f0')
        status_label.pack()
        
        def change_password():
            current = current_pass_entry.get()
            new = new_pass_entry.get()
            confirm = confirm_pass_entry.get()
            
            if not current or not new or not confirm:
                messagebox.showwarning("Input Required", "Please fill in all fields")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match")
                return
            
            if len(new) < 6:
                messagebox.showwarning("Weak Password", "Password must be at least 6 characters")
                return
            
            success = self.data_handler.change_employee_password(
                self.current_employee['id'], current, new
            )
            
            if success:
                status_label.config(text="Password changed successfully!", fg='green')
                current_pass_entry.delete(0, 'end')
                new_pass_entry.delete(0, 'end')
                confirm_pass_entry.delete(0, 'end')
            else:
                messagebox.showerror("Error", "Current password is incorrect")
        
        tk.Button(
            pass_frame,
            text="Change Password",
            command=change_password,
            width=15
        ).pack(pady=10)
        
        # Back button
        tk.Button(
            self.content_frame,
            text="Back to Dashboard",
            command=self.show_employee_dashboard
        ).pack(pady=20)
    
    def create_employee_management_tab(self, notebook):
        """Create tab for managing employees (admin only)"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Manage Employees")
        
        # Create notebook within tab
        emp_notebook = ttk.Notebook(tab)
        emp_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add a new tab for password management
        password_tab = tk.Frame(emp_notebook, bg='#f0f0f0')
        emp_notebook.add(password_tab, text="Reset Passwords")
        
        tk.Label(
            password_tab,
            text="Reset Employee Password",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Employee selection
        pass_frame = tk.Frame(password_tab, bg='#f0f0f0')
        pass_frame.pack(pady=10)
        
        tk.Label(pass_frame, text="Select Employee:", bg='#f0f0f0').pack(side='left', padx=5)
        
        all_employees = self.data_handler.get_all_employees()
        pass_emp_var = tk.StringVar()
        pass_emp_combo = ttk.Combobox(
            pass_frame,
            textvariable=pass_emp_var,
            values=[f"{emp['id']}: {emp['name']} ({emp['department']})" for emp in all_employees],
            state='readonly',
            width=35
        )
        pass_emp_combo.pack(side='left', padx=5)
        
        # New password
        pass_new_frame = tk.Frame(password_tab, bg='#f0f0f0')
        pass_new_frame.pack(pady=10)
        
        tk.Label(pass_new_frame, text="New Password:", bg='#f0f0f0').pack(side='left', padx=5)
        new_pass_var = tk.StringVar()
        new_pass_entry = tk.Entry(pass_new_frame, textvariable=new_pass_var, show='*', width=20)
        new_pass_entry.pack(side='left', padx=5)
        
        def reset_password():
            emp_selection = pass_emp_var.get()
            new_password = new_pass_var.get()
            
            if not emp_selection or not new_password:
                messagebox.showwarning("Input Required", "Please select employee and enter new password")
                return
            
            if len(new_password) < 6:
                messagebox.showwarning("Weak Password", "Password must be at least 6 characters")
                return
            
            try:
                emp_id = int(emp_selection.split(':')[0])
            except:
                messagebox.showerror("Error", "Invalid employee selection")
                return
            
            success, message = self.admin_manager.reset_employee_password(emp_id, new_password)
            
            if success:
                messagebox.showinfo("Success", message)
                pass_emp_var.set('')
                new_pass_var.set('')
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(
            password_tab,
            text="Reset Password",
            bg='#3498db',
            fg='white',
            command=reset_password,
            width=15
        ).pack(pady=20)
        
        # Add Employee Tab
        add_tab = tk.Frame(emp_notebook, bg='#f0f0f0')
        emp_notebook.add(add_tab, text="Add Employee")
        
        tk.Label(
            add_tab,
            text="Add New Employee",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Form for adding employee
        form_frame = tk.Frame(add_tab, bg='#f0f0f0')
        form_frame.pack(pady=10, padx=20)
        
        # Name
        tk.Label(form_frame, text="Full Name:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        emp_name_entry = tk.Entry(form_frame, width=30)
        emp_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Department
        tk.Label(form_frame, text="Department:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(form_frame, textvariable=dept_var, 
                                 values=self.data_handler.get_all_departments(), width=27)
        dept_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Role
        tk.Label(form_frame, text="Role/Position:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        role_entry = tk.Entry(form_frame, width=30)
        role_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Email
        tk.Label(form_frame, text="Email:", bg='#f0f0f0').grid(row=3, column=0, sticky='w', pady=5)
        email_entry = tk.Entry(form_frame, width=30)
        email_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Phone
        tk.Label(form_frame, text="Phone:", bg='#f0f0f0').grid(row=4, column=0, sticky='w', pady=5)
        phone_entry = tk.Entry(form_frame, width=30)
        phone_entry.grid(row=4, column=1, padx=10, pady=5)
        
        # Address
        tk.Label(form_frame, text="Address:", bg='#f0f0f0').grid(row=5, column=0, sticky='w', pady=5)
        address_entry = tk.Entry(form_frame, width=30)
        address_entry.grid(row=5, column=1, padx=10, pady=5)
        
        # Password
        tk.Label(form_frame, text="Default Password:", bg='#f0f0f0').grid(row=6, column=0, sticky='w', pady=5)
        password_entry = tk.Entry(form_frame, width=30)
        password_entry.insert(0, "default123")
        password_entry.grid(row=6, column=1, padx=10, pady=5)
        
        def add_employee():
            name = emp_name_entry.get().strip()
            department = dept_var.get()
            role = role_entry.get().strip()
            
            if not name or not department:
                messagebox.showwarning("Input Required", "Name and department are required")
                return
            
            success, message = self.admin_manager.add_employee_with_details(
                name=name,
                department=department,
                role=role,
                email=email_entry.get(),
                phone=phone_entry.get(),
                address=address_entry.get(),
                password=password_entry.get()
            )
            
            if success:
                messagebox.showinfo("Success", message)
                # Clear form
                emp_name_entry.delete(0, 'end')
                dept_var.set('')
                role_entry.delete(0, 'end')
                email_entry.delete(0, 'end')
                phone_entry.delete(0, 'end')
                address_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                password_entry.insert(0, "default123")
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(
            add_tab,
            text="Add Employee",
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            command=add_employee,
            width=15
        ).pack(pady=20)
        
        # Assign Grades Tab (for teaching staff)
        assign_tab = tk.Frame(emp_notebook, bg='#f0f0f0')
        emp_notebook.add(assign_tab, text="Assign Grades")
        
        tk.Label(
            assign_tab,
            text="Assign Grades to Teaching Staff",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Employee selection
        emp_frame = tk.Frame(assign_tab, bg='#f0f0f0')
        emp_frame.pack(pady=10)
        
        tk.Label(emp_frame, text="Select Employee:", bg='#f0f0f0').pack(side='left', padx=5)
        
        # Get teaching staff only
        all_employees = self.data_handler.get_all_employees()
        teaching_staff = [emp for emp in all_employees if emp.get("department") == "Teaching"]
        
        assign_emp_var = tk.StringVar()
        assign_emp_combo = ttk.Combobox(
            emp_frame,
            textvariable=assign_emp_var,
            values=[f"{emp['id']}: {emp['name']}" for emp in teaching_staff],
            state='readonly',
            width=30
        )
        assign_emp_combo.pack(side='left', padx=5)
        
        # Grade selection
        grade_frame = tk.Frame(assign_tab, bg='#f0f0f0')
        grade_frame.pack(pady=10)
        
        tk.Label(grade_frame, text="Select Grade:", bg='#f0f0f0').pack(side='left', padx=5)
        
        grades = self.data_handler.get_all_classes()
        grade_var = tk.StringVar()
        grade_combo = ttk.Combobox(
            grade_frame,
            textvariable=grade_var,
            values=grades,
            state='readonly',
            width=20
        )
        grade_combo.pack(side='left', padx=5)
        
        def assign_grade():
            emp_selection = assign_emp_var.get()
            grade = grade_var.get()
            
            if not emp_selection or not grade:
                messagebox.showwarning("Selection Required", "Please select employee and grade")
                return
            
            try:
                emp_id = int(emp_selection.split(':')[0])
            except:
                messagebox.showerror("Error", "Invalid employee selection")
                return
            
            # Validate assignment
            valid, message = self.admin_manager.validate_grade_assignment(emp_id, grade)
            if not valid:
                messagebox.showwarning("Invalid Assignment", message)
                return
            
            success, message = self.admin_manager.assign_grade_to_employee(emp_id, grade)
            
            if success:
                messagebox.showinfo("Success", message)
                assign_emp_var.set('')
                grade_var.set('')
            else:
                messagebox.showerror("Error", message)
        
        def remove_assignment():
            emp_selection = assign_emp_var.get()
            grade = grade_var.get()
            
            if not emp_selection or not grade:
                messagebox.showwarning("Selection Required", "Please select employee and grade")
                return
            
            try:
                emp_id = int(emp_selection.split(':')[0])
            except:
                messagebox.showerror("Error", "Invalid employee selection")
                return
            
            success, message = self.admin_manager.remove_grade_from_employee(emp_id, grade)
            
            if success:
                messagebox.showinfo("Success", message)
                assign_emp_var.set('')
                grade_var.set('')
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(
            assign_tab,
            text="Assign Grade",
            bg='#3498db',
            fg='white',
            command=assign_grade,
            width=15
        ).pack(side='left', padx=20, pady=20)
        
        tk.Button(
            assign_tab,
            text="Remove Assignment",
            bg='#e74c3c',
            fg='white',
            command=remove_assignment,
            width=15
        ).pack(side='left', padx=20, pady=20)
    
    def show_admin_panel(self):
        """Show admin panel with multiple tabs"""
        self.clear_content_frame()
        
        # Add Back to Menu button at top
        top_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        top_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            top_frame,
            text="← Back to Main Menu",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            command=self.show_login_screen
        ).pack(side='left')

                # NEW: open SIS web UI button (opens SIS in default browser as admin)
        def open_sis_admin():
            webbrowser.open("http://127.0.0.1:5000/sis?role=admin")

        tk.Button(
            top_frame,
            text="Open SIS Web UI",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            command=open_sis_admin
        ).pack(side='left', padx=5)

        # OPTIONAL: open SIS for currently-logged-in teacher (if an employee is logged in)
        def open_sis_for_teacher():
            if self.current_employee and self.current_employee.get('id'):
                emp_id = self.current_employee['id']
                webbrowser.open(f"http://127.0.0.1:5000/sis?role=teacher&employee_id={emp_id}")
            else:
                messagebox.showinfo("Not logged in", "No employee is currently logged in.")

        tk.Button(
            top_frame,
            text="Open SIS (My Grade)",
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            command=open_sis_for_teacher
        ).pack(side='left', padx=5)
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs - ADDED NEW EMPLOYEE MANAGEMENT TAB
        self.create_dashboard_tab(notebook)
        self.create_view_tab(notebook)
        self.create_employee_management_tab(notebook)  # NEW: Employee management
        self.create_correction_requests_tab(notebook)
        self.create_student_admin_tab(notebook)
        self.create_reports_tab(notebook)
        self.create_announcements_tab(notebook)  # NEW: Announcements management
        self.create_settings_tab(notebook)
        
        # Logout button at bottom
        tk.Button(
            self.content_frame,
            text="Logout Admin",
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            command=self.logout_admin
        ).pack(pady=10)
    
    def create_dashboard_tab(self, notebook):
        """Create dashboard tab for admin"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Dashboard")
        
        tk.Label(
            tab,
            text="System Overview",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get system stats
        today = date.today().isoformat()
        attendance = self.data_handler.get_attendance_by_date(today)
        total_employees = len(self.data_handler.get_all_employees())
        total_students = len(self.data_handler.get_all_students())
        
        stats_frame = tk.Frame(tab, bg='#f0f0f0')
        stats_frame.pack(pady=20)
        
        stats = [
            f"Total Employees: {total_employees}",
            f"Total Students: {total_students}",
            f"Present Today: {len([r for r in attendance if r.get('status') == 'Present'])}",
            f"Absent Today: {len([r for r in attendance if r.get('status') == 'Absent'])}"
        ]
        
        for stat in stats:
            tk.Label(
                stats_frame,
                text=stat,
                font=('Arial', 12),
                bg='#f0f0f0'
            ).pack(pady=5)
    
    def create_view_tab(self, notebook):
        """Create view attendance tab"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="View Attendance")
        
        tk.Label(
            tab,
            text="View Attendance Records",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Date selection
        date_frame = tk.Frame(tab, bg='#f0f0f0')
        date_frame.pack(pady=10)
        
        tk.Label(date_frame, text="Select Date:", bg='#f0f0f0').pack(side='left', padx=5)
        self.view_date_var = tk.StringVar(value=date.today().isoformat())
        date_entry = tk.Entry(date_frame, textvariable=self.view_date_var, width=15)
        date_entry.pack(side='left', padx=5)
        
        def load_attendance():
            selected_date = self.view_date_var.get()
            records = self.data_handler.get_attendance_by_date(selected_date)
            
            # Clear previous results
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            if not records:
                tk.Label(results_frame, text="No records found", bg='#f0f0f0').pack()
                return
            
            # Create treeview
            columns = ('ID', 'Name', 'Department', 'Check-in', 'Check-out', 'Status')
            tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add records
            for record in records:
                tree.insert('', 'end', values=(
                    record.get('employee_id', ''),
                    record.get('employee_name', ''),
                    record.get('department', ''),
                    record.get('check_in', 'N/A'),
                    record.get('check_out', 'N/A'),
                    record.get('status', '')
                ))
        
        tk.Button(
            date_frame,
            text="Load",
            command=load_attendance
        ).pack(side='left', padx=10)
        
        # Results frame
        results_frame = tk.Frame(tab, bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Load today's attendance by default
        load_attendance()
    
    def create_correction_requests_tab(self, notebook):
        """Create correction requests tab"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Correction Requests")
        
        tk.Label(
            tab,
            text="Manage Correction Requests",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get all correction requests
        requests = self.data_handler.get_correction_requests()
        
        if not requests:
            tk.Label(
                tab,
                text="No pending correction requests",
                font=('Arial', 12),
                bg='#f0f0f0'
            ).pack(pady=50)
        else:
            # Create treeview for requests
            columns = ('ID', 'Employee', 'Date', 'Original', 'Requested', 'Status')
            tree = ttk.Treeview(tab, columns=columns, show='headings', height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            tree.column('Employee', width=150)
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add requests
            for request in requests:
                tree.insert('', 'end', values=(
                    request.get('id', ''),
                    request.get('employee_name', ''),
                    request.get('original_date', ''),
                    request.get('original_status', ''),
                    request['requested_correction'].get('status', ''),
                    request.get('status', '')
                ))
            
            # Action buttons frame
            action_frame = tk.Frame(tab, bg='#f0f0f0')
            action_frame.pack(pady=10)
            
            tk.Label(action_frame, text="Request ID:", bg='#f0f0f0').pack(side='left', padx=5)
            request_id_entry = tk.Entry(action_frame, width=10)
            request_id_entry.pack(side='left', padx=5)
            
            def approve_request():
                try:
                    req_id = int(request_id_entry.get())
                    success = self.data_handler.update_correction_request(
                        req_id, "Approved", "Admin", "Request approved"
                    )
                    if success:
                        messagebox.showinfo("Success", "Request approved")
                        self.create_correction_requests_tab(notebook)  # Refresh
                    else:
                        messagebox.showerror("Error", "Failed to approve request")
                except:
                    messagebox.showerror("Error", "Invalid request ID")
            
            def reject_request():
                try:
                    req_id = int(request_id_entry.get())
                    success = self.data_handler.update_correction_request(
                        req_id, "Rejected", "Admin", "Request rejected"
                    )
                    if success:
                        messagebox.showinfo("Success", "Request rejected")
                        self.create_correction_requests_tab(notebook)  # Refresh
                    else:
                        messagebox.showerror("Error", "Failed to reject request")
                except:
                    messagebox.showerror("Error", "Invalid request ID")
            
            tk.Button(
                action_frame,
                text="Approve",
                bg='#27ae60',
                fg='white',
                command=approve_request
            ).pack(side='left', padx=5)
            
            tk.Button(
                action_frame,
                text="Reject",
                bg='#e74c3c',
                fg='white',
                command=reject_request
            ).pack(side='left', padx=5)
    
    def create_student_admin_tab(self, notebook):
        """Create student management tab"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Student Management")
        
        tk.Label(
            tab,
            text="Manage Students (Admin)",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Create notebook within tab
        student_notebook = ttk.Notebook(tab)
        student_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # View All Students Tab
        view_tab = tk.Frame(student_notebook, bg='#f0f0f0')
        student_notebook.add(view_tab, text="View All Students")
        
        # Get all students
        students = self.data_handler.get_all_students()
        
        if not students:
            tk.Label(
                view_tab,
                text="No students in the system",
                font=('Arial', 12),
                bg='#f0f0f0'
            ).pack(pady=50)
        else:
            # Create treeview (excel-like) with numbering
            columns = ('No.', 'ID', 'Name', 'Class', 'Age', 'Parent Contact', 'Health')
            tree = ttk.Treeview(view_tab, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=110)
            
            tree.column('Name', width=180)
            tree.column('Parent Contact', width=130)
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Insert students with numbering
            for idx, student in enumerate(students, start=1):
                tree.insert('', 'end', values=(
                    idx,
                    student.get('id', ''),
                    student.get('name', ''),
                    student.get('class', ''),
                    student.get('age', ''),
                    student.get('parent_contact', ''),
                    student.get('health_status', '')
                ))
            
            # Export to Excel button
            export_frame = tk.Frame(view_tab, bg='#f0f0f0')
            export_frame.pack(pady=10)
            
            def export_excel_all():
                success, msg, path = self.admin_manager.export_students_to_excel(None)
                if success:
                    messagebox.showinfo("Exported", f"{msg}\nSaved to: {path}")
                else:
                    messagebox.showerror("Error", msg)
            
            tk.Button(export_frame, text="Export to Excel (All)", bg='#9b59b6', fg='white', command=export_excel_all).pack(side='left', padx=10)
        
        # Add Student Tab (Admin)
        add_tab = tk.Frame(student_notebook, bg='#f0f0f0')
        student_notebook.add(add_tab, text="Add Student")
        
        tk.Label(
            add_tab,
            text="Add New Student (Admin)",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Form frame
        form_frame = tk.Frame(add_tab, bg='#f0f0f0')
        form_frame.pack(pady=10, padx=20)
        
        # Name
        tk.Label(form_frame, text="Full Name:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Class
        tk.Label(form_frame, text="Class/Grade:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(form_frame, textvariable=class_var, 
                                  values=self.data_handler.get_all_classes(), width=27)
        class_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Parent Contact
        tk.Label(form_frame, text="Parent Phone:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        parent_entry = tk.Entry(form_frame, width=30)
        parent_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def add_student_admin():
            name = name_entry.get().strip()
            class_name = class_var.get()
            
            if not name or not class_name:
                messagebox.showwarning("Input Required", "Name and class are required")
                return
            
            success, message = self.student_manager.add_new_student(
                name=name,
                class_name=class_name,
                parent_contact=parent_entry.get()
            )
            
            if success:
                messagebox.showinfo("Success", message)
                name_entry.delete(0, 'end')
                class_var.set('')
                parent_entry.delete(0, 'end')
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(
            add_tab,
            text="Add Student",
            bg='#27ae60',
            fg='white',
            command=add_student_admin,
            width=15
        ).pack(pady=20)
    
    def create_reports_tab(self, notebook):
        """Create reports tab"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Reports")
        
        tk.Label(
            tab,
            text="Generate Reports",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Report options frame
        options_frame = tk.Frame(tab, bg='#f0f0f0')
        options_frame.pack(pady=20)
        
        report_options = [
            ("📊 Attendance Report", self.generate_attendance_report),
            ("👨‍🎓 Student Report", self.generate_student_report),
            ("🏫 Class Report", self.generate_class_report),
            ("👨‍🏫 Employee Report", self.generate_employee_report)
        ]
        
        for i, (text, command) in enumerate(report_options):
            btn = tk.Button(
                options_frame,
                text=text,
                font=('Arial', 12),
                bg='#9b59b6',
                fg='white',
                width=22,
                height=2,
                command=command
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def create_announcements_tab(self, notebook):
        """Admin tab to create and manage announcements"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Announcements")
        
        tk.Label(tab, text="Create Announcement", font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=10)
        form = tk.Frame(tab, bg='#f0f0f0')
        form.pack(pady=5, padx=10)
        
        tk.Label(form, text="Title:", bg='#f0f0f0').grid(row=0, column=0, sticky='w')
        title_var = tk.StringVar()
        tk.Entry(form, textvariable=title_var, width=60).grid(row=0, column=1, pady=5)
        
        tk.Label(form, text="Content:", bg='#f0f0f0').grid(row=1, column=0, sticky='nw')
        content_text = scrolledtext.ScrolledText(form, width=60, height=6)
        content_text.grid(row=1, column=1, pady=5)
        
        tk.Label(form, text="Priority:", bg='#f0f0f0').grid(row=2, column=0, sticky='w')
        priority_var = tk.StringVar(value="Medium")
        ttk.Combobox(form, textvariable=priority_var, values=["High", "Medium", "Low"], width=20).grid(row=2, column=1, sticky='w')
        
        tk.Label(form, text="Visible To:", bg='#f0f0f0').grid(row=3, column=0, sticky='w')
        visible_var = tk.StringVar(value="All")
        visible_combo = ttk.Combobox(form, textvariable=visible_var, values=["All", "Teaching", "Administration", "Support Staff"], width=30)
        visible_combo.grid(row=3, column=1, sticky='w')
        
        def post_announcement():
            title = title_var.get().strip()
            content = content_text.get("1.0", "end-1c").strip()
            priority = priority_var.get()
            visible_to = visible_var.get()
            if not title or not content:
                messagebox.showwarning("Input Required", "Please enter title and content")
                return
            visible_list = ["All"] if visible_to == "All" else [visible_to]
            success, msg = self.admin_manager.create_announcement(title, content, "Admin", 0, priority=priority, visible_to=visible_list)
            if success:
                messagebox.showinfo("Success", msg)
                title_var.set('')
                content_text.delete('1.0', 'end')
                priority_var.set('Medium')
                visible_var.set('All')
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(tab, text="Post Announcement", bg='#3498db', fg='white', command=post_announcement, width=18).pack(pady=10)
        
        # Show existing announcements (list)
        tk.Label(tab, text="Existing Announcements", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=10)
        ann_list = self.data_handler.get_announcements()
        listbox = tk.Listbox(tab, width=100, height=8)
        listbox.pack(pady=5)
        for ann in ann_list:
            listbox.insert('end', f"{ann['id']}: {ann['title']} ({ann['date'][:10]}) [{ann.get('priority','')}]")
    
    def create_settings_tab(self, notebook):
        """Create settings tab with all system settings"""
        tab = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(tab, text="Settings")
        
        # Create notebook for different settings sections
        settings_notebook = ttk.Notebook(tab)
        settings_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ====== PASSWORD SETTINGS TAB ======
        pass_tab = tk.Frame(settings_notebook, bg='#f0f0f0')
        settings_notebook.add(pass_tab, text="Change Password")
        
        tk.Label(
            pass_tab,
            text="Change Admin Password",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Password change form
        pass_frame = tk.Frame(pass_tab, bg='#f0f0f0')
        pass_frame.pack(pady=20, padx=20)
        
        tk.Label(pass_frame, text="Current Password:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        current_entry = tk.Entry(pass_frame, show='*', width=25)
        current_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(pass_frame, text="New Password:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        new_entry = tk.Entry(pass_frame, show='*', width=25)
        new_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(pass_frame, text="Confirm New Password:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        confirm_entry = tk.Entry(pass_frame, show='*', width=25)
        confirm_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def change_admin_password():
            current = current_entry.get()
            new = new_entry.get()
            confirm = confirm_entry.get()
            
            if not current or not new or not confirm:
                messagebox.showwarning("Input Required", "Please fill in all fields")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match")
                return
            
            if len(new) < 6:
                messagebox.showwarning("Weak Password", "Password must be at least 6 characters")
                return
            
            success = self.data_handler.change_password(current, new)
            
            if success:
                messagebox.showinfo("Success", "Admin password changed successfully!")
                current_entry.delete(0, 'end')
                new_entry.delete(0, 'end')
                confirm_entry.delete(0, 'end')
            else:
                messagebox.showerror("Error", "Current password is incorrect")
        
        tk.Button(
            pass_frame,
            text="Change Password",
            bg='#3498db',
            fg='white',
            command=change_admin_password,
            width=15
        ).grid(row=3, column=0, columnspan=2, pady=20)
        
        # ====== SCHOOL SETTINGS TAB ======
        school_tab = tk.Frame(settings_notebook, bg='#f0f0f0')
        settings_notebook.add(school_tab, text="School Settings")
        
        tk.Label(
            school_tab,
            text="School Information",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Load current settings
        settings = self.data_handler.load_json(self.data_handler.settings_file)
        
        school_frame = tk.Frame(school_tab, bg='#f0f0f0')
        school_frame.pack(pady=10, padx=20)
        
        # School Name
        tk.Label(school_frame, text="School Name:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        school_name_var = tk.StringVar(value=settings.get('school_name', 'Greenwood High School'))
        school_name_entry = tk.Entry(school_frame, textvariable=school_name_var, width=30)
        school_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # School Year
        tk.Label(school_frame, text="School Year:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        school_year_var = tk.StringVar(value=settings.get('school_year', '2024-2025'))
        school_year_entry = tk.Entry(school_frame, textvariable=school_year_var, width=30)
        school_year_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Auto Backup
        auto_backup_var = tk.BooleanVar(value=settings.get('auto_backup', True))
        tk.Checkbutton(
            school_frame, 
            text="Enable Auto Backup", 
            variable=auto_backup_var,
            bg='#f0f0f0'
        ).grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        
        # Backup Days
        tk.Label(school_frame, text="Keep Backups (days):", bg='#f0f0f0').grid(row=3, column=0, sticky='w', pady=5)
        backup_days_var = tk.StringVar(value=str(settings.get('backup_days', 7)))
        backup_days_spinbox = tk.Spinbox(school_frame, from_=1, to=30, textvariable=backup_days_var, width=10)
        backup_days_spinbox.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        def save_school_settings():
            new_settings = {
                'admin_password': settings.get('admin_password'),
                'school_name': school_name_var.get(),
                'school_year': school_year_var.get(),
                'auto_backup': auto_backup_var.get(),
                'backup_days': int(backup_days_var.get()),
                'terms': settings.get('terms', ["Term 1", "Term 2", "Term 3"]),
                'subjects': settings.get('subjects', ["Math", "Science", "English", "History", "Geography", "Art", "Music", "PE"])
            }
            
            success = self.data_handler.save_json(self.data_handler.settings_file, new_settings)
            if success:
                messagebox.showinfo("Success", "School settings updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings")
        
        tk.Button(
            school_frame,
            text="Save Settings",
            bg='#27ae60',
            fg='white',
            command=save_school_settings,
            width=15
        ).grid(row=4, column=0, columnspan=2, pady=20)
        
        # ====== ACADEMIC SETTINGS TAB ======
        academic_tab = tk.Frame(settings_notebook, bg='#f0f0f0')
        settings_notebook.add(academic_tab, text="Academic Settings")
        
        tk.Label(
            academic_tab,
            text="Academic Configuration",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Terms Management
        terms_frame = tk.Frame(academic_tab, bg='#f0f0f0')
        terms_frame.pack(pady=10, padx=20)
        
        tk.Label(terms_frame, text="Academic Terms:", font=('Arial', 11, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        terms_listbox = tk.Listbox(terms_frame, height=5, width=30)
        terms_listbox.pack(side='left', padx=(0, 10), pady=5)
        
        # Load current terms
        current_terms = settings.get('terms', ["Term 1", "Term 2", "Term 3"])
        for term in current_terms:
            terms_listbox.insert('end', term)
        
        # Terms controls
        terms_controls = tk.Frame(terms_frame, bg='#f0f0f0')
        terms_controls.pack(side='left')
        
        new_term_var = tk.StringVar()
        tk.Entry(terms_controls, textvariable=new_term_var, width=15).pack(pady=2)
        
        def add_term():
            term = new_term_var.get().strip()
            if term and term not in terms_listbox.get(0, 'end'):
                terms_listbox.insert('end', term)
                new_term_var.set('')
        
        def remove_term():
            selection = terms_listbox.curselection()
            if selection:
                terms_listbox.delete(selection[0])
        
        tk.Button(terms_controls, text="Add Term", command=add_term, width=12).pack(pady=2)
        tk.Button(terms_controls, text="Remove Selected", command=remove_term, width=12).pack(pady=2)
        
        # Subjects Management
        subjects_frame = tk.Frame(academic_tab, bg='#f0f0f0')
        subjects_frame.pack(pady=10, padx=20)
        
        tk.Label(subjects_frame, text="Subjects:", font=('Arial', 11, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        subjects_listbox = tk.Listbox(subjects_frame, height=8, width=30)
        subjects_listbox.pack(side='left', padx=(0, 10), pady=5)
        
        # Load current subjects
        current_subjects = settings.get('subjects', ["Math", "Science", "English", "History", "Geography", "Art", "Music", "PE"])
        for subject in current_subjects:
            subjects_listbox.insert('end', subject)
        
        # Subjects controls
        subjects_controls = tk.Frame(subjects_frame, bg='#f0f0f0')
        subjects_controls.pack(side='left')
        
        new_subject_var = tk.StringVar()
        tk.Entry(subjects_controls, textvariable=new_subject_var, width=15).pack(pady=2)
        
        def add_subject():
            subject = new_subject_var.get().strip()
            if subject and subject not in subjects_listbox.get(0, 'end'):
                subjects_listbox.insert('end', subject)
                new_subject_var.set('')
        
        def remove_subject():
            selection = subjects_listbox.curselection()
            if selection:
                subjects_listbox.delete(selection[0])
        
        tk.Button(subjects_controls, text="Add Subject", command=add_subject, width=12).pack(pady=2)
        tk.Button(subjects_controls, text="Remove Selected", command=remove_subject, width=12).pack(pady=2)
        
        def save_academic_settings():
            new_terms = list(terms_listbox.get(0, 'end'))
            new_subjects = list(subjects_listbox.get(0, 'end'))
            
            settings['terms'] = new_terms
            settings['subjects'] = new_subjects
            
            success = self.data_handler.save_json(self.data_handler.settings_file, settings)
            if success:
                messagebox.showinfo("Success", "Academic settings updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to save academic settings")
        
        tk.Button(
            academic_tab,
            text="Save Academic Settings",
            bg='#27ae60',
            fg='white',
            command=save_academic_settings,
            width=20
        ).pack(pady=20)
        
        # ====== SYSTEM INFO TAB ======
        info_tab = tk.Frame(settings_notebook, bg='#f0f0f0')
        settings_notebook.add(info_tab, text="System Info")
        
        tk.Label(
            info_tab,
            text="System Information",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        info_frame = tk.Frame(info_tab, bg='#f0f0f0')
        info_frame.pack(pady=10, padx=20)
        
        # Get system stats
        school_info = self.data_handler.get_school_info()
        
        info_text = f"School Name: {school_info['name']}\n"
        info_text += f"School Year: {school_info['year']}\n"
        info_text += f"Total Employees: {school_info['total_employees']}\n"
        info_text += f"Total Students: {school_info['total_students']}\n"
        info_text += f"Data Directory: {self.data_handler.data_dir}\n"
        info_text += f"Photos Directory: {self.data_handler.photos_dir}"
        
        tk.Label(
            info_frame,
            text=info_text,
            font=('Arial', 10),
            bg='#f0f0f0',
            justify='left'
        ).pack(anchor='w')
        
        def create_backup():
            success = self.data_handler.create_backup()
            if success:
                messagebox.showinfo("Success", "Backup created successfully!")
            else:
                messagebox.showerror("Error", "Failed to create backup")
        
        tk.Button(
            info_tab,
            text="Create Database Backup",
            bg='#9b59b6',
            fg='white',
            command=create_backup,
            width=20
        ).pack(pady=20)
    
    def logout_admin(self):
        """Logout admin and return to login screen"""
        self.admin_logged_in = False
        self.show_login_screen()
    
    def show_grade_attendance(self):
        """Show attendance for the current grade"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Grade {self.current_grade} Attendance",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get all students in this grade
        students = self.data_handler.get_students_by_class(self.current_grade)
        
        if not students:
            tk.Label(
                self.content_frame,
                text="No students in this grade",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
        else:
            # Create attendance table
            columns = ('Student ID', 'Name', 'Present', 'Absent', 'Late', 'Attendance %')
            tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            tree.column('Name', width=150)
            tree.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Calculate attendance for each student
            for student in students:
                attendance = student.get('attendance_record', {})
                present = attendance.get('present', 0)
                absent = attendance.get('absent', 0)
                late = attendance.get('late', 0)
                total = present + absent + late
                
                if total > 0:
                    percentage = (present / total) * 100
                else:
                    percentage = 0
                
                tree.insert('', 'end', values=(
                    student['id'],
                    student['name'],
                    present,
                    absent,
                    late,
                    f"{percentage:.1f}%"
                ))
            
            # Record attendance for today
            tk.Label(
                self.content_frame,
                text="Record Today's Attendance",
                font=('Arial', 14, 'bold'),
                bg='#f0f0f0'
            ).pack(pady=(20, 10))
            
            record_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
            record_frame.pack(pady=10)
            
            tk.Label(record_frame, text="Select Student:", bg='#f0f0f0').pack(side='left', padx=5)
            student_var = tk.StringVar()
            student_combo = ttk.Combobox(
                record_frame,
                textvariable=student_var,
                values=[f"{s['id']}: {s['name']}" for s in students],
                width=30
            )
            student_combo.pack(side='left', padx=5)
            
            tk.Label(record_frame, text="Status:", bg='#f0f0f0').pack(side='left', padx=5)
            status_var = tk.StringVar(value="present")
            status_combo = ttk.Combobox(
                record_frame,
                textvariable=status_var,
                values=["present", "absent", "late"],
                width=10
            )
            status_combo.pack(side='left', padx=5)
            
            def record_attendance():
                student_selection = student_var.get()
                status = status_var.get()
                
                if not student_selection:
                    messagebox.showwarning("Selection Required", "Please select a student")
                    return
                
                try:
                    student_id = int(student_selection.split(':')[0])
                except:
                    messagebox.showerror("Error", "Invalid student selection")
                    return
                
                success, message = self.student_manager.record_student_attendance(student_id, status)
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.show_grade_attendance()  # Refresh
                else:
                    messagebox.showerror("Error", message)
            
            tk.Button(
                record_frame,
                text="Record",
                bg='#27ae60',
                fg='white',
                command=record_attendance
            ).pack(side='left', padx=10)
        
        tk.Button(
            self.content_frame,
            text="Back to Grade Management",
            command=lambda: self.show_grade_management(self.current_grade)
        ).pack(pady=20)
    
    def show_grade_results(self):
        """Show academic results for the current grade"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Grade {self.current_grade} Academic Results",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get all students in this grade
        students = self.data_handler.get_students_by_class(self.current_grade)
        
        if not students:
            tk.Label(
                self.content_frame,
                text="No students in this grade",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
        else:
            # Create notebook for different terms
            notebook = ttk.Notebook(self.content_frame)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Get available terms
            terms = self.data_handler.get_available_terms()
            
            for term in terms:
                term_tab = tk.Frame(notebook, bg='#f0f0f0')
                notebook.add(term_tab, text=term)
                
                # Get subjects for this term
                subjects = self.data_handler.get_available_subjects()
                
                # Create results table
                columns = ['Student'] + subjects + ['Average']
                tree = ttk.Treeview(term_tab, columns=columns, show='headings', height=15)
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=80)
                
                tree.column('Student', width=150)
                tree.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Add student results
                for student in students:
                    results = student.get('academic_results', {}).get(term, {})
                    row_data = [student['name']]
                    total = 0
                    count = 0
                    
                    for subject in subjects:
                        score = results.get(subject, '')
                        if score != '':
                            row_data.append(str(score))
                            total += score
                            count += 1
                        else:
                            row_data.append('')
                    
                    # Calculate average
                    if count > 0:
                        average = total / count
                        row_data.append(f"{average:.1f}")
                    else:
                        row_data.append('')
                    
                    tree.insert('', 'end', values=row_data)
            
            # Add/edit results frame
            edit_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
            edit_frame.pack(pady=20, padx=20)
            
            tk.Label(edit_frame, text="Update Student Results", font=('Arial', 12, 'bold'), bg='#f0f0f0').grid(row=0, column=0, columnspan=4, pady=10)
            
            tk.Label(edit_frame, text="Student:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
            result_student_var = tk.StringVar()
            result_student_combo = ttk.Combobox(
                edit_frame,
                textvariable=result_student_var,
                values=[f"{s['id']}: {s['name']}" for s in students],
                width=25
            )
            result_student_combo.grid(row=1, column=1, padx=5, pady=5)
            
            tk.Label(edit_frame, text="Term:", bg='#f0f0f0').grid(row=1, column=2, sticky='w', pady=5)
            result_term_var = tk.StringVar()
            result_term_combo = ttk.Combobox(
                edit_frame,
                textvariable=result_term_var,
                values=terms,
                width=10
            )
            result_term_combo.grid(row=1, column=3, padx=5, pady=5)
            
            tk.Label(edit_frame, text="Subject:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
            result_subject_var = tk.StringVar()
            result_subject_combo = ttk.Combobox(
                edit_frame,
                textvariable=result_subject_var,
                values=self.data_handler.get_available_subjects(),
                width=15
            )
            result_subject_combo.grid(row=2, column=1, padx=5, pady=5)
            
            tk.Label(edit_frame, text="Score (0-100):", bg='#f0f0f0').grid(row=2, column=2, sticky='w', pady=5)
            result_score_entry = tk.Entry(edit_frame, width=10)
            result_score_entry.grid(row=2, column=3, padx=5, pady=5)
            
            def update_results():
                student_selection = result_student_var.get()
                term = result_term_var.get()
                subject = result_subject_var.get()
                score_text = result_score_entry.get().strip()
                
                if not student_selection or not term or not subject or not score_text:
                    messagebox.showwarning("Input Required", "Please fill in all fields")
                    return
                
                try:
                    student_id = int(student_selection.split(':')[0])
                    score = int(score_text)
                    
                    if not 0 <= score <= 100:
                        messagebox.showerror("Error", "Score must be between 0 and 100")
                        return
                    
                    success, message = self.student_manager.update_student_results(student_id, term, subject, score)
                    
                    if success:
                        messagebox.showinfo("Success", message)
                        result_score_entry.delete(0, 'end')
                        self.show_grade_results()  # Refresh
                    else:
                        messagebox.showerror("Error", message)
                except ValueError:
                    messagebox.showerror("Error", "Invalid score format")
            
            btn_frame_inner = tk.Frame(edit_frame, bg='#f0f0f0')
            btn_frame_inner.grid(row=3, column=0, columnspan=4, pady=10)
            
            tk.Button(
                btn_frame_inner,
                text="Update Results",
                bg='#3498db',
                fg='white',
                command=update_results
            ).pack(side='left', padx=5)
            
            # NEW: explicit Back button inside academic results upload area
            tk.Button(
                btn_frame_inner,
                text="Back to Grade Management",
                bg='#95a5a6',
                fg='white',
                command=lambda: self.show_grade_management(self.current_grade)
            ).pack(side='left', padx=5)
            
            # Back button frame
            back_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
            back_frame.pack(pady=20)
            
            tk.Button(
                back_frame,
                text="← Back to Grade Management",
                font=('Arial', 10),
                bg='#95a5a6',
                fg='white',
                command=lambda: self.show_grade_management(self.current_grade)
            ).pack(side='left', padx=5)
            
            tk.Button(
                back_frame,
                text="← Back to Menu",
                font=('Arial', 10),
                bg='#3498db',
                fg='white',
                command=self.show_employee_dashboard
            ).pack(side='left', padx=5)
    
    def show_health_records(self):
        """Show health records for the current grade"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Grade {self.current_grade} Health Records",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get all students in this grade
        students = self.data_handler.get_students_by_class(self.current_grade)
        
        if not students:
            tk.Label(
                self.content_frame,
                text="No students in this grade",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
        else:
            # Create health records table
            columns = ('Student ID', 'Name', 'Health Status', 'Allergies', 'Emergency Contact')
            tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            tree.column('Name', width=150)
            tree.column('Allergies', width=200)
            tree.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Add student health records
            for student in students:
                allergies = student.get('allergies', 'None')
                if not allergies:
                    allergies = 'None'
                
                tree.insert('', 'end', values=(
                    student['id'],
                    student['name'],
                    student.get('health_status', 'Unknown'),
                    allergies,
                    student.get('emergency_contact', 'N/A')
                ))
        
        tk.Button(
            self.content_frame,
            text="Back to Grade Management",
            command=lambda: self.show_grade_management(self.current_grade)
        ).pack(pady=20)
    
    def show_photo_management(self):
        """Show photo management for the current grade"""
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Grade {self.current_grade} Photo Management",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get all students in this grade
        students = self.data_handler.get_students_by_class(self.current_grade)
        
        if not students:
            tk.Label(
                self.content_frame,
                text="No students in this grade",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=20)
        else:
            # Create photo grid
            canvas = tk.Canvas(self.content_frame, bg='#f0f0f0')
            scrollbar = tk.Scrollbar(self.content_frame, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Display student photos in a grid
            for i, student in enumerate(students):
                row = i // 4
                col = i % 4
                
                frame = tk.Frame(scrollable_frame, bg='white', relief='solid', borderwidth=1)
                frame.grid(row=row, column=col, padx=10, pady=10)
                
                # Student photo
                photo_path = self.data_handler.get_student_photo(student['id'])
                photo_label = tk.Label(frame, text=student['name'], bg='white', font=('Arial', 9))
                
                if photo_path and os.path.exists(photo_path):
                    try:
                        img = Image.open(photo_path)
                        img.thumbnail((100, 100))
                        photo = ImageTk.PhotoImage(img)
                        photo_label.config(image=photo, compound='top')
                        photo_label.image = photo
                    except:
                        photo_label.config(text=f"{student['name']}\n(No photo)")
                else:
                    photo_label.config(text=f"{student['name']}\n(No photo)")
                
                photo_label.pack(padx=10, pady=10)
                
                # Update photo button
                def update_photo(sid=student['id'], sname=student['name']):
                    filepath = filedialog.askopenfilename(
                        title=f"Select photo for {sname}",
                        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
                    )
                    if filepath:
                        success = self.data_handler.save_student_photo(sid, filepath)
                        if success:
                            messagebox.showinfo("Success", f"Photo updated for {sname}")
                            self.show_photo_management()  # Refresh
                        else:
                            messagebox.showerror("Error", "Failed to update photo")
                
                tk.Button(
                    frame,
                    text="Update Photo",
                    command=update_photo,
                    width=12
                ).pack(pady=(0, 10))
            
            canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            scrollbar.pack(side='right', fill='y')
        
        tk.Button(
            self.content_frame,
            text="Back to Grade Management",
            command=lambda: self.show_grade_management(self.current_grade)
        ).pack(pady=20)
    
    def edit_student_details(self, student_id):
        """Edit student details"""
        # Get student information
        student = self.data_handler.get_student_full_info(student_id)
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Edit Student: {student['name']}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Create edit form
        form_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        form_frame.pack(pady=20, padx=20)
        
        # Name
        tk.Label(form_frame, text="Full Name:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.insert(0, student.get('name', ''))
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Class
        tk.Label(form_frame, text="Class:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        class_var = tk.StringVar(value=student.get('class', ''))
        class_combo = ttk.Combobox(form_frame, textvariable=class_var, 
                                  values=self.data_handler.get_all_classes(), width=27)
        class_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Parent Contact
        tk.Label(form_frame, text="Parent Phone:", bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        parent_entry = tk.Entry(form_frame, width=30)
        parent_entry.insert(0, student.get('parent_contact', ''))
        parent_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Health Status
        tk.Label(form_frame, text="Health Status:", bg='#f0f0f0').grid(row=3, column=0, sticky='w', pady=5)
        health_var = tk.StringVar(value=student.get('health_status', 'Good'))
        health_combo = ttk.Combobox(form_frame, textvariable=health_var, 
                                   values=["Excellent", "Good", "Fair", "Poor"], width=27)
        health_combo.grid(row=3, column=1, padx=10, pady=5)
        
        # Allergies
        tk.Label(form_frame, text="Allergies:", bg='#f0f0f0').grid(row=4, column=0, sticky='w', pady=5)
        allergies_entry = tk.Entry(form_frame, width=30)
        allergies_entry.insert(0, student.get('allergies', ''))
        allergies_entry.grid(row=4, column=1, padx=10, pady=5)
        
        def save_changes():
            updates = {
                'name': name_entry.get().strip(),
                'class': class_var.get(),
                'parent_contact': parent_entry.get(),
                'health_status': health_var.get(),
                'allergies': allergies_entry.get()
            }
            
            # Update student
            success = self.data_handler.update_student(student_id, **updates)
            
            if success:
                messagebox.showinfo("Success", "Student details updated successfully!")
                self.show_grade_students()
            else:
                messagebox.showerror("Error", "Failed to update student details")
        
        tk.Button(
            form_frame,
            text="Save Changes",
            bg='#27ae60',
            fg='white',
            command=save_changes,
            width=15
        ).grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(
            self.content_frame,
            text="Cancel",
            command=self.show_grade_students
        ).pack()
    
    def show_student_results(self, student_id):
        """Show academic results for a specific student"""
        student = self.data_handler.get_student_full_info(student_id)
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Academic Results - {student['name']}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get student results
        results = student.get('academic_results', {})
        
        if not results or all(not term_results for term_results in results.values()):
            tk.Label(
                self.content_frame,
                text="No academic results available for this student",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=50)
        else:
            # Display results by term
            for term, term_results in results.items():
                if term_results:
                    tk.Label(
                        self.content_frame,
                        text=f"{term}:",
                        font=('Arial', 14, 'bold'),
                        bg='#f0f0f0'
                    ).pack(pady=(10, 5), anchor='w')
                    
                    for subject, score in term_results.items():
                        tk.Label(
                            self.content_frame,
                            text=f"  {subject}: {score}/100",
                            font=('Arial', 12),
                            bg='#f0f0f0'
                        ).pack(anchor='w', padx=20)
        
        tk.Button(
            self.content_frame,
            text="Back to Students",
            command=self.show_grade_students
        ).pack(pady=20)
    
    def show_student_attendance(self, student_id):
        """Show attendance for a specific student"""
        student = self.data_handler.get_student_full_info(student_id)
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        self.clear_content_frame()
        
        tk.Label(
            self.content_frame,
            text=f"Attendance - {student['name']}",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(20, 10))
        
        # Get attendance record
        attendance = student.get('attendance_record', {})
        present = attendance.get('present', 0)
        absent = attendance.get('absent', 0)
        late = attendance.get('late', 0)
        total = present + absent + late
        
        if total == 0:
            tk.Label(
                self.content_frame,
                text="No attendance records for this student",
                font=('Arial', 14),
                bg='#f0f0f0'
            ).pack(pady=50)
        else:
            # Calculate percentages
            present_pct = (present / total) * 100 if total > 0 else 0
            absent_pct = (absent / total) * 100 if total > 0 else 0
            late_pct = (late / total) * 100 if total > 0 else 0
            
            # Display attendance summary
            summary_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
            summary_frame.pack(pady=20)
            
            tk.Label(
                summary_frame,
                text=f"Total Days: {total}",
                font=('Arial', 12, 'bold'),
                bg='#f0f0f0'
            ).grid(row=0, column=0, padx=20, pady=5)
            
            tk.Label(
                summary_frame,
                text=f"Present: {present} ({present_pct:.1f}%)",
                font=('Arial', 12),
                bg='#f0f0f0',
                fg='#27ae60'
            ).grid(row=1, column=0, padx=20, pady=5)
            
            tk.Label(
                summary_frame,
                text=f"Absent: {absent} ({absent_pct:.1f}%)",
                font=('Arial', 12),
                bg='#f0f0f0',
                fg='#e74c3c'
            ).grid(row=2, column=0, padx=20, pady=5)
            
            tk.Label(
                summary_frame,
                text=f"Late: {late} ({late_pct:.1f}%)",
                font=('Arial', 12),
                bg='#f0f0f0',
                fg='#f39c12'
            ).grid(row=3, column=0, padx=20, pady=5)
            
            # Attendance rate
            attendance_rate = (present / total) * 100 if total > 0 else 0
            tk.Label(
                summary_frame,
                text=f"Attendance Rate: {attendance_rate:.1f}%",
                font=('Arial', 14, 'bold'),
                bg='#f0f0f0'
            ).grid(row=4, column=0, padx=20, pady=10)
        
        tk.Button(
            self.content_frame,
            text="Back to Students",
            command=self.show_grade_students
        ).pack(pady=20)
    
    # REPORT GENERATION METHODS
    def generate_attendance_report(self):
        """Generate attendance report"""
        # Get date range
        date_range = self.get_date_range_dialog("Generate Attendance Report")
        if not date_range:
            return
        
        start_date, end_date = date_range
        
        # Generate report
        summary = self.report_generator.print_summary_report(start_date, end_date)
        
        # Show report
        self.show_report_dialog("Attendance Report", summary)
    
    def generate_student_report(self):
        """Generate student report"""
        # Get student selection
        students = self.data_handler.get_all_students()
        if not students:
            messagebox.showinfo("No Students", "No students in the system")
            return
        
        student_selection = self.get_selection_dialog(
            "Select Student",
            "Choose a student to generate report for:",
            [f"{s['id']}: {s['name']} ({s['class']})" for s in students]
        )
        
        if not student_selection:
            return
        
        try:
            student_id = int(student_selection.split(':')[0])
        except:
            messagebox.showerror("Error", "Invalid selection")
            return
        
        # Generate report
        filepath, message = self.report_generator.generate_student_report(student_id)
        
        if filepath:
            messagebox.showinfo("Success", f"{message}\n\nReport saved to:\n{filepath}")
        else:
            messagebox.showerror("Error", message)
    
    def generate_class_report(self):
        """Generate class report"""
        # Get class selection
        classes = self.data_handler.get_all_classes()
        if not classes:
            messagebox.showinfo("No Classes", "No classes in the system")
            return
        
        class_selection = self.get_selection_dialog(
            "Select Class",
            "Choose a class to generate report for:",
            classes
        )
        
        if not class_selection:
            return
        
        # Generate report
        filepath, message = self.report_generator.generate_class_report(class_selection)
        
        if filepath:
            messagebox.showinfo("Success", f"{message}\n\nReport saved to:\n{filepath}")
        else:
            messagebox.showerror("Error", message)
    
    def generate_employee_report(self):
        """Generate employee report (with period specification)"""
        # Get employee selection
        employees = self.data_handler.get_all_employees()
        if not employees:
            messagebox.showinfo("No Employees", "No employees in the system")
            return
        
        employee_selection = self.get_selection_dialog(
            "Select Employee",
            "Choose an employee to generate report for:",
            [f"{e['id']}: {e['name']} ({e['department']})" for e in employees]
        )
        
        if not employee_selection:
            return
        
        try:
            employee_id = int(employee_selection.split(':')[0])
        except:
            messagebox.showerror("Error", "Invalid selection")
            return
        
        # Ask for date range
        date_range = self.get_date_range_dialog("Generate Employee Attendance Report")
        if not date_range:
            return
        start_date, end_date = date_range
        
        # Generate report via ReportGenerator
        filepath, message = self.report_generator.generate_employee_report(employee_id, start_date, end_date)
        
        if filepath:
            messagebox.showinfo("Success", f"{message}\n\nReport saved to:\n{filepath}")
        else:
            messagebox.showerror("Error", message)
    
    def show_employee_hours_report(self):
        """Show employee hours report"""
        messagebox.showinfo("Info", "Employee Hours Report feature is not yet implemented")
    
    def show_students_by_class_excel(self):
        """Export students by class to Excel"""
        messagebox.showinfo("Info", "Excel Export feature is not yet implemented")
    
    # HELPER METHODS
    def get_date_range_dialog(self, title):
        """Show dialog to get date range"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter Date Range", font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=(20, 10))
        
        frame = tk.Frame(dialog, bg='#f0f0f0')
        frame.pack(pady=10)
        
        tk.Label(frame, text="Start Date (YYYY-MM-DD):", bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        start_entry = tk.Entry(frame, width=15)
        start_entry.grid(row=0, column=1, padx=5, pady=5)
        start_entry.insert(0, (date.today() - timedelta(days=30)).isoformat())
        
        tk.Label(frame, text="End Date (YYYY-MM-DD):", bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        end_entry = tk.Entry(frame, width=15)
        end_entry.grid(row=1, column=1, padx=5, pady=5)
        end_entry.insert(0, date.today().isoformat())
        
        result = []
        
        def confirm():
            start_date = start_entry.get().strip()
            end_date = end_entry.get().strip()
            
            if not start_date or not end_date:
                messagebox.showwarning("Input Required", "Please enter both dates")
                return
            
            result.append(start_date)
            result.append(end_date)
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Confirm", command=confirm, width=10).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=cancel, width=10).pack(side='left', padx=10)
        
        dialog.wait_window()
        
        if len(result) == 2:
            return tuple(result)
        return None
    
    def get_selection_dialog(self, title, prompt, options):
        """Show dialog to get selection from list"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=prompt, font=('Arial', 12), bg='#f0f0f0').pack(pady=(20, 10))
        
        listbox = tk.Listbox(dialog, height=10, width=40)
        listbox.pack(pady=10, padx=20)
        
        for option in options:
            listbox.insert('end', option)
        
        result = []
        
        def confirm():
            selection = listbox.curselection()
            if selection:
                result.append(listbox.get(selection[0]))
                dialog.destroy()
            else:
                messagebox.showwarning("Selection Required", "Please select an item")
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Select", command=confirm, width=10).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=cancel, width=10).pack(side='left', padx=10)
        
        dialog.wait_window()
        
        return result[0] if result else None
    
    def show_report_dialog(self, title, content):
        """Show report in a dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(dialog, width=70, height=25)
        text_widget.pack(padx=10, pady=10, fill='both', expand=True)
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        
        tk.Button(dialog, text="Close", command=dialog.destroy, width=10).pack(pady=10)