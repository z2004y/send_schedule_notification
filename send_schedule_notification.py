import json
import requests
import os
from datetime import datetime, date
import pytz

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

# 设置北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

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

    # 获取北京时间
    beijing_time = datetime.now(BEIJING_TZ)
    current_weekday = beijing_time.weekday() + 1  # Convert to 1-7 scale
    today = beijing_time.date()
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

        # 获取星期几的中文表示
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday_name = weekday_names[current_weekday - 1]

        title = f"📚 今日课程提醒 (第{current_week}周 {weekday_name})"
        content_lines = []
        
        # 添加主容器样式
        content_lines.append("""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                    line-height: 1.6; color: #333; padding: 20px; border-radius: 10px; 
                    background: linear-gradient(to bottom right, #f8f9fa, #e9ecef);">
        """)
        
        # 添加标题
        content_lines.append(f"""
        <h1 style="color: #2c3e50; margin: 0 0 20px 0; padding-bottom: 10px; 
                   border-bottom: 2px solid #3498db; text-align: center;">
            📚 今日课程安排
        </h1>
        """)
        
        # 添加日期和周数信息
        content_lines.append(f"""
        <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; color: #1565c0;">
                <span style="font-weight: bold;">📅 日期：</span>{today.strftime('%Y年%m月%d日')}
                <span style="margin-left: 15px; font-weight: bold;">📊 第{current_week}周</span>
                <span style="margin-left: 15px; font-weight: bold;">📌 {weekday_name}</span>
            </p>
        </div>
        """)
        
        # 添加天气信息
        content_lines.append(f"""
        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; color: #2e7d32;">
                <span style="font-weight: bold;">🌤️ 天气信息 ({WEATHER_CITY})：</span>{weather_info}
            </p>
        </div>
        """)
        
        # 添加课程列表
        content_lines.append("""
        <div style="margin-bottom: 20px;">
            <h2 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 1.2em;">
                📋 今日课程安排：
            </h2>
        """)
        
        for i, course in enumerate(todays_courses, 1):
            content_lines.append(f"""
            <div style="background-color: white; padding: 15px; border-radius: 5px; 
                        margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="margin: 0 0 10px 0; color: #1a237e; font-size: 1.1em; font-weight: bold;">
                    {i}. {course['course_name']}
                </p>
                <p style="margin: 0; color: #455a64;">
                    <span style="font-weight: bold;">⏰ 时间：</span>{course['start_time']}
                    <span style="margin-left: 15px; font-weight: bold;">📍 地点：</span>{course['location']}
                </p>
            </div>
            """)
        
        content_lines.append("</div>")
        
        # 添加底部信息
        now = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        content_lines.append(f"""
        <div style="text-align: right; font-size: 0.9em; color: #666; 
                    border-top: 1px solid #dee2e6; padding-top: 10px;">
            <p style="margin: 0;">
                <span style="font-weight: bold;">🕒 更新时间：</span>{now}
            </p>
        </div>
        """)
        
        content_lines.append("</div>")
        
        content = "".join(content_lines)
        
        send_notification(title, content)
    else:
        # 获取天气信息
        weather_info = get_weather(WEATHER_CITY, JUHE_WEATHER_API_KEY)

        # 获取星期几的中文表示
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday_name = weekday_names[current_weekday - 1]

        title = f"🎉 今日无课提醒 (第{current_week}周 {weekday_name})"
        content_lines = []
        
        # 添加主容器样式
        content_lines.append("""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                    line-height: 1.6; color: #333; padding: 20px; border-radius: 10px; 
                    background: linear-gradient(to bottom right, #f8f9fa, #e9ecef);">
        """)
        
        # 添加标题
        content_lines.append(f"""
        <h1 style="color: #2c3e50; margin: 0 0 20px 0; padding-bottom: 10px; 
                   border-bottom: 2px solid #3498db; text-align: center;">
            🎉 今日无课
        </h1>
        """)
        
        # 添加日期和周数信息
        content_lines.append(f"""
        <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; color: #1565c0;">
                <span style="font-weight: bold;">📅 日期：</span>{today.strftime('%Y年%m月%d日')}
                <span style="margin-left: 15px; font-weight: bold;">📊 第{current_week}周</span>
                <span style="margin-left: 15px; font-weight: bold;">📌 {weekday_name}</span>
            </p>
        </div>
        """)
        
        # 添加天气信息
        content_lines.append(f"""
        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; color: #2e7d32;">
                <span style="font-weight: bold;">🌤️ 天气信息 ({WEATHER_CITY})：</span>{weather_info}
            </p>
        </div>
        """)
        
        # 添加无课信息
        content_lines.append("""
        <div style="background-color: white; padding: 15px; border-radius: 5px; 
                    margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <p style="margin: 0; color: #1a237e; font-size: 1.1em; font-weight: bold; text-align: center;">
                🎉 今天没有课程安排，可以好好休息或安排其他活动！
            </p>
        </div>
        """)
        
        # 添加底部信息
        now = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        content_lines.append(f"""
        <div style="text-align: right; font-size: 0.9em; color: #666; 
                    border-top: 1px solid #dee2e6; padding-top: 10px;">
            <p style="margin: 0;">
                <span style="font-weight: bold;">🕒 更新时间：</span>{now}
            </p>
        </div>
        """)
        
        content_lines.append("</div>")
        
        content = "".join(content_lines)
        
        send_notification(title, content)
        print("No courses scheduled for today.")

if __name__ == "__main__":
    main() 
