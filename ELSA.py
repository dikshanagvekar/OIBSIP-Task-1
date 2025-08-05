import speech_recognition as sr
import pyttsx3
import datetime
import time
from dateutil import parser
import wikipedia
import webbrowser
import os
import subprocess
import platform
import smtplib
from email.message import EmailMessage
import re
import psutil
import pyjokes
import pyautogui
import requests
import calendar
import winsound
import speedtest
import google.generativeai as genai
from dotenv import load_dotenv

# ---------------- INITIALIZATION ----------------

try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    if voices:
        # Use female voice if available, otherwise fallback to first
        engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
    engine.setProperty('rate', 180)  # Set speaking speed   
except Exception as e:
    print(f"TTS initialization failed: {e}")
    engine = None

# Speak function
def speak(text):
    print(f"ELSA: {text}")  # Always print for debugging
    try:
        engine.say(text)        # Queue the text
        engine.runAndWait()     # Process and play audio
        engine.stop()           # Clear the queue to prevent overlap
    except Exception as e:
        print(f"[Speak Error] {e}")


# Greeting
def greeting():
    current_time = datetime.datetime.now()
    if current_time.hour < 12:
        msg = "Good morning! It's a bright new day, full of possibilities!"
    elif 12 <= current_time.hour < 18:
        msg = "Good afternoon! I hope your day is going well."
    else:
        msg = "Good evening! I'm here to assist you with whatever you need."
    
    # Combine greeting and intro message into one speech
    full_msg = f"{msg} I am ELSA, your virtual assistant. How can I assist you today?"
    speak(full_msg)

# ---------------- VOICE COMMAND ----------------

def take_command(language='en-US'):
    listener = sr.Recognizer()

    for attempt in range(3):  # Retry listening 3 times
        try:
            with sr.Microphone() as source:
                print("Listening...")
                listener.adjust_for_ambient_noise(source, duration=1)  # calibrate quickly
                voice = listener.listen(source, phrase_time_limit=10)  # no strict timeout
                command = listener.recognize_google(voice, language=language).lower()
                if 'elsa' in command:
                    command = command.replace('elsa', '').strip()
                print(f"User said: {command}")
                return command
        except sr.UnknownValueError:
            speak("Sorry, I did not understand. Please repeat.")
        except sr.RequestError:
            speak("Speech service is unavailable.")
        except Exception as e:
            print(f"Voice error: {e}")

    # If all attempts fail, fallback to manual input
    print("No voice detected, switching to manual input.")
    return input("Type your command: ").lower().strip()


# Function to get current weather information
def get_weather():
    speak("Which city's weather would you like to know?")
    city_name = take_command()
    if city_name:
        api_key = '1c284bf58d670036271690bf4377ae61'  # Replace with your OpenWeatherMap API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            main = response["main"]
            weather_desc = response["weather"][0]["description"]
            temp = main["temp"]
            humidity = main["humidity"]
            wind_speed = response["wind"]["speed"]
            speak(f"The temperature in {city_name} is {temp:.1f}°C with {weather_desc}. Humidity is at {humidity}% and wind speed is {wind_speed} m/s.")
        else:
            speak(f"Sorry, I couldn't find weather information for {city_name}.")

# Function to get system information
def get_system_info():
    speak('Let me gather some details about your system...')
    uname = platform.uname()
    cpu_usage = psutil.cpu_percent()
    battery = psutil.sensors_battery()
    info = (f"You are using a {uname.system} system with a {uname.processor} processor."
            f" Your machine is named {uname.node}, running on {uname.release}. "
            f"Current CPU usage is {cpu_usage}%. Battery level is at {battery.percent}%.")
    print(info)
    speak(info)

# Function to open applications and websites
def open_app_or_web(command):
    # Predefined websites
    websites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "stack overflow": "https://stackoverflow.com",
        "gmail": "https://mail.google.com",
    }

    # Predefined local apps (add more as needed)
    local_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # adjust path if needed
        "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
    }

    # Extract keyword (remove "open")
    keyword = command.replace("open", "").strip()

    # 1. Check websites
    if keyword in websites:
        speak(f"Opening {keyword}")
        webbrowser.open(websites[keyword])
        return

    # 2. Check local apps
    if keyword in local_apps:
        speak(f"Launching {keyword}")
        try:
            if platform.system() == "Windows":
                os.startfile(local_apps[keyword])
            else:
                subprocess.Popen([local_apps[keyword]])
        except Exception as e:
            speak(f"Unable to launch {keyword}. Please check installation path.")
        return

    # 3. Fallback: Google Search
    speak(f"I couldn't find {keyword} in my apps or websites. Searching on Google.")
    webbrowser.open(f"https://www.google.com/search?q={keyword}")

