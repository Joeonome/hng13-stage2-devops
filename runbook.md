# 🏃 Blue-Green Deployment Runbook (Stage 3 - HNG13)

## 1️⃣ Purpose

This runbook provides step-by-step instructions to deploy, monitor, and
test the **Blue/Green Node.js service** behind **Nginx** with: -
Automatic failover\
- Manual pool switching\
- Chaos simulation for resilience testing\
- Slack-based alert notifications

------------------------------------------------------------------------

## 2️⃣ Prerequisites

Before starting, ensure: - Docker and Docker Compose are installed\
- Python 3 is available\
- Slack Incoming Webhook URL is configured\
- Ports `8080`, `8081`, and `8082` are open

------------------------------------------------------------------------

## 3️⃣ Environment Setup

1.  **Clone the repository**

    ``` bash
    git clone <your_repo_url>
    cd hng13-stage3
    ```

2.  **Create `.env` file**

    ``` bash
    cp .env.example .env
    ```

    Update the variables:

        NGINX_TARGET=http://nginx_gateway
        SLACK_WEBHOOK_URL=<your_slack_webhook_url>
        ERROR_RATE_THRESHOLD=2.0
        WINDOW_SIZE=200
        ALERT_COOLDOWN_SEC=60

3.  **Pull the Blue/Green application image**

    ``` bash
    docker pull yimikaade/wonderful:devops-stage-two
    ```

4.  **Start the full stack**

    ``` bash
    docker compose up -d
    ```

------------------------------------------------------------------------

## 4️⃣ Service Access

  Component   URL
  ----------- ------------------------------------------
  Gateway     http://`<server_ip>`{=html}:8080/version
  Blue App    http://`<server_ip>`{=html}:8081/version
  Green App   http://`<server_ip>`{=html}:8082/version

Check the active pool:

``` bash
curl -I http://<server_ip>:8080/version
```

Response should include:

    X-App-Pool: blue

------------------------------------------------------------------------

## 5️⃣ Monitoring & Slack Alerts

The **Watcher (`watcher.py`)** continuously monitors error rates and
sends alerts to Slack when the error rate exceeds the configured
threshold.

1.  Ensure `.env` contains a valid `SLACK_WEBHOOK_URL`.\

2.  Run the watcher:

    ``` bash
    python3 watcher.py
    ```

### Example Slack Alert

    :fire: High Error Rate Detected!
    Error rate exceeded threshold: 5.0% (limit 2.0%)
    Time: 2025-10-31 21:41:09
    Current Pool: blue
    Requests Monitored: 64
    Recommended Action: Inspect upstream logs or consider switching pools

------------------------------------------------------------------------

## 6️⃣ Failover Simulation (Chaos Mode)

1.  **Confirm Blue is active**

    ``` bash
    curl -I http://<server_ip>:8080/version
    ```

2.  **Simulate failure on Blue**

    ``` bash
    curl -X POST http://<server_ip>:8081/chaos/start?mode=error
    ```

3.  **Check Gateway response**

    ``` bash
    curl -I http://<server_ip>:8080/version
    ```

    Expected:

        X-App-Pool: green

4.  **Stop Chaos Mode (restore Blue)**

    ``` bash
    curl -X POST http://<server_ip>:8081/chaos/stop
    ```

5.  **Confirm normal routing**

    ``` bash
    curl -I http://<server_ip>:8080/version
    ```

------------------------------------------------------------------------

## 7️⃣ Manual Pool Switching (Optional)

If you want to manually activate a pool:

1.  Edit `.env`:

        ACTIVE_POOL=green

2.  Reload Nginx configuration:

    ``` bash
    docker exec -it nginx_gateway nginx -s reload
    ```

3.  Verify:

    ``` bash
    curl -I http://<server_ip>:8080/version
    ```

------------------------------------------------------------------------

## 8️⃣ Container Logs (for HNG verification)

Run inside the Nginx container:

``` bash
docker exec -it nginx_gateway tail -n 10 /var/log/nginx/access.log
```

### Example Log Snippet

    2025/10/31 21:40:52 [info] 8#8: *45 pool=blue release=v1 upstream_status=200
    upstream_addr=172.18.0.2:8081 request_time=0.003
    "GET /version HTTP/1.1" 200 45 "-" "curl/8.6.0"

Fields: - `pool` → Active upstream (blue/green)\
- `release` → Release ID (v1/v2)\
- `upstream_status` → HTTP code from upstream\
- `request_time` → Latency in seconds

------------------------------------------------------------------------

## 9️⃣ Troubleshooting

**No Slack Alerts?** - Verify `SLACK_WEBHOOK_URL` in `.env`.\
- Ensure `requests` library is installed.\
- Check network connectivity from watcher container.

**Watcher not detecting errors?** - Ensure `NGINX_TARGET` matches the
gateway URL.\
- Lower `ERROR_RATE_THRESHOLD` for testing.\
- Confirm `/health` endpoint is reachable.

**Routing issues?** - Inspect generated Nginx config:
`bash   docker exec -it nginx_gateway cat /etc/nginx/conf.d/default.conf` -
Test upstreams directly:
`bash   curl -i http://<server_ip>:8081/version   curl -i http://<server_ip>:8082/version`

------------------------------------------------------------------------

## 🔟 Cleanup

Stop and remove containers, networks, and volumes:

``` bash
docker compose down
```

------------------------------------------------------------------------

**Author:** Joseph Onumeguolor\
**Track:** DevOps --- HNG13 Internship\
**Date:** 2025-10-30