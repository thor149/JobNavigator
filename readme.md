# README.md

## OnCampus Job Scraper

### Introduction
This is a Python script that automates the process of scraping job information from the Birla Institute of Technology OnCampus job portal and notifies users about new job postings via email.

### Requirements
- Python 3.x
- Chrome browser installed
- ChromeDriver (compatible with your Chrome version) in the system PATH
- MongoDB server

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/thor149/JobNavigator.git
   cd JobNavigator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MongoDB:
   - Install and run MongoDB server.
   - Create a database named "OnCampusDB."

4. Configure the `config.json` file:
   - Replace the placeholder values in `config.json` with your actual credentials.

### Usage

#### Running the Script
```bash
python main.py
```

This will execute the script, which logs into the OnCampus portal, scrapes job information, and sends email notifications for new job postings.

#### Scheduled Execution
If you want the script to run continuously and check for new jobs every hour, uncomment the following lines in `main.py`:
```python
# web_automation_instance = WebAutomation("config.json")
# run_all_day_instance = RunAllDay(web_automation_instance)
# run_all_day_instance.run_all_day()
```

And then run:
```bash
python main.py
```

### Configuration

#### `config.json`

- `"username"`: Your OnCampus username.
- `"password"`: Your OnCampus password.
- `"usermongo"`: Your MongoDB username.
- `"passmongo"`: Your MongoDB password.
- `"urlmongo"`: Your MongoDB connection URL.
- `"sender"`: Your email address (used to send notifications).
- `"authkey"`: Your email authentication key.

### Components

#### `main.py`
- The main script that orchestrates the entire process.
- Uses classes for database management (`DatabaseManager`), web scraping (`WebScraper`), email management (`EmailManager`), and overall automation (`WebAutomation`).

#### `config.json`
- Configuration file containing sensitive information and settings.

### Troubleshooting

- If you encounter issues, make sure you have installed the required dependencies and configured the `config.json` file correctly.

### Disclaimer

This script is provided as-is, and the developers are not responsible for any misuse or unintended consequences resulting from its use. Use it responsibly and adhere to the terms and conditions of the Birla Institute of Technology, Training & Placement portal.