def create_text_file():
    speak('Please provide a name for the text file.')
    file_name = take_command()
    if file_name:
        path = os.path.join(os.path.expanduser('~'), 'Desktop', f"{file_name}.txt")
        with open(path, 'w') as file:
            speak('What would you like to write in the file?')
            content = take_command()
            file.write(content)
            speak(f'Text file {file_name}.txt has been created on your Desktop.')
    else:
        speak('File name cannot be empty.')

def schedule_meeting():
    speak("Please tell me the meeting title.")
    title = take_command()

    speak("When is the meeting? Please specify the date and time.")
    date_time_input = take_command()  # Example format: "October 12, 2024, at 10 AM"

    speak("How long is the meeting in minutes?")
    duration_input = take_command()  # Expecting a number input

    try:
        # Parse the date and time input
        meeting_time = parser.parse(date_time_input)
        
        # Calculate end time based on duration
        duration = int(duration_input)
        end_time = meeting_time + datetime.timedelta(minutes=duration)
        
        # Ask if the user wants a reminder
        speak("Do you want to set a reminder for this meeting? Say 'yes' or 'no'.")
        reminder_response = take_command().lower()
        
        reminder_time = None
        if 'yes' in reminder_response:
            speak("How many minutes before the meeting do you want the reminder?")
            reminder_input = take_command()
            reminder_minutes = int(reminder_input)
            reminder_time = meeting_time - datetime.timedelta(minutes=reminder_minutes)
            speak(f"Reminder set for {reminder_minutes} minutes before the meeting.")

        # Formatting meeting details
        meeting_details = f"Meeting: {title}\n" \
                        f"Date and Time: {meeting_time.strftime('%Y-%m-%d %H:%M')}\n" \
                        f"Duration: {duration} minutes\n" \
                        f"End Time: {end_time.strftime('%Y-%m-%d %H:%M')}\n"
        
        if reminder_time:
            meeting_details += f"Reminder Time: {reminder_time.strftime('%Y-%m-%d %H:%M')}\n"

        # Saving meeting details to a file
        path = os.path.join(os.path.expanduser('~'), 'Desktop', 'meetings.txt')
        with open(path, 'a') as file:
            file.write(meeting_details + "\n")

        speak(f"Meeting titled '{title}' has been scheduled for {meeting_time.strftime('%Y-%m-%d %H:%M')}.")

    except (ValueError, Exception) as e:
        speak("I couldn't understand the date and time. Please try again.")
        print(f"Error: {e}")

def take_notes():
    speak("What category do you want to assign to this note? (e.g., personal, work, study)")
    category = take_command()

    speak("What would you like to note down?")
    note_content = take_command()

    if note_content:
        # Get the current date and time
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the note entry
        formatted_note = f"[{timestamp}] [{category}] {note_content}\n"
        
        # Define the file path for the notes
        path = os.path.join(os.path.expanduser('~'), 'Desktop', 'notes.txt')
        
        # Save the note to the file
        with open(path, 'a') as file:
            file.write(formatted_note)
        
        # Inform the user about the saved note
        speak(f"Note has been saved under the category '{category}'. Here is what I saved: {note_content}")
    else:
        speak("Note content cannot be empty.")

def extract_number(text):
    numbers = re.findall(r'\d+', text)  # Finds all numbers in the string
    return int(numbers[0]) if numbers else None  # Return the first number found, if any

def study_timer():
    try:
        speak("How many minutes would you like to study?")
        study_time_text = take_command()
        study_time = extract_number(study_time_text)
        
        if study_time is None:
            speak("I couldn't understand the study time. Please say it again.")
            return

        speak("How many minutes of break would you like to take?")
        break_time_text = take_command()
        break_time = extract_number(break_time_text)
        
        if break_time is None:
            speak("I couldn't understand the break time. Please say it again.")
            return

    except ValueError:
        speak("Please provide a valid number.")
        return

    speak(f"Starting study timer for {study_time} minutes.")
    time.sleep(study_time * 60)  # Convert to seconds
    speak("Time's up! Take a break.")
    winsound.Beep(1000, 1000)
    
    speak(f"Starting break time for {break_time} minutes.")
    time.sleep(break_time * 60)  # Convert to seconds
    winsound.Beep(800, 1000)  # Different tone for break end
    speak("Break time is over. Let's get back to studying!")


