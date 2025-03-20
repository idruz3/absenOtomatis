import time
import sys
import logging
import threading
from pathlib import Path
from datetime import datetime

from config import Config
from notifications import EmailNotifier, WhatsAppNotifier
from web_automation import AttendanceAutomation
from gui import SystemTrayIcon

class Logger:
    """Class for handling logging operations"""

    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Configure logging to both file and console"""
        try:
            # Get the executable's directory
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            
            # Create logs directory
            logs_dir = base_path / 'logs'
            logs_dir.mkdir(exist_ok=True)

            # Create log file with date
            log_file = logs_dir / f'automation_{datetime.now().strftime("%Y%m%d")}.log'

            # Configure logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(str(log_file), encoding='utf-8', mode='a'),
                    logging.StreamHandler()
                ]
            )
            return logging.getLogger(__name__)

        except Exception as e:
            # Fallback to basic console logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to initialize file logging: {e}')
            return logger

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

class LMSAutomationController:
    """Main controller class for the LMS automation"""

    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.email_notifier = EmailNotifier(self.config, self.logger)
        self.whatsapp_notifier = WhatsAppNotifier(self.config, self.logger)
        self.automation = AttendanceAutomation(
            self.config, 
            self.logger,
            self.email_notifier,
            self.whatsapp_notifier
        )
        self.system_tray = SystemTrayIcon(self.logger, self)
        
        self.running = False
        self.automation_thread = None
        self.session_count = 0

    def automation_loop(self):
        """Main automation loop"""
        self.running = True
        self.logger.info("Starting attendance automation loop")
        
        while self.running:
            self.run_session()
            
            if self.running:
                wait_time = int(self.config.get_settings().get("check_interval", "3600"))
                self.logger.info(f"Waiting {wait_time//60} minutes before next session...")
                
                start_time = time.time()
                while self.running and (time.time() - start_time) < wait_time:
                    time.sleep(1)
        
        self.logger.info("Automation loop stopped")

    def run_session(self):
        """Run a single automation session"""
        if not self.running:
            return
            
        self.system_tray.update_status("running")
        self.session_count += 1
        self.logger.info(f"Starting Session {self.session_count}")
        
        try:
            self.automation.run_session()
        except Exception as e:
            self.logger.error(f"Session error: {e}")
            self.system_tray.update_status("error")
        finally:
            if self.running:
                self.system_tray.update_status("idle")

    def start_automation(self):
        """Start the automation process"""
        if not self.running:
            self.logger.info("Starting automation")
            self.automation_thread = threading.Thread(target=self.automation_loop)
            self.automation_thread.daemon = True
            self.automation_thread.start()
            self.system_tray.update_status("idle")

    def stop_automation(self):
        """Stop the automation process"""
        if self.running:
            self.logger.info("Stopping automation")
            self.running = False
            if self.automation_thread:
                self.automation_thread.join(timeout=5)
            self.system_tray.update_status("idle")

    def run_now(self):
        """Run a single session immediately"""
        self.logger.info("Running a single session immediately")
        threading.Thread(target=self.run_session, daemon=True).start()

    def test_email_notification(self):
        """Send a test email notification"""
        self.logger.info("Sending test email...")
        success = self.email_notifier.send_notification(
            "Test Email",
            "This is a test email to verify that the notification system is working correctly.",
            "info"
        )
        self.system_tray.update_status("running" if success else "error")
        threading.Timer(3, lambda: self.system_tray.update_status("idle")).start()

    def test_whatsapp_notification(self):
        """Send a test WhatsApp notification"""
        self.logger.info("Sending test WhatsApp message...")
        success = self.whatsapp_notifier.send_notification(
            "This is a test message to verify that the WhatsApp notification system is working correctly."
        )
        self.system_tray.update_status("running" if success else "error")
        threading.Timer(3, lambda: self.system_tray.update_status("idle")).start()

    def exit_app(self):
        """Exit the application"""
        self.logger.info("Exiting application")
        self.stop_automation()
        self.system_tray.stop()
        sys.exit(0)

def main():
    """Main entry point of the application"""
    controller = LMSAutomationController()
    
    # Start system tray in a separate thread
    tray_thread = threading.Thread(target=controller.system_tray.run, daemon=True)
    tray_thread.start()
    
    # Start automation
    controller.start_automation()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.exit_app()

if __name__ == "__main__":
    main()