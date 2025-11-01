## 🚀 Blue-Green Deployment with Nginx (Stage 3 - HNG13)

### 🧩 Overview
This setup deploys a **Blue/Green Node.js service** behind **Nginx** with automatic failover, manual toggle support, and **Slack alerts for high error rates**.  
- **Blue** serves traffic by default.  
- **Nginx** automatically switches to **Green** if Blue becomes unhealthy.  
- **Watcher** monitors error rates and pool switches, sending notifications to Slack.

---

### 🌐 Server Details
| Component | Description | Port |
|------------|--------------|------|
| **Server IP** | `<your_server_ip>` | — |
| **Nginx Gateway** | Public entrypoint | `8080` |
| **Blue App** | Primary (active) | `8081` |
| **Green App** | Backup (standby) | `8082` |

---

### ⚙️ How to Run

1. **Clone the repository**
```bash
git clone <your_repo_url>
cd hng13-stage3
```

2. **Create the `.env` file**
```bash
cp .env.example .env
```

3. **Pull the required images**
```bash
docker pull yimikaade/wonderful:devops-stage-two
```

4. **Start the stack**
```bash
docker compose up -d
```

5. **Run the watcher for monitoring & Slack alerts**
```bash
docker exec -it watcher python3 watcher.py
```

---

### 🧪 Testing Failover & Error Alerts

#### ✅ Step 1: Confirm Blue is active
```bash
curl -I http://localhost:8080/version
```
Response should include:
```
X-App-Pool: blue
```

#### ⚠️ Step 2: Simulate Blue failure
```bash
curl -X POST http://localhost:8081/chaos/start?mode=error
```

#### 🔁 Step 3: Check failover
```bash
curl -I http://localhost:8080/version
```
Response should now include:
```
X-App-Pool: green
```

#### 🔥 Step 4: Trigger high error rate alert
```bash
for i in $(seq 1 20); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081/version; sleep 0.2; done
```
- Check Slack channel for high error rate alert message.

#### 🔄 Step 5: Restore Blue
```bash
curl -X POST http://<localhost:8081/chaos/stop
curl -I http://localhost:8080/version
```
Response should again include:
```
X-App-Pool: blue
```

---

### 📂 File Structure

| File | Description |
|------|--------------|
| `docker-compose.yml` | Orchestrates Nginx, Blue, Green, and Watcher services |
| `.env.example` | Environment variables (copy to `.env`) |
| `nginx.conf.template` | Nginx configuration for Blue/Green routing, failover, and /fail endpoint |
| `watcher.py` | Monitors error rates, pool switches, and sends Slack alerts |

---

### 🧭 Deployment on AWS

1. **Copy project files to your server**
```bash
scp -r ./hng13-stage3 ubuntu@<your_server_ip>:/home/ubuntu/
```

2. **SSH into your EC2 instance**
```bash
ssh ubuntu@<your_server_ip>
```

3. **Run the project**
```bash
cd hng13-stage3
docker compose up -d
```

4. **Start the watcher**
```bash
docker exec -it watcher python3 watcher.py
```

5. **Check running containers**
```bash
docker ps
```

6. **Access your services**
- Gateway → http://localhost:8080/version  
- Blue App → http://localhost:8081/version  
- Green App → http://localhost:8082/version  

---

### 📝 Notes
- Nginx forwards all headers from upstream apps (including `X-App-Pool` and `X-Release-Id`).
- Failover occurs automatically during timeouts or 5xx errors.
- The watcher monitors error rates and pool changes, sending alerts to Slack.
- Manual pool switching: modify `ACTIVE_POOL` in `.env` and reload Nginx:
```bash
docker exec -it nginx_gateway nginx -s reload
```
- Exposed URLs:
  - Gateway: [http://localhost:8080](http://localhost:8080)
  - Blue App: [http://localhost:8081](http://localhost:8081)
  - Green App: [http://localhost:8082](http://localhost:8082)

---

**Author:** Joseph Onumeguolor  
**Track:** DevOps — HNG13 Internship  