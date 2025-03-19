# LMS Attendance Automation
A background tool that automatically marks attendance in LMS (Learning Management System) for students at Thamrin University.

## Features
- **Automatic Attendance Marking:** Checks and marks attendance for all classes.
- **Email Notifications:** Alerts when attendance is marked.
- **System Tray Integration:** Color-coded status icon (Orange: Idle, Green: Running, Red: Error).
- **Low Resource Usage:** Runs silently in the background.

## Quick Start
1. **Download:** Get the latest executable from [Releases](link-to-releases).
2. **Run:** Launch `LMS_Attendance_Automation.exe`.
3. **Configure:** Edit the config file that appears at first run with your credentials.
4. **Done!** The app will now check for attendance opportunities automatically.

## Configuration
Edit `C:\Users\[YourUsername]\lms_automation_config.ini` with:
- Your LMS username and password.
- Email settings for notifications (Gmail requires App Password).
- Check interval (default: 1 hour).

## System Requirements
- Windows 10/11
- Google Chrome browser
- Internet connection

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
