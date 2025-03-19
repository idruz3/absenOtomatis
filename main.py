import time
import sys
from lms_automation import LMSAttendanceAutomation

def main():
    """Main function to initialize and run the attendance automation"""
    # Create and start the automation
    automation = LMSAttendanceAutomation()
    automation.start_automation()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        automation.exit_app()

if __name__ == "__main__":
    main()