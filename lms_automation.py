import sys
import time
import threading
import random
from typing import Tuple, Set

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException

from config import Config
from logging_utils import Logger
from email_notifier import EmailNotifier
from webdriver_manager import WebDriverManager
from attendance_logger import AttendanceLogger
from system_tray import SystemTrayIcon

class LMSAttendanceAutomation:
    """Main class for LMS attendance automation"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.email_notifier = EmailNotifier(self.config, self.logger)
        self.driver_manager = WebDriverManager(self.logger)
        self.attendance_logger = AttendanceLogger(self.logger)
        self.system_tray = SystemTrayIcon(self.logger, self)
        
        self.url, self.username, self.password = self.config.get_credentials()
        self.session_count = 0
        self.running = False
        self.automation_thread = None
        self.known_classes = set()
        
        # Start system tray
        self.system_tray_thread = threading.Thread(target=self.system_tray.run, daemon=True)
        self.system_tray_thread.start()
    
    def login(self, driver) -> bool:
        """Log into the LMS website"""
        try:
            driver.get(self.url)
            driver.maximize_window()
            
            # Use explicit waits for performance
            wait = WebDriverWait(driver, 10)
            
            # Click sign-in button
            signin_form = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-success")))
            signin_form.click()

            # Enter credentials
            wait.until(EC.element_to_be_clickable((By.ID, "iduser"))).send_keys(self.username)
            wait.until(EC.element_to_be_clickable((By.ID, "idpass"))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_sign_in_form"]/div[4]/button'))).click()
            
            # Wait for successful login
            wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'V-Class')))
            self.logger.info(f"Successfully logged in as {self.username}")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Login failed: {str(e)}")
            self.email_notifier.send_notification(
                "Login Failed", 
                f"Failed to log in to LMS as {self.username}.\nError: {str(e)}", 
                "error"
            )
            return False
    
    def navigate_to_vclass(self, driver) -> Tuple[bool, int, Set[str]]:
        """Navigate to the V-Class section and get class information"""
        try:
            # Add a short wait before clicking V-Class link
            time.sleep(1)
            
            # Try multiple strategies to find V-Class link with a single wait object
            wait = WebDriverWait(driver, 10)
            
            # First try clicking by link text
            try:
                wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'V-Class'))).click()
            except (TimeoutException, NoSuchElementException):
                try:
                    # Try partial link text
                    wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Class'))).click()
                except (TimeoutException, NoSuchElementException):
                    # Try XPATH as last resort
                    wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(text(), 'V-Class')]"))).click()
            
            self.logger.info("Navigated to V-Class section")
            
            # Wait for page to load
            time.sleep(2)
            
            # Get available classes
            class_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'kt-widget__username')))
            
            class_count = len(class_elements)
            self.logger.info(f"Found {class_count} available classes")
            
            # Get class names and check for new classes
            current_classes = set()
            for number, class_element in enumerate(class_elements, start=1):
                class_name = class_element.text[8:]
                current_classes.add(class_name)
                self.logger.info(f"Class {number}: {class_name}")
            
            # Check for new classes
            new_classes = current_classes - self.known_classes
            if new_classes:
                self.logger.info(f"Detected {len(new_classes)} new classes: {', '.join(new_classes)}")
                self.known_classes.update(new_classes)
                
            return True, class_count, current_classes
        except Exception as e:
            self.logger.error(f"Failed to navigate to V-Class: {str(e)}")
            self.email_notifier.send_notification(
                "Navigation Failed", 
                f"Failed to navigate to V-Class section.\nError: {str(e)}", 
                "error"
            )
            # Take a screenshot for debugging
            try:
                import os
                from pathlib import Path
                screenshot_path = os.path.join(Path(__file__).parent, "error_screenshot.png")
                driver.save_screenshot(screenshot_path)
                self.logger.info(f"Error screenshot saved to: {screenshot_path}")
            except Exception:
                pass
            return False, 0, set()
    
    # The rest of the methods (process_attendance, run_session, etc.)
    # [Remaining methods truncated for brevity - copy from original file]

    # Add the test_email_notification method
    def test_email_notification(self) -> None:
        """Send a test email notification"""
        self.logger.info("Sending test email notification...")
        try:
            success = self.email_notifier.send_notification(
                "Test Email", 
                "This is a test email to verify that the notification system is working correctly.\n\n" +
                "If you received this email, your email settings are configured properly.", 
                "info"
            )
            if success:
                self.logger.info("Test email sent successfully")
                self.system_tray.update_status("running")
                # Reset status after 3 seconds
                threading.Timer(3, lambda: self.system_tray.update_status("idle")).start()
            else:
                self.logger.error("Failed to send test email - Check if email is enabled in config")
                self.system_tray.update_status("error")
                # Reset status after 3 seconds
                threading.Timer(3, lambda: self.system_tray.update_status("idle")).start()
        except Exception as e:
            self.logger.error(f"Failed to send test email: {e}")
            self.system_tray.update_status("error")
            # Reset status after 3 seconds
            threading.Timer(3, lambda: self.system_tray.update_status("idle")).start()

    def exit_app(self) -> None:
        """Exit the application"""
        self.logger.info("Exiting application")
        self.stop_automation()
        self.system_tray.stop()
        sys.exit(0)