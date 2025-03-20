import threading
import pystray
from PIL import Image, ImageDraw
from datetime import datetime

class SystemTrayIcon:
    """Class for managing the system tray icon"""

    def __init__(self, logger, app_controller):
        self.logger = logger
        self.app_controller = app_controller
        self.icon = None
        self.status = "idle"
        self.last_status_change = datetime.now()

    def create_image(self, width, height):
        """Create an image for the system tray icon based on current status"""
        image = Image.new('RGB', (width, height), color=(0, 0, 0))
        dc = ImageDraw.Draw(image)

        colors = {
            "idle": (255, 165, 0),    # Orange
            "running": (0, 255, 0),    # Green
            "error": (255, 0, 0)       # Red
        }
        
        dc.ellipse([(0, 0), (width, height)], fill=colors.get(self.status, colors["idle"]))
        return image

    def update_status(self, status):
        """Update the status of the system tray icon"""
        if status in ["idle", "running", "error"]:
            self.status = status
            self.last_status_change = datetime.now()
            if self.icon:
                self.icon.icon = self.create_image(64, 64)
                self.icon.update_menu()

    def get_status_text(self):
        """Get the current status text for the menu"""
        timestamp = self.last_status_change.strftime("%H:%M:%S")
        return f"Status: {self.status.upper()} (since {timestamp})"

    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            pystray.MenuItem(
                lambda text: self.get_status_text(),
                lambda: None,
                enabled=False
            ),
            pystray.MenuItem(
                "Start Automation",
                lambda: self.app_controller.start_automation(),
                enabled=lambda item: self.status != "running"
            ),
            pystray.MenuItem(
                "Stop Automation",
                lambda: self.app_controller.stop_automation(),
                enabled=lambda item: self.status == "running"
            ),
            pystray.MenuItem(
                "Run Now",
                lambda: self.app_controller.run_now(),
                enabled=lambda item: self.status != "running"
            ),
            pystray.MenuItem(
                "Test Email",
                lambda: self.app_controller.test_email_notification()
            ),
            pystray.MenuItem(
                "Test WhatsApp",
                lambda: self.app_controller.test_whatsapp_notification()
            ),
            pystray.MenuItem(
                "Open Logs",
                self.open_logs
            ),
            pystray.MenuItem(
                "Exit",
                lambda: self.app_controller.exit_app()
            )
        )

    def open_logs(self):
        """Open the logs directory"""
        try:
            from pathlib import Path
            import sys
            import webbrowser
            
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            logs_dir = base_path / 'logs'
            logs_dir.mkdir(exist_ok=True)
            webbrowser.open(str(logs_dir))
        except Exception as e:
            self.logger.error(f"Failed to open logs directory: {e}")

    def run(self):
        """Run the system tray icon"""
        self.icon = pystray.Icon(
            "lms_automation",
            self.create_image(64, 64),
            "LMS Attendance Automation",
            self.create_menu()
        )
        self.icon.run()

    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()
            import threading
import pystray
import webbrowser
from PIL import Image, ImageDraw
from datetime import datetime
from pathlib import Path
import sys
import json