def search_jobs():
    speak("What type of job are you looking for? (e.g., software developer, data analyst, etc.)")
    job_type = take_command()
    
    speak("Which location are you looking to work in? (e.g., New York, Remote, etc.)")
    location = take_command()
    
    speak("What type of employment are you looking for? (e.g., full-time, part-time, contract, remote)")
    employment_type = take_command()
    
    # Construct the job search URL with parameters
    url = f"https://www.indeed.com/q-{job_type}-l-{location}-jobs.html"
    
    # Optionally add employment type to the URL or inform the user
    if employment_type.lower() in ["full-time", "part-time", "contract", "remote"]:
        speak(f"Searching for {employment_type.lower()} {job_type} jobs in {location}.")
    else:
        speak(f"Searching for {job_type} jobs in {location}.")
    
    # Open the job search results
    webbrowser.open(url)
    speak(f"Here are the job listings for {job_type} in {location}.")

# Function to play music
def play_music():
    music_dir = "C:\\Users\\diksh\\Music\\Diksha" # Replace with your music directory
    songs = os.listdir(music_dir)
    if songs:
        os.startfile(os.path.join(music_dir, songs[0]))
        speak("Enjoy your music!!")
    else:
        speak("It seems like your music folder is empty.")  

def take_screenshot():
    screenshots_dir = "C:\\Users\\diksh\\Pictures\\Screenshots"  # Change to your desired directory
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'screenshot_{timestamp}.png'
    file_path = os.path.join(screenshots_dir, filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    speak(f'Screenshot taken and saved as {filename}')
# Function to set an alarm
def set_alarm():
    speak("Please type the time to set the alarm, in HH:MM format.")
    alarm_time = input("Enter alarm time (HH:MM): ")
    try:
        alarm_time_obj = datetime.datetime.strptime(alarm_time, "%H:%M").time()
        speak(f"Alarm is set for {alarm_time}")
        while True:
            current_time = datetime.datetime.now().time()
            if current_time.hour == alarm_time_obj.hour and current_time.minute == alarm_time_obj.minute:
                speak("Wake up! Time to get up!")
                winsound.Beep(1000, 1000)
                break
            time.sleep(10)
    except ValueError:
        speak("Invalid time format. Please try again in HH:MM format.")

def research_topic():
    speak("What topic would you like to research?")
    topic = take_command()
    try:
        summary = wikipedia.summary(topic, sentences=3)
        speak(f"Here's a brief summary of {topic}: {summary}")
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"There are multiple topics related to {topic}. Can you specify further?")
    except Exception as e:
        speak(f"Sorry, I couldn't retrieve information. {e}")
        print(summary)
    # Search on Google
    speak("Would you like me to perform a Google search as well?")
    response = take_command()
    if 'yes' in response:
        webbrowser.open(f"https://www.google.com/search?q={topic}")

def open_calender():
    try:
        speak('Please tell me the year you want to view.')
        year = int(take_command())
        speak('Now, please tell me the month you want to view.')
        month = int(take_command())
        cal = calendar.month(year, month)
        speak(f'Here is the calendar for {calendar.month_name[month]} {year}.')
        print(cal)
    except Exception as e:
        speak("Sorry, I couldn't fetch the calendar.")
        print(f"Error: {e}")

def test_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    speak(f"Your download speed is {download_speed:.2f} Mbps and your upload speed is {upload_speed:.2f} Mbps.")

def find_location():
    try:
        speak("Which location would you like to find?")
        location = take_command()
        if location:
            speak(f"Finding the location of {location}.")
            webbrowser.open(f"https://www.google.com/maps/place/{location}")
        else:
            speak("I didn't catch that. Please try again.")
    except Exception as e:
        speak("Sorry, I couldn't find the location.")
        print(f"Error: {e}")

#sending email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Email sender function
def send_email():
    try:
        # 1. Get recipient email (typed for accuracy)
        while True:
            speak("Please type the recipient's email address.")
            recipient = input("Enter recipient's email: ")
            if is_valid_email(recipient):
                break
            else:
                speak("That doesn't seem to be a valid email address. Please try again.")

        # 2. Get subject (voice or text)
        speak("What would you like the subject to be?")
        subject = take_command()

        # 3. Get body (voice or text)
        speak("What should I include in the email body?")
        body = take_command()

        # 4. Prepare email
        email = EmailMessage()
        email['From'] = EMAIL_ADDRESS
        email['To'] = recipient
        email['Subject'] = subject
        email.set_content(body)

        # 5. Send email securely
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(email)

        speak("Email has been sent successfully.")
    except Exception as e:
        speak("Sorry, I couldn't send the email.")
        print(f"Error: {e}")


