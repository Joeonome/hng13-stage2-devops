## Blue-Green Deployment with Nginx (Stage 2 - HNG13)

### Overview
This setup deploys a Blue/Green Node.js service behind Nginx with automatic failover. Blue serves traffic by default, and Nginx switches to Green when Blue fails.

### Server Details
- **Public IP:** [your_server_IP]
- **Nginx Port:** 8080
- **Blue App Port:** 8081
- **Green App Port:** 8082

### How to Run
1. Clone the repository.
2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
3. Pull the required image:
   ```bash
   docker pull yimikaade/wonderful:devops-stage-two
   ```
4. Start the stack:
   ```bash
   docker compose up -d
   ```

### Testing Failover
1. Confirm Blue is active:
   ```bash
   curl -i http://localhost:8080/version
   ```
   Response should include `X-App-Pool: blue`
2. Simulate Blue failure:
   ```bash
   curl -X POST http://localhost:8080/chaos/start?mode=error
   ```
3. Check failover:
   ```bash
   curl -i http://localhost:8080/version
   ```
   Response should include `X-App-Pool: green`
4. Restore:
   ```bash
curl -X POST http://localhost:8080/chaos/stop
    ```
    ```bash
curl -i http://localhost:8080/version
   ```
   Response should include `X-App-Pool: blue`

### Files
- `docker-compose.yml` → orchestrates services
- `.env.example` → environment variables
- `nginx.conf.template` → Nginx config with failover

### Notes
- Nginx forwards all headers from the app.
- Failover is handled automatically within the same request.
- Modify `ACTIVE_POOL` in `.env` and reload Nginx if you want manual switching:
  ```bash
  docker exec -it nginx_gateway nginx -s reload
  ```
