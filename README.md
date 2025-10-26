## 🚀 Blue-Green Deployment with Nginx (Stage 2 - HNG13)

### 🧩 Overview
This setup deploys a **Blue/Green Node.js service** behind **Nginx** with automatic failover and manual toggle support.  
- **Blue** serves traffic by default.  
- **Nginx** automatically switches to **Green** if Blue becomes unhealthy.  

---

### 🌐 Server Details
| Component | Description | Port |
|------------|--------------|------|
| **Server IP** | `30.40.4.4` | — |
| **Nginx Gateway** | Public entrypoint | `8080` |
| **Blue App** | Primary (active) | `8081` |
| **Green App** | Backup (standby) | `8082` |

---

### ⚙️ How to Run

1. **Clone the repository**
   ```bash
   git clone <your_repo_url>
   cd hng13-stage2
   ```

2. **Create the `.env` file**
   ```bash
   cp .env.example .env
   ```

3. **Pull the required image**
   ```bash
   docker pull yimikaade/wonderful:devops-stage-two
   ```

4. **Start the stack**
   ```bash
   docker compose up -d
   ```

---

### 🧪 Testing Failover

#### ✅ Step 1: Confirm Blue is active
```bash
curl -i http://localhost:8080/version
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
curl -i http://localhost:8080/version
```
Response should now include:
```
X-App-Pool: green
```

#### 🔄 Step 4: Restore Blue
```bash
curl -X POST http://localhost:8081/chaos/stop
curl -i http://localhost:8080/version
```
Response should again include:
```
X-App-Pool: blue
```

---

### 📂 File Structure

| File | Description |
|------|--------------|
| `docker-compose.yml` | Orchestrates Nginx, Blue, and Green services |
| `.env.example` | Environment variables (to be copied to `.env`) |
| `nginx.conf.template` | Nginx configuration for Blue/Green routing and failover |

---

### 🧭 Deployment on AWS

1. **Copy project files to your server**
   ```bash
   scp -r ./Hng13-stage2-devops ubuntu@30.40.4.4:/home/ubuntu/
   ```

2. **SSH into your EC2 instance**
   ```bash
   ssh ubuntu@30.40.4.4
   ```

3. **Run the project**
   ```bash
   cd Hng13-stage2-devops
   docker compose up -d
   ```

4. **Check running containers**
   ```bash
   docker ps
   ```

5. **Access your services**
   - Gateway → http://30.40.4.4:8080/version  
   - Blue App → http://30.40.4.4:8081/version  
   - Green App → http://30.40.4.4:8082/version  

---

### 📝 Notes
- Nginx forwards all headers from the upstream apps (including `X-App-Pool` and `X-Release-Id`).
- Failover occurs automatically during timeouts or 5xx errors.
- For **manual switching**, modify `ACTIVE_POOL` in `.env` and reload Nginx:
  ```bash
  docker exec -it nginx_gateway nginx -s reload
  ```
- Exposed URLs:
  - Gateway: [http://30.40.4.4:8080](http://30.40.4.4:8080)
  - Blue App: [http://30.40.4.4:8081](http://30.40.4.4:8081)
  - Green App: [http://30.40.4.4:8082](http://30.40.4.4:8082)

---

**Author:** Joseph Onumeguolor  
**Track:** DevOps — HNG13 Internship  