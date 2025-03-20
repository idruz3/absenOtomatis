import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

class WebDriverManager:
    """Class for managing the WebDriver"""

    def __init__(self, logger):
        self.logger = logger
        self.driver = None

    def setup_driver(self):
        """Initialize and configure the Chrome webdriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('log-level=3')
            chrome_options.add_argument("--headless=new")
            
            # Create unique user data directory
            unique_id = f"{int(time.time())}_{random.randint(10000, 99999)}"
            temp_dir = Path.home() / "temp" / f'chrome_user_data_{unique_id}'
            temp_dir.mkdir(parents=True, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={str(temp_dir)}")

            # Add additional arguments
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver

        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return None

    def close_driver(self):
        """Close the WebDriver safely"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {e}")

class AttendanceLogger:
    """Class for handling attendance logging"""

    def __init__(self, logger):
        self.logger = logger
        self.log_file_path = Path.home() / "attendance_log.txt"
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def is_already_logged_today(self):
        """Check if we've already logged attendance today"""
        if self.log_file_path.exists():
            with open(self.log_file_path, "r") as log_file:
                if any(self.current_date in line for line in log_file):
                    return True
        return False

    def add_session_header(self):
        """Add a session header to the log file"""
        with open(self.log_file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"\n[{timestamp}] Starting attendance check for all classes\n")

    def log_attendance(self, class_index, class_name):
        """Log attendance for a specific class"""
        with open(self.log_file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] Attendance recorded for Class {class_index}, {class_name}\n")

    def log_already_attended(self, class_index):
        """Log that a class was already attended"""
        with open(self.log_file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] Class {class_index} already attended, skipped\n")

