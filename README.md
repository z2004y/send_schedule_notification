# 课程推送通知脚本

这是一个 Python 脚本，用于根据课程表 `schedule.json` 和当前日期，通过 Pushplus 推送今日课程安排和天气信息。

## 功能特点

- 从 `schedule.json` 读取课程表。
- 根据当前日期和学期开始日期计算当前周次。
- 检查当天是否有课程，并判断课程是否在本周进行。
- 调用聚合数据天气 API 获取指定城市的天气信息。
- 将当天课程和天气信息整合到一条美化过的 HTML 消息中。
- 使用 Pushplus API 发送推送通知。
- 支持通过环境变量配置敏感信息（Pushplus Token 和天气 API Key），方便在 GitHub Actions 等环境下部署。

## 文件说明

- `send_schedule_notification.py`: 主程序脚本。
- `schedule.json`: 存储你的课程表信息。

## 本地运行

1.  **克隆仓库**：将代码克隆到本地。

    ```bash
    git clone <你的仓库地址>
    cd <你的仓库目录>
    ```

2.  **安装依赖**：安装所需的 Python 库 `requests`。

    ```bash
    pip install requests
    ```

3.  **配置 `schedule.json`**：根据你的实际课程表编辑 `schedule.json` 文件。确保格式正确，包含 `course_name`, `start_time`, `location`, `weekday`, `week_type` 等字段。`weekday` 1-7 表示星期一到星期日，`week_type` 可以是 "every" 或以逗号分隔的周次列表。

4.  **配置 API Keys**：为了安全起见，程序从环境变量读取 Pushplus Token 和聚合数据天气 API Key。在运行脚本前，需要设置这两个环境变量。

    - 获取你的 Pushplus Token: 访问 [Pushplus](https://www.pushplus.plus/)。
    - 获取你的聚合数据天气 API Key: 访问 [聚合数据](https://www.juhe.cn/)，注册并申请天气预报 API。

    在终端中设置环境变量（请将 `YOUR_PUSHPLUS_TOKEN` 和 `YOUR_JUHE_WEATHER_API_KEY` 替换为你的实际 Key）：

    **Windows PowerShell:**

    ```powershell
    $env:PUSHPLUS_TOKEN="YOUR_PUSHPLUS_TOKEN"
    $env:JUHE_WEATHER_API_KEY="YOUR_JUHE_WEATHER_API_KEY"
    python send_schedule_notification.py
    ```

    **Linux/macOS:**

    ```bash
    export PUSHPLUS_TOKEN="YOUR_PUSHPLUS_TOKEN"
    export JUHE_WEATHER_API_KEY="YOUR_JUHE_WEATHER_API_KEY"
    python send_schedule_notification.py
    ```

5.  **运行脚本**：

    ```bash
    python send_schedule_notification.py
    ```

## 部署到 GitHub Actions

可以将脚本部署到 GitHub Actions，实现每天定时自动运行。

1.  **将代码上传到 GitHub 仓库**：包括 `send_schedule_notification.py` 和 `schedule.json`。

2.  **在 GitHub 仓库中设置 Secrets**：

    - 进入你的 GitHub 仓库页面。
    - 点击 **Settings**。
    - 在左侧导航栏中，点击 **Secrets and variables** -> **Actions**。
    - 点击 **New repository secret**。
    - 创建名为 `PUSHPLUS_TOKEN` 的 Secret，其值为你的 Pushplus Token。
    - 再次点击 **New repository secret**，创建名为 `JUHE_WEATHER_API_KEY` 的 Secret，其值为你的聚合数据天气 API Key。

3.  **创建 GitHub Actions Workflow 文件**：

    - 在你的 GitHub 仓库中，点击 **Actions**。
    - 点击 **set up a workflow yourself**。
    - 将文件名修改为 `.github/workflows/schedule_notify.yml` (如果目录不存在请创建)。
    - 将以下 YAML 代码复制到文件中：

    ```yaml
    name: Schedule Notification

    on:
      schedule:
        # Runs every day at 6:40 AM UTC
        - cron: '40 6 * * *'
      workflow_dispatch: # Allows manual triggering

    jobs:
      run_script:
        runs-on: ubuntu-latest

        steps:
        - name: Checkout code
          uses: actions/checkout@v4

        - name: Set up Python
          uses: actions/setup-python@v5
          with:
            python-version: '3.x'

        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install requests

        - name: Run schedule notification script
          env:
            PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
            JUHE_WEATHER_API_KEY: ${{ secrets.JUHE_WEATHER_API_KEY }}
          run: python send_schedule_notification.py
    ```

    **注意**：请根据你的需求调整 `cron: '40 6 * * *'` 来设置定时运行时间（基于 UTC 时间）。

4.  **提交并推送**：提交并推送 `.github/workflows/schedule_notify.yml` 文件到你的仓库。

完成以上步骤后，GitHub Actions 将会按照你设定的时间自动运行脚本并发送课程和天气推送通知。

## 许可证

[选择一个合适的开源许可证，例如 MIT 许可证] 