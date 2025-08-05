# ELSA – Voice Assistant with Gemini AI

ELSA is a Python-based voice assistant that can execute commands (open apps, search, weather, etc.) and optionally use Google's Gemini AI for intelligent responses.

---

## Features
- Voice and text command support
- Open websites and desktop applications
- Weather, system info, news, jokes, notes, timers, and more
- Gemini AI integration for conversational responses
- Fallback to static responses if Gemini is disabled or unavailable

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/dikshanagvekar/OIBSIP-Task-1.git
cd elsa-assistant

###Install dependencies
pip install -r requirements.txt

###Set up environment variables
 Create a .env file based on .env.example:
 cp .env.example .env

Edit .env and add your Gemini API key:
GEMINI_API_KEY=your_api_key_here

### Email Setup
1. Enable 2-Step Verification on your Google Account.
2. Generate an App Password under **Google Account → Security → App Passwords**.
3. Add these to your `.env` file:

----EMAIL_ADDRESS=your_gmail_here
----EMAIL_PASSWORD=your_app_password_here
4. ELSA will use these credentials to send emails.

###Usage
Run the assistant:

python ELSA.py
   ###On startup, choose Gemini mode or static mode:
Enable Gemini AI mode? (yes/no):

###File Structure

project-root/
│── ELSA.py           # Main assistant script
│── requirements.txt  # Dependencies
│── .env.example      # Example env file
│── .gitignore        # Ignores .env
│── README.md         # Documentation

Notes
1)Keep .env out of version control (already ignored in .gitignore)
2)Use .env.example for sharing required variables
3)Tested on Python 3.9+ (Windows)