# Function to tell a joke
def tell_joke():
    speak(pyjokes.get_joke())

# Load .env variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")  # from .env file

# Initialize Gemini model if API key exists
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Gemini initialization failed: {e}")
        gemini_model = None
else:
    print("Warning: Gemini API key not found. Using static responses.")
    gemini_model = None

# Toggle Gemini mode (ask user)
use_gemini = False
choice = input("Enable Gemini AI mode? (yes/no): ").strip().lower()
use_gemini = choice == "yes"

# Chatbot function with fallback
def chatbot_response(prompt):
    global use_gemini

    # If Gemini enabled and available
    if use_gemini and gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                # Fallback to static if empty
                return static_responses.get(prompt.lower(), static_responses['default'])
        except Exception as e:
            print(f"[Gemini Error] {e}")
            # Fallback to static responses
            return static_responses.get(prompt.lower(), static_responses['default'])
    else:
        # Static mode
        return static_responses.get(prompt.lower(), static_responses['default'])

# Static fallback responses
static_responses = {
        'hello': 'Hi there! How can I help you today?',
        'how are you': 'I am doing great! How about you?',
        'what is your name': 'I am ELSA, your virtual assistant.',
        'bye': 'Goodbye! Have a great day!',
        'what can you do': 'I can assist with various tasks like opening apps, sending emails, telling jokes, and more. Just ask!',
        'who created you': 'I was created by a talented developer!',
        'thank you': 'You\'re welcome!',
        'what is your purpose': 'My purpose is to assist you with tasks and provide information.',
        'how old are you': 'I am as old as the lines of code I am made of!',
        'default': 'Sorry, I didn\'t understand that. Can you please repeat?'
}

def search_google():
    speak("What would you like me to search for?")
    query = take_command()
    if query:
        url = f"https://google.com/search?q={query}"
        webbrowser.open(url)
        speak(f"Here are the results for {query}")

# News briefing
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def news_briefing():
    if not NEWS_API_KEY:
        speak("News API key not configured. Please add it to your .env file.")
        return

    speak("Fetching the latest news headlines. Please hold on for a moment.")
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check for articles
        articles = data.get('articles', [])
        if not articles:
            speak("There are currently no news headlines available.")
            return

        # Ask user for number of headlines
        speak("How many headlines would you like to hear? Please say a number.")
        num_input = take_command()

        # Convert spoken number words to integers (e.g., "five" → 5)
        try:
            num_of_headlines = int(num_input)
        except ValueError:
            # Basic mapping for common numbers
            number_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
            num_of_headlines = number_words.get(num_input.lower(), 5)

        # Validate number
        if num_of_headlines < 1:
            num_of_headlines = 5

        # Speak headlines
        headlines = articles[:num_of_headlines]
        for article in headlines:
            title = article.get('title', 'No title available')
            speak(title)
            print(title)

    except requests.exceptions.RequestException as e:
        speak("Sorry, I couldn't fetch the news. Please try again later.")
        print(f"Error: {e}")


# Main command handler
def run_elsa():
    command = take_command()
    if not command:
        return  # Skip empty commands
    print(f"Received command: {command}")
    if 'current time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        speak(f"The current time is {current_time}")
    elif 'search' in command:
        search_google()
    elif 'calendar' in command:
        open_calender()
    elif 'open' in command:
        open_app_or_web(command)
    elif 'weather' in command or 'report' in command:
        get_weather()
    elif 'send email' in command:
        send_email()
    elif 'get system info' in command:
        get_system_info()
    elif 'create text file' in command:
        create_text_file()
    elif 'research' in command or 'topic' in command:
        research_topic()
    elif 'play music' in command or 'music' in command:
        play_music()
    elif 'set alarm' in command:
        set_alarm()
    elif 'take a screenshot' in command:
        take_screenshot()
    elif 'show internet speed' in command or 'speed' in command:
        test_speed()
    elif 'study timer' in command or 'timer' in command:
        study_timer()
    elif 'note' in command:
        take_notes()
    elif 'meeting timer' in command:
        schedule_meeting()
    elif 'find job' in command or 'search job' in command:
        search_jobs()
    elif 'current news' in command:
        news_briefing()
    elif 'tell me a joke' in command:
        tell_joke()
    elif 'exit' in command or 'quit' in command:
        speak('Goodbye!')
        exit()
    else:
        response = chatbot_response(command)
        print(response)
        speak(response)

# Start assistant
if __name__ == "__main__":
    greeting()
    while True:
        run_elsa()