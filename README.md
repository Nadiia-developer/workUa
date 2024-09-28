# Resume Parsing Telegram Bot

This project is a Telegram bot that assists users in finding resumes from popular job website.

## Features
- User-friendly interaction with Telegram bot for finding candidates
- Fetches resumes from job website using web scraping Selenium

### Prerequisites
- Python 3.8 or higher
- Telegram Bot API Token, you can get one from [BotFather](https://t.me/botfather)
- Google Chrome and ChromeDriver (for web scraping using Selenium)

## Setup

1. Clone the repository or download the files
- Clone project from [GitHub](https://github.com/Nadiia-developer/workUa.git)
- git clone https://github.com/Nadiia-developer/workUa.git
2. Create a virtual environment
- python -m venv venv
- On Mac: source venv/bin/activate 
- On Windows: venv\Scripts\activate
3. Install dependencies:
```bash 
pip install -r requirements.txt
```
4. Download the ChromeDriver binary for your platform under the downloads section of this site [ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads)
5. Add your Telegram bot token to 
`telegram_work_bot.py`:
```python
# In telegram_work_bot.py, replace 'YOUR_BOT_TOKEN' with your actual bot token
application = Application.builder().token("YOUR_BOT_TOKEN").build()
```
6. Update the path to ChromeDriver in `telegram_work_bot.py`:
```python
service = Service("path/to/chromedriver")
```

## Usage
1. Start the bot by running the `telegram_work_bot.py` script:
```bash
telegram_work_bot.py
```
2. Open Telegram and start a conversation with your bot using the `/start` command.
3. Follow the bot's instructions.
4. The bot will fetch and display relevant resumes directly in the chat.
