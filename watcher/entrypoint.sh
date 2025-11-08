#!/bin/sh
echo "Installing dependencies..."
pip install -r /app/watcher/requirements.txt

echo "Waiting for Nginx logs to be ready..."
while [ ! -f /var/log/nginx/access.log ]; do
    echo "[!] Log file not found, retrying in 5s..."
    sleep 5
done

echo "Starting watcher..."
python /app/watcher/watcher.py
