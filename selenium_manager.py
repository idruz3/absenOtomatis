import os
import time
import random
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # This refers to the package

from logging_utils import Logger

import sys

class WebDriverManager:
    """Manages Selenium WebDriver instances"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.driver = None
        self.driver_options = self._create_options()
    
    def _create_options(self) -> Options:
        """Create optimized Chrome options - only called once"""
        chrome_options = Options()
        chrome_options.add_argument('log-level=3')  # Suppress browser logs
        chrome_options.add_argument("--headless=new")  # Run in headless mode
        
        # Add additional arguments to improve stability and performance
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        return chrome_options
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """Initialize Chrome webdriver with previously created options"""
        try:
            self.logger.info("Initializing WebDriver...")
            
            # Create a unique user data directory
            unique_id = f"{int(time.time())}_{random.randint(10000, 99999)}"
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'chrome_user_data_{unique_id}')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Apply unique user directory to existing options
            options = self.driver_options
            options.add_argument(f"--user-data-dir={temp_dir}")
            
            # Get the path to the bundled ChromeDriver
            chromedriver_path = self.get_bundled_chromedriver_path()
            
            if chromedriver_path and os.path.exists(chromedriver_path):
                # Use bundled ChromeDriver
                self.logger.info(f"Using bundled ChromeDriver at: {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Fall back to webdriver_manager
                self.logger.info("Bundled ChromeDriver not found, using webdriver_manager")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            self.logger.info("WebDriver initialized successfully")
            return self.driver
        except Exception as e:
            self.logger.error(f"Error initializing WebDriver: {str(e)}")
            return None
    
    def quit_driver(self, driver=None) -> None:
        """Safely quit the WebDriver instance"""
        try:
            # Use the provided driver or fall back to self.driver
            driver_to_quit = driver if driver else self.driver
            
            if driver_to_quit:
                driver_to_quit.quit()
                self.logger.info("WebDriver closed successfully")
                if driver_to_quit == self.driver:
                    self.driver = None
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {str(e)}")
    
    def get_bundled_chromedriver_path(self):
        """Get the path to the bundled ChromeDriver executable"""
        try:
            if getattr(sys, 'frozen', False):
                # Running in PyInstaller bundle
                base_path = sys._MEIPASS
                driver_dir = os.path.join(base_path, "drivers")
            else:
                # Running in normal Python
                driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers")
                
            # Look for chromedriver file
            for file in os.listdir(driver_dir):
                if file.startswith("chromedriver") or file == "chromedriver.exe":
                    return os.path.join(driver_dir, file)
                    
            self.logger.error(f"No ChromeDriver found in {driver_dir}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding bundled ChromeDriver: {str(e)}")
            return None