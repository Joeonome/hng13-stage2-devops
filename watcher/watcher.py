#!/usr/bin/env python3
import os
import time
import requests
import logging
from collections import deque

# ==============================
# 🔧 Configuration
# ==============================
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD', 2.0))
WINDOW_SIZE = int(os.getenv('WINDOW_SIZE', 200))
ALERT_COOLDOWN_SEC = int(os.getenv('ALERT_COOLDOWN_SEC', 300))
NGINX_TARGET = os.getenv('NGINX_TARGET', 'http://nginx:80/version')

# ==============================
# 🧠 State
# ==============================
last_alert_time = 0
current_pool = "blue"
error_window = deque(maxlen=WINDOW_SIZE)
request_count = 0
pool_distribution = {"blue": 0, "green": 0, "unknown": 0}

# ==============================
# 📝 Logging Setup
# ==============================
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )

# ==============================
# 🚨 Slack Alerts
# ==============================
def send_slack_alert(message, alert_type="failover", error_rate=None, window_size=None, distribution=None):
    global last_alert_time
    current_time = time.time()

    if current_time - last_alert_time < ALERT_COOLDOWN_SEC:
        logging.info(f"⏱ Cooldown active, skipping alert: {message}")
        return False

    if not SLACK_WEBHOOK_URL:
        logging.error("⚠️ SLACK_WEBHOOK_URL not configured!")
        return False

    if alert_type == "failover":
        color = "#FFA500"  # Orange
        title = ":rotating_light: Pool Change Alert"
        fields = [
            {"title": "Alert", "value": title, "short": True},
            {"title": "Time", "value": f"*{time.strftime('%Y-%m-%d %H:%M:%S')}*", "short": True},
            {"title": "Current Pool", "value": f"*{current_pool}*", "short": True},
            {"title": "Requests Processed", "value": f"{request_count}", "short": True}
        ]
    else:
        color = "#FF0000"  # Red
        title = ":fire: High Error Rate Detected!"
        fields = [
            {"title": "⚠️ Status", 
             "value": f"*{error_rate:.1f}%* errors ❌ (limit: {ERROR_RATE_THRESHOLD:.1f}%)", 
             "short": False},
            {"title": "⏰ Checked At", 
             "value": f"*{time.strftime('%Y-%m-%d %H:%M:%S')}*", 
             "short": True},
            {"title": "Current Pool", "value": f"*{current_pool}*", "short": True},
            {"title": "Requests Monitored", "value": f"*{request_count}*", "short": True},
            {"title": "💡 Recommended Action", 
             "value": "_Inspect upstream logs or consider switching pools_", 
             "short": False}
        ]

    payload = {
        "text": f"{title}\n{message}",
        "username": "Joeonome Watcher",
        "icon_emoji": ":male-technologist:",
        "attachments": [
            {
                "color": color,
                "fields": fields,
                "footer": "Blue/Green Deployment Monitor",
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                "ts": time.time()
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            last_alert_time = current_time
            logging.info(f"✅ Slack alert sent successfully: {message}")
            return True
        else:
            logging.error(f"❌ Slack webhook error {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"💥 Network error sending Slack alert: {e}")
        return False

# ==============================
# 👀 Monitor Function
# ==============================
def monitor_services():
    global current_pool, error_window, request_count, pool_distribution

    nginx_url = NGINX_TARGET
    logging.info("🚀 Starting Blue/Green HTTP Monitor (Joeonome Version)")
    logging.info(f"Config: ERROR_RATE_THRESHOLD={ERROR_RATE_THRESHOLD}%, WINDOW_SIZE={WINDOW_SIZE}")
    logging.info(f"Monitoring Nginx endpoint: {nginx_url}")

    # Test Slack webhook
    logging.info("Testing Slack webhook connectivity...")
    try:
        test_response = requests.post(SLACK_WEBHOOK_URL, json={"text": "🔧 Joeonome Watcher started!"})
        if test_response.status_code == 200:
            logging.info("✅ Slack webhook is functional")
        else:
            logging.warning(f"⚠️ Slack webhook test returned {test_response.status_code}")
    except Exception as e:
        logging.warning(f"⚠️ Slack webhook test failed: {e}")

    # Main monitoring loop
    while True:
        try:
            response = requests.get(nginx_url, timeout=5)
            new_pool = response.headers.get('X-App-Pool', 'unknown')
            status_code = response.status_code
            is_error = status_code >= 500

            request_count += 1
            error_window.append(1 if is_error else 0)

            # Track pool distribution
            if new_pool not in pool_distribution:
                pool_distribution[new_pool] = 0
            pool_distribution[new_pool] += 1

            # Failover detection
            if current_pool and new_pool != current_pool and new_pool != 'unknown':
                message = f"Traffic switched from *{current_pool}* → *{new_pool}*."
                send_slack_alert(message, "failover")
                logging.info(f"📊 Pool switch detected: {current_pool} → {new_pool}")
                current_pool = new_pool

            # Error rate detection
            if len(error_window) >= 10:
                error_rate = (sum(error_window) / len(error_window)) * 100
                if error_rate > ERROR_RATE_THRESHOLD:
                    message = f"High Error Rate detected: {error_rate:.2f}% (limit {ERROR_RATE_THRESHOLD:.2f}%)"
                    send_slack_alert(
                        message,
                        "error_rate",
                        error_rate=error_rate,
                        window_size=len(error_window),
                        distribution=pool_distribution
                    )
                    logging.info(f"⚠️ Error rate alert: {error_rate:.2f}%")
                    error_window.clear()
                    # reset pool distribution
                    pool_distribution = {k: 0 for k in pool_distribution}

            # Periodic log
            if request_count % 20 == 0:
                error_rate = (sum(error_window) / len(error_window)) * 100 if error_window else 0
                logging.info(f"📈 {request_count} requests monitored | Current Pool: {current_pool} | Error Rate: {error_rate:.1f}%")

            time.sleep(3)

        except requests.exceptions.RequestException as e:
            logging.warning(f"🌐 HTTP request failed: {e}")
            error_window.append(1)
            time.sleep(5)
        except Exception as e:
            logging.error(f"💥 Monitoring loop exception: {e}")
            time.sleep(10)

# ==============================
# ▶️ Entrypoint
# ==============================
if __name__ == '__main__':
    setup_logging()
    logging.info("🔧 Initializing Joeonome Blue/Green Monitor...")
    time.sleep(15)
    monitor_services()