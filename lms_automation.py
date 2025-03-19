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
from selenium_manager import WebDriverManager
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
    
    def run_session(self) -> None:
        """Run a single attendance check session"""
        driver = None
        try:
            self.session_count += 1
            self.logger.info(f"Starting attendance check session #{self.session_count}")
            self.system_tray.update_status("running")
            
            # Initialize webdriver
            driver = self.driver_manager.get_driver()
            if not driver:
                self.logger.error("Failed to initialize WebDriver")
                return
                
            # Login to the LMS
            if not self.login(driver):
                self.logger.error("Login failed, aborting session")
                return
                
            # Navigate to V-Class and get class info
            success, class_count, current_classes = self.navigate_to_vclass(driver)
            if not success or class_count == 0:
                self.logger.warning("No classes found or navigation failed")
                return
                
            # Check each class for attendance opportunities
            attendance_found = False
            for class_index in range(class_count):
                # Navigate to class (classes are indexed from 0)
                try:
                    # Wait for class elements to be visible
                    wait = WebDriverWait(driver, 10)
                    class_elements = wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, 'kt-widget__username')))
                    
                    # Click on the class
                    class_elements[class_index].click()
                    self.logger.info(f"Checking class {class_index + 1}/{class_count}")
                    
                    # Check for attendance section
                    time.sleep(random.uniform(1.5, 3.0))  # Random wait to appear more human-like
                    
                    # Try to find attendance elements
                    try:
                        attendance_elements = driver.find_elements(By.XPATH, "//button[contains(text(), 'Attend')]")
                        if attendance_elements:
                            self.logger.info(f"Found {len(attendance_elements)} attendance buttons")
                            attendance_found = True
                            
                            # Process each attendance button
                            for i, button in enumerate(attendance_elements):
                                try:
                                    class_name = list(current_classes)[class_index] if class_index < len(current_classes) else "Unknown"
                                    self.logger.info(f"Submitting attendance {i+1}/{len(attendance_elements)} for class: {class_name}")
                                    
                                    # Click the attendance button
                                    button.click()
                                    time.sleep(random.uniform(1.0, 2.0))
                                    
                                    # Handle any confirm dialog if it appears
                                    try:
                                        confirm_button = WebDriverWait(driver, 3).until(
                                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'OK')]")))
                                        confirm_button.click()
                                    except (TimeoutException, NoSuchElementException):
                                        # No confirmation dialog found, continue
                                        pass
                                        
                                    # Log successful attendance
                                    self.attendance_logger.log_attendance(class_name)
                                    
                                    # Send success notification
                                    self.email_notifier.send_notification(
                                        f"Attendance Submitted - {class_name}",
                                        f"Successfully submitted attendance for class: {class_name}",
                                        "success"
                                    )
                                except Exception as e:
                                    self.logger.error(f"Error processing attendance button {i+1}: {str(e)}")
                        else:
                            self.logger.info("No attendance buttons found for this class")
                    except Exception as e:
                        self.logger.error(f"Error finding attendance elements: {str(e)}")
                    
                    # Go back to class list
                    driver.back()
                    time.sleep(random.uniform(1.0, 2.0))
                    
                except Exception as e:
                    self.logger.error(f"Error navigating to class {class_index + 1}: {str(e)}")
                    # Try to go back to the class list
                    try:
                        driver.back()
                        time.sleep(1.0)
                    except:
                        pass
            
            if not attendance_found:
                self.logger.info("No attendance opportunities found in any class")
                
            self.logger.info(f"Completed attendance check session #{self.session_count}")
            self.system_tray.update_status("idle")
            
        except UnexpectedAlertPresentException as e:
            self.logger.warning(f"Unexpected alert: {str(e)}")
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass
        except Exception as e:
            self.logger.error(f"Error during attendance session: {str(e)}")
            self.system_tray.update_status("error")
            self.email_notifier.send_notification(
                "Automation Error",
                f"Error during attendance check session #{self.session_count}.\nError: {str(e)}",
                "error"
            )
        finally:
            # Clean up
            if driver:
                self.driver_manager.quit_driver(driver)

    def start_automation(self) -> None:
        """Start the attendance automation process"""
        if self.running:
            self.logger.info("Automation is already running")
            return
            
        self.logger.info("Starting attendance automation")
        self.running = True
        self.system_tray.update_status("running")
        
        # Create and start automation thread
        self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
        
        # Send notification
        self.email_notifier.send_notification(
            "Automation Started",
            "LMS Attendance automation has been started and will check for attendance periodically.",
            "info"
        )
    
    def run_automation(self) -> None:
        """Run the automation process in a loop"""
        try:
            settings = self.config.get_settings()
            interval = int(settings.get("check_interval", 3600))  # Default: 1 hour
            
            while self.running:
                self.run_session()
                self.logger.info(f"Sleeping for {interval} seconds until next check")
                
                # Sleep in smaller increments to allow for clean shutdown
                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Error in automation thread: {str(e)}")
            self.system_tray.update_status("error")
            self.running = False
    
    def run_now(self) -> None:
        """Run a single attendance check session immediately"""
        if not self.running:
            self.logger.info("Running single attendance check")
            threading.Thread(target=self.run_session, daemon=True).start()
        else:
            self.logger.info("Automation is already running, skipping manual run")
    
    def stop_automation(self) -> None:
        """Stop the attendance automation process"""
        if not self.running:
            self.logger.info("Automation is not running")
            return
            
        self.logger.info("Stopping attendance automation")
        self.running = False
        
        if self.automation_thread and self.automation_thread.is_alive():
            self.automation_thread.join(timeout=5)
            
        self.system_tray.update_status("idle")
        
        # Send notification
        self.email_notifier.send_notification(
            "Automation Stopped",
            "LMS Attendance automation has been stopped.",
            "info"
        )

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