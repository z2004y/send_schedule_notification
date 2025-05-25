# 课程提醒推送服务

这是一个基于 Python 的课程提醒推送服务，使用 GitHub Actions 定时运行，通过 Pushplus 推送服务发送课程提醒通知。

## 功能特点

- 📅 自动计算当前周数
- 📚 根据课程表发送每日课程提醒
- 🌤️ 集成天气信息（使用聚合数据API）
- ⏰ 每天早上6:40自动推送（北京时间）
- 🎯 支持手动触发推送
- 📱 支持 Pushplus 推送服务
- 🌍 使用北京时间（UTC+8）

## 配置说明

### 1. 环境变量配置

在 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中配置以下 secrets：

- `PUSHPLUS_TOKEN`: Pushplus 推送服务的 token
- `JUHE_WEATHER_API_KEY`: 聚合数据天气 API 的 key

### 2. 课程表配置

在 `schedule.json` 文件中配置课程信息，格式如下：

```json
[
    {
        "course_name": "课程名称",
        "weekday": 1,  // 1-7 表示周一到周日
        "start_time": "08:00",
        "location": "教室位置",
        "week_type": "every"  // "every" 表示每周都上，或者用逗号分隔的周数，如 "1,3,5"
    }
]
```

### 3. 学期配置

在 `send_schedule_notification.py` 中配置学期开始日期：

```python
SEMESTER_START_DATE = date(2025, 2, 24)  # 修改为你的学期开始日期
```

## 使用说明

1. Fork 本仓库
2. 配置环境变量（Pushplus Token 和天气 API Key）
3. 修改 `schedule.json` 配置你的课程表
4. 修改学期开始日期
5. 启用 GitHub Actions

## 推送效果

推送内容包含：
- 当前周数
- 今日天气信息
- 课程时间表
- 课程地点
- 更新时间

## 依赖说明

- Python 3.10+
- requests
- pytz

## 注意事项

1. 确保 GitHub Actions 已启用
2. 确保环境变量配置正确
3. 课程表格式必须符合要求
4. 天气 API 有调用次数限制，请合理使用

## 手动触发

除了自动推送外，你也可以在 GitHub Actions 页面手动触发推送：
1. 进入仓库的 Actions 页面
2. 选择 "Schedule Notification" 工作流
3. 点击 "Run workflow" 按钮

## 许可证

MIT License 
