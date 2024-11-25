# LMS Attendance Automation

An automated attendance system for LMS (Learning Management System) using Selenium WebDriver.

## Features

- Automated login to the LMS platform
- Class list retrieval and display
- Automated attendance marking
- Intelligent navigation through class pages
- Error handling and retry mechanisms

## Prerequisites

- Python 3.x
- Chrome/Edge WebDriver
- Selenium
- pwinput

## Installation

```bash
pip install selenium
pip install pwinput
```

## Usage

1. Ensure you have the necessary WebDriver (Chrome/Edge) installed and its path set in the `setup_driver` function.
2. Run the script using Python:
   ```bash
   python src/absen1.py
   ```
3. Follow the prompts to enter your NIM and password.

## Functions

- `setup_driver()`: Configures and returns a WebDriver instance.
- `login(driver, url, username, password)`: Logs into the specified URL with the provided credentials.
- `access_dashboard(driver)`: Navigates to the dashboard and retrieves the username.
- `vClass(driver)`: Accesses the virtual class page.
- `getClass(driver)`: Retrieves and prints the list of classes.
- `selectClass(driver, number)`: Iterates through the list of classes and attempts to click an attendance button.


s