class AttendanceAutomation:
    """Class handling the core attendance automation logic"""
    
    def __init__(self, config, logger, email_notifier, whatsapp_notifier):
        self.config = config
        self.logger = logger
        self.email_notifier = email_notifier
        self.whatsapp_notifier = whatsapp_notifier
        self.driver_manager = WebDriverManager(logger)
        self.attendance_logger = AttendanceLogger(logger)
        self.url, self.username, self.password = config.get_credentials()
        self.known_classes = set()

    def login(self, driver):
        """Log into the LMS website"""
        try:
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)
            
            signin_form = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-success")))
            signin_form.click()

            wait.until(EC.element_to_be_clickable((By.ID, "iduser"))).send_keys(self.username)
            wait.until(EC.element_to_be_clickable((By.ID, "idpass"))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="kt_sign_in_form"]/div[4]/button'))).click()
            
            wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'V-Class')))
            self.logger.info(f"Successfully logged in as {self.username}")
            return True

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            self.send_notifications("Login Failed", 
                                 f"Failed to log in as {self.username}\nError: {str(e)}", 
                                 "error")
            return False

    def navigate_to_vclass(self, driver):
        """Navigate to the V-Class section and get class information"""
        try:
            # Add a short wait before clicking V-Class link
            time.sleep(1)
            
            wait = WebDriverWait(driver, 10)
            
            # Try multiple strategies to find V-Class link
            try:
                wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'V-Class'))).click()
            except (TimeoutException, NoSuchElementException):
                try:
                    wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Class'))).click()
                except (TimeoutException, NoSuchElementException):
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
                class_name = class_element.text[8:]  # Remove "Class - " prefix
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
            self.send_notifications(
                "Navigation Failed",
                f"Failed to navigate to V-Class section.\nError: {str(e)}",
                "error"
            )
            return False, 0, set()

    def process_attendance(self, driver, class_count):
        """Check and mark attendance for all available classes"""
        attendance_button_xpath = '//*[@id="kt_content"]/div[2]/div[1]/div/center/button'
        
        # Check if already logged today
        already_logged_today = self.attendance_logger.is_already_logged_today()
        
        # Add session header to log file
        self.attendance_logger.add_session_header()
        
        # Create a single wait object for reuse
        wait = WebDriverWait(driver, 10)
        
        # Track attendance results for notifications
        attendance_results = []
        
        for i in range(1, class_count + 1):
            try:
                # Get class name
                class_name_xpath = f'//*[@id="kt_content"]/div[2]/div[{i}]/div/div/div[1]/div[3]/div[2]/a'
                class_name_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, class_name_xpath)))
                class_name = class_name_elem.text
                self.logger.info(f"Checking attendance for Class {i}: {class_name}")
                
                # Click on class
                class_xpath = f'//*[@id="kt_content"]/div[2]/div[{i}]/div/div/div[2]/div[2]'
                wait.until(EC.element_to_be_clickable((By.XPATH, class_xpath))).click()
                
                try:
                    # Look for attendance button with shorter timeout
                    short_wait = WebDriverWait(driver, 5)
                    attendance_button = short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, attendance_button_xpath)))
                    self.logger.info(f"Attendance button found for {class_name}")
                    
                    # Add random delay before clicking
                    delay_minutes = random.uniform(0.1, 0.3)
                    self.logger.info(f"Waiting {delay_minutes:.1f} minutes before marking attendance...")
                    time.sleep(delay_minutes * 60)
                    
                    try:
                        # Mark attendance
                        attendance_button.click()
                        self.logger.info(f"Successfully marked attendance for {class_name}")
                        
                        # Log the attendance and add to results
                        if not already_logged_today:
                            self.attendance_logger.log_attendance(i, class_name)
                        attendance_results.append(
                            f"✓ Class {i}: {class_name} - Attendance marked successfully")
                    
                    except UnexpectedAlertPresentException:
                        # Handle "already attended" alert
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        if "Anda sudah absen!" in alert_text:
                            self.logger.info(f"Already attended Class {i} ({class_name}), skipping...")
                            self.attendance_logger.log_already_attended(i)
                            attendance_results.append(f"✓ Class {i}: {class_name} - Already attended")
                            alert.accept()
                        else:
                            alert.accept()
                            self.logger.warning(f"Unexpected alert: {alert_text}")
                            attendance_results.append(
                                f"⚠ Class {i}: {class_name} - Unexpected alert: {alert_text}")
                            
                except TimeoutException:
                    self.logger.info(f"No attendance button found for {class_name}")
                    attendance_results.append(f"ℹ Class {i}: {class_name} - No attendance button found")
                
                # Go back to class list
                driver.back()
                
            except Exception as e:
                self.logger.error(f"Error processing class {i}: {str(e)}")
                attendance_results.append(f"✗ Class {i}: Error - {str(e)}")
                self.send_notifications(
                    f"Error Processing Class {i}",
                    f"Error processing class {i}.\nError: {str(e)}",
                    "error"
                )

        # Send notification with attendance results if attendance was marked
        if attendance_results:
            attendance_marked = any("Attendance marked successfully" in result 
                                 or "Already attended" in result 
                                 for result in attendance_results)
            
            if attendance_marked:
                self.send_notifications(
                    "Attendance Results",
                    "Attendance check completed with the following results:\n\n" +
                    "\n".join(attendance_results),
                    "info"
                )
            else:
                self.logger.info("No attendance buttons were clicked, skipping notification")
        
        return True

    def run_session(self):
        """Run a complete attendance checking session"""
        driver = None
        try:
            # Setup driver
            driver = self.driver_manager.setup_driver()
            if driver is None:
                raise Exception("Failed to initialize WebDriver")

            # Login to system
            if not self.login(driver):
                raise Exception("Login failed")
            
            # Navigate to classes and process attendance
            success, class_count, current_classes = self.navigate_to_vclass(driver)
            if success and class_count > 0:
                self.process_attendance(driver, class_count)
            else:
                raise Exception("Failed to get class information")
            
        except Exception as e:
            self.logger.error(f"Session failed: {str(e)}")
            self.send_notifications(
                "Session Failed",
                f"Attendance session failed.\nError: {str(e)}",
                "error"
            )
            raise  # Re-raise the exception for the main loop to handle
            
        finally:
            # Clean up resources
            if driver:
                self.driver_manager.close_driver()

    def send_notifications(self, subject, message, category="info"):
        """Send notifications through configured channels"""
        # Send email notification if enabled
        if self.email_notifier.enabled:
            self.email_notifier.send_notification(subject, message, category)
        
        # Send WhatsApp notification if enabled
        if self.whatsapp_notifier.enabled:
            # Format message for WhatsApp
            whatsapp_message = f"*{subject}*\n\n{message}"
            self.whatsapp_notifier.send_notification(whatsapp_message)