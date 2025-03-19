import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

from logging_utils import Logger

class SystemTrayIcon:
    """Class for managing the system tray icon"""
    
    def __init__(self, logger: Logger, app_controller):
        self.logger = logger
        self.app_controller = app_controller
        self.icon = None
        self.status = "idle"  # idle, running, error
        self.last_status_change = datetime.now()
    
    def create_image(self, width: int, height: int) -> Image.Image:
        """Create an image for the system tray icon based on current status"""
        image = Image.new('RGB', (width, height), color=(0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw different colored circles based on status
        if self.status == "idle":
            dc.ellipse([(0, 0), (width, height)], fill=(255, 165, 0))  # Orange
        elif self.status == "running":
            dc.ellipse([(0, 0), (width, height)], fill=(0, 255, 0))  # Green
        else:  # error
            dc.ellipse([(0, 0), (width, height)], fill=(255, 0, 0))  # Red
            
        return image
    
    def update_status(self, status: str) -> None:
        """Update the status of the system tray icon"""
        if status in ["idle", "running", "error"]:
            self.status = status
            self.last_status_change = datetime.now()
            if self.icon:
                self.icon.icon = self.create_image(64, 64)
                self.icon.update_menu()
    
    def get_status_text(self) -> str:
        """Get the current status text for the menu"""
        timestamp = self.last_status_change.strftime("%H:%M:%S")
        return f"Status: {self.status.upper()} (since {timestamp})"
    
    def create_menu(self) -> pystray.Menu:
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
                "Open Logs",
                self.open_logs
            ),
            pystray.MenuItem(
                "Exit",
                lambda: self.app_controller.exit_app()
            )
        )
    
    def open_logs(self) -> None:
        """Open the logs directory"""
        try:
            base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent
            logs_dir = base_path / 'logs'
            logs_dir.mkdir(exist_ok=True)
            
            # Open the logs directory in file explorer
            webbrowser.open(str(logs_dir))
        except Exception as e:
            self.logger.error(f"Failed to open logs directory: {e}")
    
    def run(self) -> None:
        """Run the system tray icon"""
        self.icon = pystray.Icon(
            "lms_automation",
            self.create_image(64, 64),
            "LMS Attendance Automation",
            self.create_menu()
        )
        self.icon.run()
    
    def stop(self) -> None:
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()