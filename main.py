# main.py - starts Flask API in background and launches Tkinter GUI (single-run)
import threading
import time
import webbrowser
import traceback
import sys
import tkinter as tk
from werkzeug.serving import make_server

# Import the factory that creates the Flask app (we import this at module level)
from api_server import create_app

def run_flask_in_thread(app, host='127.0.0.1', port=5000):
    server = make_server(host, port, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread

def main():
    try:
        print("=" * 50)
        print("School Management System - Starting...")
        print("=" * 50)

        # Create Flask app and run it in background
        app = create_app(static_folder=".", static_index="INDEX.HTML")
        print("Starting local API server at http://127.0.0.1:5000 ...")
        server, server_thread = run_flask_in_thread(app, '127.0.0.1', 5000)
        time.sleep(0.2)  # small delay to allow server to bind

        # Import backend modules here so we get their import-time errors inside try/except
        try:
            from data_handler import DataHandler
            from report_generator import ReportGenerator
            from student_manager import StudentManager
            from admin_manager import AdminManager
            from gui import AttendanceGUI
        except Exception as e:
            print("Failed importing backend modules. Full traceback follows:")
            traceback.print_exc()
            print("\nPlease fix the error above (often a missing dependency or a syntax/runtime error inside one of the modules).")
            raise

        # Initialize backend modules for GUI (they will use same JSON files)
        data_handler = DataHandler()
        report_generator = ReportGenerator(data_handler)
        student_manager = StudentManager(data_handler)
        admin_manager = AdminManager(data_handler, student_manager)

        # Create main Tk window and GUI
        root = tk.Tk()
        root.title("School Management System v2.0")
        root.geometry("1200x700")
        try:
            root.iconbitmap('icon.ico')
        except:
            pass

        app_gui = AttendanceGUI(root, data_handler, report_generator, admin_manager, student_manager)

        print("You can open the SIS web UI at: http://127.0.0.1:5000/sis?role=admin")
        # Uncomment to open automatically:
        # webbrowser.open("http://127.0.0.1:5000/sis?role=admin")

        root.mainloop()

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()