class SystemTrayIcon:
    """Class for managing the system tray icon"""

    def __init__(self, logger, app_controller):
        self.logger = logger
        self.app_controller = app_controller
        self.icon = None
        self.status = "idle"
        self.last_status_change = datetime.now()
        self.tooltip_text = "LMS Attendance Automation"
        self.status_messages = {
            "idle": "System is ready",
            "running": "Processing attendance",
            "error": "Error occurred",
            "checking": "Checking classes",
            "waiting": "Waiting for next session"
        }
        self.last_error = None

    def create_image(self, width, height):
        """Create an image for the system tray icon based on current status"""
        image = Image.new('RGB', (width, height), color=(0, 0, 0))
        dc = ImageDraw.Draw(image)

        # Status colors
        colors = {
            "idle": (255, 165, 0),     # Orange
            "running": (0, 255, 0),     # Green
            "error": (255, 0, 0),       # Red
            "checking": (0, 191, 255),  # Deep Sky Blue
            "waiting": (147, 112, 219)  # Medium Purple
        }

        # Draw the status circle
        dc.ellipse([(0, 0), (width, height)], 
                  fill=colors.get(self.status, colors["idle"]))

        # Add a border for better visibility
        dc.ellipse([(0, 0), (width, height)], 
                  outline=(255, 255, 255), width=2)

        return image

    def update_status(self, status, error_message=None):
        """Update the status of the system tray icon"""
        if status in self.status_messages:
            old_status = self.status
            self.status = status
            self.last_status_change = datetime.now()
            self.last_error = error_message if status == "error" else None

            # Update icon and tooltip
            if self.icon:
                self.icon.icon = self.create_image(64, 64)
                self.icon.title = f"{self.tooltip_text}\n{self.get_status_text()}"
                self.icon.update_menu()

            # Log status change
            self.logger.info(f"Status changed: {old_status} -> {status}")
            if error_message:
                self.logger.error(f"Error details: {error_message}")

    def get_status_text(self):
        """Get the current status text for the menu"""
        timestamp = self.last_status_change.strftime("%H:%M:%S")
        status_msg = self.status_messages.get(self.status, "Unknown status")
        
        if self.last_error and self.status == "error":
            return f"Status: {status_msg} (since {timestamp})\nError: {self.last_error}"
        return f"Status: {status_msg} (since {timestamp})"

    def save_session_info(self):
        """Save current session information"""
        try:
            session_info = {
                "last_run": datetime.now().isoformat(),
                "status": self.status,
                "last_error": self.last_error
            }
            
            session_file = Path.home() / ".lms_automation" / "session.json"
            session_file.parent.mkdir(exist_ok=True)
            
            with open(session_file, 'w') as f:
                json.dump(session_info, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save session info: {e}")

    def load_session_info(self):
        """Load previous session information"""
        try:
            session_file = Path.home() / ".lms_automation" / "session.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_info = json.load(f)
                    
                self.logger.info(f"Loaded previous session info: {session_info}")
                return session_info
        except Exception as e:
            self.logger.error(f"Failed to load session info: {e}")
        return None

    def create_menu(self):
        """Create the system tray menu with all options"""
        return pystray.Menu(
            pystray.MenuItem(
                lambda text: self.get_status_text(),
                lambda: None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Start Automation",
                lambda: self.app_controller.start_automation(),
                enabled=lambda item: self.status not in ["running", "checking"]
            ),
            pystray.MenuItem(
                "Stop Automation",
                lambda: self.app_controller.stop_automation(),
                enabled=lambda item: self.status in ["running", "checking", "waiting"]
            ),
            pystray.MenuItem(
                "Run Now",
                lambda: self.app_controller.run_now(),
                enabled=lambda item: self.status not in ["running", "checking"]
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Test Notifications",
                pystray.Menu(
                    pystray.MenuItem(
                        "Test Email",
                        lambda: self.app_controller.test_email_notification()
                    ),
                    pystray.MenuItem(
                        "Test WhatsApp",
                        lambda: self.app_controller.test_whatsapp_notification()
                    )
                )
            ),
            pystray.MenuItem(
                "Tools",
                pystray.Menu(
                    pystray.MenuItem(
                        "Open Logs",
                        self.open_logs
                    ),
                    pystray.MenuItem(
                        "Open Config",
                        self.open_config
                    ),
                    pystray.MenuItem(
                        "Clear Session Data",
                        self.clear_session_data
                    )
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit",
                lambda: self.app_controller.exit_app()
            )
        )

    def open_logs(self):
        """Open the logs directory"""
        try:
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
            logs_dir = base_path / 'logs'
            logs_dir.mkdir(exist_ok=True)
            
            # Open the most recent log file if it exists
            log_files = list(logs_dir.glob('automation_*.log'))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                webbrowser.open(str(latest_log))
            else:
                webbrowser.open(str(logs_dir))
        except Exception as e:
            self.logger.error(f"Failed to open logs: {e}")
            self.update_status("error", f"Failed to open logs: {e}")

    def open_config(self):
        """Open the configuration file"""
        try:
            config_file = Path.home() / "lms_automation_config.ini"
            if config_file.exists():
                webbrowser.open(str(config_file))
            else:
                self.logger.error("Configuration file not found")
                self.update_status("error", "Configuration file not found")
        except Exception as e:
            self.logger.error(f"Failed to open config: {e}")
            self.update_status("error", f"Failed to open config: {e}")

    def clear_session_data(self):
        """Clear all session-related data"""
        try:
            session_dir = Path.home() / ".lms_automation"
            if session_dir.exists():
                for file in session_dir.glob("*"):
                    file.unlink()
                session_dir.rmdir()
            self.logger.info("Session data cleared successfully")
            self.update_status("idle")
        except Exception as e:
            self.logger.error(f"Failed to clear session data: {e}")
            self.update_status("error", f"Failed to clear session data: {e}")

    def run(self):
        """Run the system tray icon"""
        # Load previous session info
        session_info = self.load_session_info()
        if session_info:
            self.status = session_info.get("status", "idle")
            self.last_error = session_info.get("last_error")

        # Create and run the icon
        self.icon = pystray.Icon(
            "lms_automation",
            self.create_image(64, 64),
            self.tooltip_text,
            self.create_menu()
        )

        # Update initial status
        self.icon.title = f"{self.tooltip_text}\n{self.get_status_text()}"
        
        try:
            self.icon.run()
        except Exception as e:
            self.logger.error(f"System tray icon error: {e}")
            raise

    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            try:
                # Save session info before stopping
                self.save_session_info()
                self.icon.stop()
            except Exception as e:
                self.logger.error(f"Error stopping system tray icon: {e}")