import os
from datetime import datetime
from logging_utils import Logger

class AttendanceLogger:
    """Class for handling attendance logging"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.log_file_path = "attendance_log.txt"
        self.current_date = datetime.now().strftime("%Y-%m-%d")
    
    def is_already_logged_today(self) -> bool:
        """Check if we've already logged attendance today"""
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, "r") as log_file:
                if any(self.current_date in line for line in log_file):
                    self.logger.info(f"Logs for {self.current_date} already exist. Will check attendance but skip logging.")
                    return True
        return False
    
    def add_session_header(self) -> None:
        """Add a session header to the log file"""
        with open(self.log_file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n[{timestamp}] Starting attendance check for all classes\n")
    
    def log_attendance(self, class_index: int, class_name: str) -> None:
        """Log attendance for a specific class"""
        with open(self.log_file_path, "a") as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + 
                          f"Attendance recorded for Class {class_index}, {class_name}\n")
    
    def log_already_attended(self, class_index: int) -> None:
        """Log that a class was already attended"""
        with open(self.log_file_path, "a") as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " +
                          f"Class {class_index} already attended, skipped\n")