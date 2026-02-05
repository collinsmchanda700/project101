# diag_imports.py
import traceback

print("=== Testing admin_manager import ===")
try:
    import admin_manager
    print("admin_manager imported OK. Public names:", [n for n in dir(admin_manager) if not n.startswith('_')])
except Exception:
    print("Import admin_manager failed. Traceback follows:")
    traceback.print_exc()

print("\n=== Testing report_generator import ===")
try:
    import report_generator
    print("report_generator imported OK. Public names:", [n for n in dir(report_generator) if not n.startswith('_')])
except Exception:
    print("Import report_generator failed. Traceback follows:")
    traceback.print_exc()