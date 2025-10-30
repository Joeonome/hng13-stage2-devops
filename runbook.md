# Runbook — Stage 3 Observability & Alerts

## Overview
This document explains what each alert means and how operators should respond.

### 1. Failover Detected
**Alert:** "Failover detected! Active pool switched from Blue → Green"  
**Action:**
- Check which container failed (`docker logs blue` or `docker ps`)
- Verify the new active pool is healthy (`curl localhost`)
- Confirm that requests are being served correctly

### 2. High Error Rate
**Alert:** "High error rate detected! X% 5xx responses"  
**Action:**
- Inspect upstream logs to identify cause of errors.
- Review application health checks.
- If needed, toggle pool manually to the stable version.

### 3. Maintenance Mode (Suppress Alerts)
To silence alerts temporarily during maintenance:
- Set `MAINTENANCE_MODE=true` in `.env`
- Restart watcher service (`docker compose restart alert_watcher`)

---

**Contact:** DevOps On-call Engineer  
**Last Updated:** October 2025
