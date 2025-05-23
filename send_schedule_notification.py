import json
import requests
import os
from datetime import datetime, date

# Get token and API key from environment variables
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
JUHE_WEATHER_API_KEY = os.environ.get("JUHE_WEATHER_API_KEY")

# TODO: Replace with your actual token
# PUSHPLUS_TOKEN = ""
SCHEDULE_FILE = "schedule.json"
PUSHPLUS_API_URL = "https://www.pushplus.plus/send"

# TODO: Replace with your actual Juhe Weather API Key
# JUHE_WEATHER_API_KEY = ""
JUHE_WEATHER_API_URL = "http://apis.juhe.cn/simpleWeather/query"
WEATHER_CITY = "兰州"

# Define the start date of the semester
SEMESTER_START_DATE = date(2025, 2, 24)

def load_schedule(file_path):
    """Loads the schedule from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            schedule = json.load(f)
        return schedule
    except FileNotFoundError:
        print(f"Error: Schedule file not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return None

def is_course_scheduled_this_week(week_type, current_week):
    """Checks if a course is scheduled for the current week based on its week_type."""
    if week_type == "every":
        return True
    try:
        # Assuming week_type is a comma-separated string of week numbers
        scheduled_weeks = [int(w) for w in week_type.split(',')]
        return current_week in scheduled_weeks
    except ValueError:
        print(f"Warning: Invalid week_type format: {week_type}")
        return False

def get_weather(city, api_key):
    """Gets weather information for a given city using Juhe Weather API."""
    params = {
        "city": city,
        "key": api_key
    }
    try:
        response = requests.get(JUHE_WEATHER_API_URL, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        weather_data = response.json()
        if weather_data and weather_data.get("error_code") == 0:
            # Get today's forecast from the 'future' list
            future_weather = weather_data.get("result", {}).get("future", [])
            if future_weather:
                today_forecast = future_weather[0] # Get the first element for today
                weather_info = f"今日天气: {today_forecast.get('weather', 'N/A')}, 温度: {today_forecast.get('temperature', 'N/A')}, 风向: {today_forecast.get('direct', 'N/A')}"
                return weather_info
            else:
                return "无法获取今天的天气预报。"
        else:
            return f"天气 API 请求失败: {weather_data.get('reason', '未知错误')}"
    except requests.exceptions.RequestException as e:
        return f"请求天气 API 发生错误: {e}"
    except json.JSONDecodeError:
        return "解析天气数据失败。"

def send_notification(title, content):
    """Sends a push notification using the Pushplus API."""
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "html", # You can choose a different template if needed
        "topic": "721683736" # Add topic parameter for group push
    }
    try:
        response = requests.get(PUSHPLUS_API_URL, params=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        if result.get("code") == 200:
            print(f"Notification sent successfully: {title}")
        else:
            print(f"Failed to send notification: {title}, Response: {result}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {title}, Exception: {e}")

def main():
    # Check if tokens are set
    if not PUSHPLUS_TOKEN:
        print("Error: PUSHPLUS_TOKEN environment variable not set.")
        return
    if not JUHE_WEATHER_API_KEY:
        print("Error: JUHE_WEATHER_API_KEY environment variable not set.")
        return

    schedule = load_schedule(SCHEDULE_FILE)
    if not schedule:
        return

    current_weekday = datetime.now().weekday() + 1 # Convert to 1-7 scale
    today = date.today()
    current_week = (today - SEMESTER_START_DATE).days // 7 + 1

    print(f"Checking schedule for today (Weekday {current_weekday}, Week {current_week})...")

    todays_courses = []
    for course in schedule:
        if course["weekday"] == current_weekday:
            if is_course_scheduled_this_week(course["week_type"], current_week):
                todays_courses.append(course)

    if todays_courses:
        # Sort courses by start time
        todays_courses.sort(key=lambda course: course['start_time'])

        # Get weather information
        weather_info = get_weather(WEATHER_CITY, JUHE_WEATHER_API_KEY)

        title = f"今日课程提醒 (第{current_week}周)"
        content_lines = []
        
        # Add a container div with refined styling and increased font size
        content_lines.append("<div style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; line-height: 1.6; color: #333; padding: 15px; border: 1px solid #cce5ff; border-radius: .25rem; background-color: #e9f7fd; font-size: 0.9em;\">")
        
        # Add a heading with refined styling including week number
        content_lines.append(f"<h2 style=\"color: #004085; margin-top: 0; margin-bottom: 10px; border-bottom: 2px solid #b8daff; padding-bottom: 5px;\">今日课程安排：</h2>")
        
        # Add weather information
        content_lines.append(f"<p style=\"margin-bottom: 15px; color: #0056b3;\"><span style=\"font-weight: bold;\">当前天气 ({WEATHER_CITY}):</span> {weather_info}</p>")
        
        # Add introductory text with refined styling
        content_lines.append("<p style=\"margin-bottom: 20px; color: #004085;\">请注意以下课程时间和地点：</p>")
        
        # Start the unordered list with refined styling
        content_lines.append("<ul style=\"padding-left: 0; margin-bottom: 20px; list-style: none;\">") # Removed padding-left and added margin-bottom
        
        for course in todays_courses:
            # Using HTML list items with refined styling and emoji
            content_lines.append(f"<li style=\"margin-bottom: 15px; padding: 15px; border: 1px solid #b8daff; border-radius: .25rem; background-color: #cce5ff; box-shadow: 0 2px 4px rgba(0,0,0,.05);\">📚 <b><span style=\"font-size: 1.1em; color: #0056b3;\">{course['course_name']}</span></b><br>时间：{course['start_time']}<br>地点：{course['location']}</li>")
        
        content_lines.append("</ul>") # End the unordered list
        
        # Add a footer with timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content_lines.append(f"<div style=\"text-align: right; font-size: 0.8em; color: #666; margin-top: 10px;\">更新时间：{now}</div>")

        content_lines.append("</div>") # End the container div
        
        content = "".join(content_lines)
        
        send_notification(title, content)
    else:
        print("No courses scheduled for today.")

if __name__ == "__main__":
    main() 
