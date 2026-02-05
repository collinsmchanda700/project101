# Simple Flask API to serve the INDEX.HTML SIS frontend and expose endpoints
# that the frontend will call. Uses the same JSON-backed DataHandler.
from flask import Flask, jsonify, request, send_from_directory, send_file, abort
import os
from io import BytesIO
import base64
from werkzeug.utils import secure_filename

def create_app(data_handler=None, static_folder=".", static_index="INDEX.HTML"):
    # Import backend classes here to avoid import-time circular dependencies
    from data_handler import DataHandler
    from student_manager import StudentManager
    from admin_manager import AdminManager
    from report_generator import ReportGenerator

    app = Flask(__name__, static_folder=static_folder)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for uploads

    # Use provided DataHandler instance if given (so GUI and API can share same instance),
    # otherwise create one locally.
    if data_handler is None:
        data_handler = DataHandler()
    student_manager = StudentManager(data_handler)
    admin_manager = AdminManager(data_handler, student_manager)
    report_generator = ReportGenerator(data_handler)

    # Serve the front-end index page
    @app.route("/sis")
    def serve_sis_index():
        return send_from_directory(static_folder, static_index)

    # Serve photos (student/employee photos saved in data/photos)
    @app.route("/photos/<path:filename>")
    def serve_photos(filename):
        photos_dir = data_handler.photos_dir
        safe = os.path.normpath(os.path.join(photos_dir, filename))
        if os.path.exists(safe):
            return send_file(safe)
        abort(404)

    # --- API endpoints ---

    @app.route("/api/classes", methods=["GET"])
    def api_get_classes():
        classes = data_handler.get_all_classes()
        return jsonify({"success": True, "classes": classes})

    @app.route("/api/students", methods=["GET"])
    def api_get_students():
        class_name = request.args.get("class")  # expects e.g. "Grade 10"
        if class_name:
            students = data_handler.get_students_by_class(class_name)
        else:
            students = data_handler.get_all_students()
        return jsonify({"success": True, "students": students})

    @app.route("/api/students/<int:student_id>", methods=["GET"])
    def api_get_student(student_id):
        student = data_handler.get_student_full_info(student_id)
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
        return jsonify({"success": True, "student": student})

    @app.route("/api/students", methods=["POST"])
    def api_create_student():
        payload = request.get_json() or {}
        name = payload.get("name")
        class_name = payload.get("class")
        if not name or not class_name:
            return jsonify({"success": False, "message": "name and class are required"}), 400
        ok, msg = student_manager.add_new_student(
            name=name,
            class_name=class_name,
            parent_contact=payload.get("parent_contact", ""),
            parent_email=payload.get("parent_email", ""),
            dob=payload.get("dob", ""),
            address=payload.get("address", ""),
            health_status=payload.get("health_status", "Good"),
            allergies=payload.get("allergies", ""),
            emergency_contact=payload.get("emergency_contact", "")
        )
        if ok:
            return jsonify({"success": True, "message": msg})
        return jsonify({"success": False, "message": msg}), 400

    @app.route("/api/students/<int:student_id>", methods=["PUT"])
    def api_update_student(student_id):
        payload = request.get_json() or {}
        ok = data_handler.update_student(student_id, **payload)
        if ok:
            return jsonify({"success": True})
        return jsonify({"success": False}), 400

    @app.route("/api/students/<int:student_id>", methods=["DELETE"])
    def api_delete_student(student_id):
        ok = data_handler.remove_student(student_id)
        if ok:
            return jsonify({"success": True})
        return jsonify({"success": False}), 400

    @app.route("/api/students/search", methods=["GET"])
    def api_search_students():
        q = (request.args.get("q") or "").strip().lower()
        if not q:
            return jsonify({"success": True, "students": []})
        all_students = data_handler.get_all_students()
        found = [s for s in all_students if q in s.get("name", "").lower()]
        return jsonify({"success": True, "students": found})

    @app.route("/api/import/students", methods=["POST"])
    def api_import_students():
        payload = request.get_json()
        if not isinstance(payload, list):
            return jsonify({"success": False, "message": "Expected an array of students"}), 400
        base = data_handler.load_json(data_handler.students_file)
        next_id = max([s.get("id", 0) for s in base.get("students", [])], default=0)
        new_list = []
        for s in payload:
            # Accept either 'fullName'/'grade' (frontend) or 'name'/'class' (API style)
            fullname = s.get("fullName") or s.get("name")
            grade_raw = s.get("grade") or (s.get("class") and s.get("class").replace("Grade ", ""))
            if not fullname or not grade_raw:
                return jsonify({"success": False, "message": "Each student must have fullName (or name) and grade (or class)"}), 400
            next_id += 1
            new_list.append({
                "id": next_id,
                "name": fullname,
                "class": f"Grade {grade_raw}",
                "parent_contact": s.get("parentPhone", s.get("parent_contact", "")),
                "parent_email": s.get("parentEmail", s.get("parent_email", "")),
                "dob": s.get("dob", ""),
                "age": data_handler.calculate_age(s.get("dob", "")) if s.get("dob") else 0,
                "address": s.get("address", ""),
                "health_status": s.get("healthStatus", "Good"),
                "allergies": s.get("allergies", ""),
                "emergency_contact": s.get("emergencyContact", ""),
                "enrollment_date": s.get("enrollmentDate", ""),
                "photo": None,
                "academic_results": {},
                "attendance_record": {"present": 0, "absent": 0, "late": 0},
                "monthly_attendance": {},
                "term_attendance": {}
            })
        base["students"] = new_list
        ok = data_handler.save_json(data_handler.students_file, base)
        if ok:
            return jsonify({"success": True})
        return jsonify({"success": False}), 500

    @app.route("/api/export/students", methods=["GET"])
    def api_export_students():
        class_filter = request.args.get("class")
        students = data_handler.get_all_students()
        if class_filter:
            students = [s for s in students if s.get("class") == class_filter]
        return jsonify({"success": True, "students": students})

    @app.route("/api/students/<int:student_id>/photo", methods=["POST"])
    def api_upload_photo(student_id):
        payload = request.get_json() or {}
        image_b64 = payload.get("image_base64")
        if not image_b64:
            return jsonify({"success": False, "message": "image_base64 required"}), 400
        try:
            filename = data_handler.save_student_photo_from_base64(student_id, image_b64)
            if filename:
                return jsonify({"success": True, "photo_url": f"/photos/{filename}"})
            return jsonify({"success": False, "message": "Failed to save photo"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @app.route("/api/students/<int:student_id>/term_attendance", methods=["POST"])
    def api_term_attendance(student_id):
        payload = request.get_json() or {}
        term_key = payload.get("term_key")
        present_days = payload.get("present_days")
        if not term_key or present_days is None:
            return jsonify({"success": False, "message": "term_key and present_days required"}), 400
        ok = data_handler.save_student_term_attendance(student_id, term_key, int(present_days))
        if ok:
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Failed to save term attendance"}), 400

    @app.route("/api/report/student/<int:student_id>", methods=["GET"])
    def api_student_report(student_id):
        filepath, message = report_generator.generate_student_report(student_id)
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({"success": False, "message": message}), 400

    @app.route("/api/employee/<int:employee_id>/context", methods=["GET"])
    def api_employee_context(employee_id):
        emp = admin_manager.get_employee_full_info(employee_id)
        if not emp:
            return jsonify({"success": False, "message": "Employee not found"}), 404
        return jsonify({"success": True, "employee": {
            "id": emp.get("id"),
            "name": emp.get("name"),
            "department": emp.get("department"),
            "assigned_grades": emp.get("assigned_grades", [])
        }})

    @app.route("/api/stats", methods=["GET"])
    def api_stats():
        school_info = data_handler.get_school_info()
        # include terms and term defaults to help frontend
        settings = data_handler.load_json(data_handler.settings_file)
        return jsonify({"success": True, "school_info": school_info, "terms": settings.get("terms", []), "term_days_default": settings.get("term_days_default", 60)})

    return app