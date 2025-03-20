import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class EmailNotifier:
    """Class for sending email notifications"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.email_settings = config.get_email_settings()
        self.enabled = self.email_settings.get("enabled", "false").lower() == "true"

    def send_notification(self, subject, message, category="info"):
        if not self.enabled:
            self.logger.warning("Email notifications are disabled in config")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_settings["sender_email"]
            msg["To"] = self.email_settings["recipient_email"]
            msg["Subject"] = f"LMS Automation: {subject}"

            email_body = f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            email_body += f"Category: {category.upper()}\n\n"
            email_body += message

            msg.attach(MIMEText(email_body, "plain"))

            with smtplib.SMTP(self.email_settings["smtp_server"], 
                            int(self.email_settings["smtp_port"])) as server:
                server.starttls()
                server.login(self.email_settings["sender_email"], 
                           self.email_settings["sender_password"])
                server.send_message(msg)

            self.logger.info(f"Email notification sent: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False

class WhatsAppNotifier:
    """Class for sending WhatsApp notifications"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.whatsapp_settings = config.get_whatsapp_settings()
        self.enabled = self.whatsapp_settings.get("enabled", "false").lower() == "true"
        self.user_data_dir = Path.home() / "whatsapp_automation" / "persistent_session"

    def _setup_chrome_options(self):
        """Set up Chrome options with proper configuration"""
        options = Options()
        options.add_argument(f"--user-data-dir={str(self.user_data_dir)}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--window-size=1200,800')
        options.add_argument('--log-level=3')
        options.add_argument('--headless')  # Uncomment for headless mode
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        return options

    def send_notification(self, message: str) -> bool:
        """Send WhatsApp notification"""
        if not self.enabled:
            self.logger.warning("WhatsApp notifications are disabled in config")
            return False

        driver = None
        try:
            # Create persistent directory if it doesn't exist
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Using Chrome profile directory: {self.user_data_dir}")

            # Setup Chrome options
            options = self._setup_chrome_options()
            self.logger.info("Chrome options configured")

            # Initialize Chrome driver
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                self.logger.info("Chrome driver initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Chrome driver: {str(e)}")
                return False

            # Load WhatsApp Web
            driver.set_page_load_timeout(30)
            driver.get("https://web.whatsapp.com")
            self.logger.info("WhatsApp Web loaded")

            # First time setup check
            first_time = not (self.user_data_dir / "Default").exists()
            wait_time = 60 if first_time else 20
            
            if first_time:
                self.logger.info("First time setup: Please scan the QR code to log in to WhatsApp Web")
                self.logger.info("This is only required once, future sessions will reuse this login")
            
            # Wait for WhatsApp to load
            try:
                wait = WebDriverWait(driver, wait_time)
                # Wait for the message input box to appear
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
                self.logger.info("WhatsApp Web interface loaded successfully")
            except TimeoutException:
                self.logger.error("Timeout waiting for WhatsApp Web to load")
                return False

            # Use direct URL to open chat
            recipient_number = self.whatsapp_settings["recipient_number"]
            encoded_message = message.replace('\n', '%0A').replace(' ', '%20')
            whatsapp_url = f"https://web.whatsapp.com/send?phone={recipient_number}&text={encoded_message}"
            driver.get(whatsapp_url)

            # Wait for chat to load and send button to appear
            try:
                wait = WebDriverWait(driver, 30)
                send_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]'))
                )
                
                # Small delay to ensure the button is truly clickable
                time.sleep(2)
                
                # Send message
                send_button.click()
                self.logger.info("WhatsApp message sent successfully")
                
                # Wait a moment to ensure the message is sent
                time.sleep(3)
                
                return True
                
            except TimeoutException:
                self.logger.error("Timeout waiting for send button")
                return False

        except Exception as e:
            self.logger.error(f"Failed to send WhatsApp notification: {str(e)}")
            return False

        finally:
            if driver:
                try:
                    driver.quit()
                    self.logger.info("Chrome driver closed successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to close Chrome driver: {str(e)}")