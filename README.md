LMS Attendance Automation is a Python-based application designed to automate the process of marking attendance in an LMS (Learning Management System). The application uses Selenium WebDriver to interact with the LMS website and can send notifications via email and WhatsApp.

## Features

- Automates attendance marking in LMS
- Sends email and WhatsApp notifications
- Configurable through an INI file
- Runs as a system tray application
- Logs activities for auditing and debugging

## Installation

### Prerequisites

- Python 3.6+
- Google Chrome
- ChromeDriver
- Required Python packages (see \`requirements.txt\`)

### Clone the repository

\`\`\`bash
git clone https://github.com/idruz3/absenOtomatis.git
cd absenOtomatis
\`\`\`

### Install dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Create an icon (optional)

If you don't have an icon, you can create a simple one:

\`\`\`bash
python create_icon.py
\`\`\`

## Configuration

Before running the application, you need to configure your credentials and settings. The application uses an INI file for configuration.

1. Run the application for the first time to generate the config file:

\`\`\`bash
python main.py
\`\`\`

2. Edit the \`lms_automation_config.ini\` file located in your home directory:

\`\`\`ini
[Credentials]
url = https://lms.thamrin.ac.id/
username = your_username
password = your_password

[Email]
enabled = false
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = your_email@gmail.com
sender_password = your_email_password
recipient_email = recipient_email@gmail.com

[WhatsApp]
enabled = false
recipient_number = your_phone_number  # Include country code without +

[Settings]
check_interval = 3600  # 1 hour in seconds
notification_level = all  # all, errors, none
\`\`\`

## Usage

### Running the Application

To run the application:

\`\`\`bash
python main.py
\`\`\`

The application will appear in your system tray. You can control it using the tray icon menu.

### Compiling to an Executable

You can compile the application to an executable using PyInstaller:

1. Install PyInstaller:

\`\`\`bash
pip install pyinstaller
\`\`\`

2. Create the executable:

\`\`\`bash
pyinstaller --clean lms_automation.spec
\`\`\`

The executable will be located in the \`dist\` directory.

### Creating an Installer

You can create an installer using Inno Setup:

1. Download and install Inno Setup from [here](https://jrsoftware.org/isdl.php).
2. Open the \`installer.iss\` script in Inno Setup Compiler.
3. Click Compile to create the installer.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
" > README.md
