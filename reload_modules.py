import sys
import importlib

# List modules to reload
modules_to_reload = [
    'selenium_manager',
    'lms_automation',
    'logging_utils'
]

# Reload modules
for module_name in modules_to_reload:
    if module_name in sys.modules:
        print(f"Reloading {module_name}...")
        importlib.reload(sys.modules[module_name])
    else:
        print(f"Module {module_name} not loaded yet.")

print("Module reload complete.")