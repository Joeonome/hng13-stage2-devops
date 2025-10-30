import os
import time
import json
import requests
from collections import deque
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = '/var/log/nginx/access.log'
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD', 2))
WINDOW_SIZE = int(os.getenv('WINDOW_SIZE', 200))
ALERT_COOLDOWN_SEC = int(os.getenv('ALERT_COOLDOWN_SEC', 300))
ACTIVE_POOL = os.getenv('ACTIVE_POOL', 'blue')

last_alert_time = 0
last_pool = ACTIVE_POOL
recent_statuses = deque(maxlen=WINDOW_SIZE)

def send_slack_alert(message):
    """Send formatted alert to Slack."""
    global last_alert_time
    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN_SEC:
        return  # prevent spam

    last_alert_time = now
    payload = {"text": f":rotating_light: {message}"}
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        print(f"Slack alert failed: {e}")

def parse_log_line(line):
    """Extract key-value pairs from Nginx log line."""
    parts = line.strip().split()
    data = {}
    for part in parts:
        if '=' in part:
            key, val = part.split('=', 1)
            data[key] = val
    return data

def main():
    global last_pool
    print("Watcher started. Monitoring Nginx logs...")

    with open(LOG_PATH, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            if "pool=" not in line:
                continue

            data = parse_log_line(line)
            pool = data.get('pool')
            status = data.get('upstream_status', '200')

            # Detect failover
            if pool and pool != last_pool:
                send_slack_alert(f"Failover detected! Active pool switched from {last_pool} → {pool}")
                last_pool = pool

            # Track status codes
            recent_statuses.append(status)
            errors = sum(1 for s in recent_statuses if s.startswith('5'))
            error_rate = (errors / len(recent_statuses)) * 100 if recent_statuses else 0

            # Detect high error rate
            if error_rate > ERROR_RATE_THRESHOLD:
                send_slack_alert(
                    f"High error rate detected! {error_rate:.2f}% 5xx responses in last {len(recent_statuses)} requests"
                )

if __name__ == "__main__":
    main()
