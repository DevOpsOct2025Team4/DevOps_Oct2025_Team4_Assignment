# Observability & Monitoring Guide - Prometheus & Grafana

## Overview

This guide explains the monitoring and observability implementation using Prometheus for metrics collection and Grafana for visualization.

## Components

### 1. **Prometheus**

- **Port**: 9090
- **Purpose**: Time-series database for collecting and storing metrics
- **Config**: `prometheus.yml`
- **Access**: http://localhost:9090

### 2. **Grafana**

- **Port**: 3000
- **Purpose**: Visualization and dashboard creation
- **Default Login**: admin / admin
- **Access**: http://localhost:3000

### 3. **Flask Metrics Exporter**

- **Port**: 5000 (same as Flask app)
- **Metrics Endpoint**: http://localhost:5000/metrics
- **Metrics Exported**:
  - `flask_http_requests_total`: Total HTTP requests (labeled by method, endpoint, status)
  - `flask_http_requests_active`: Currently active HTTP requests (gauge)
  - `flask_http_request_duration_seconds`: Request duration histogram (labeled by method, endpoint)

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

### 2. Access Prometheus

- Open: http://localhost:9090
- Check targets: http://localhost:9090/targets
- Query metrics: http://localhost:9090/graph

### 3. Access Grafana

- Open: http://localhost:3000
- Login: admin / admin
- Change password when prompted
- Dashboard automatically provisioned: "Flask App Monitoring"

## Available Prometheus Queries

### Key Metrics to Monitor

```promql
# Request rate (requests per second over last 5 minutes)
rate(flask_http_requests_total[5m])

# Total requests by status
sum(flask_http_requests_total) by (status)

# Active requests
flask_http_requests_active

# Request success rate
sum(rate(flask_http_requests_total{status=~"2.."}[5m])) / sum(rate(flask_http_requests_total[5m]))

# HTTP 4xx errors rate
rate(flask_http_requests_total{status=~"4.."}[5m])

# HTTP 5xx errors rate
rate(flask_http_requests_total{status=~"5.."}[5m])

# Requests by endpoint
sum(flask_http_requests_total) by (endpoint)

# Requests by method
sum(flask_http_requests_total) by (method)
```

## Dashboard Panels

The pre-configured "Flask App Monitoring" dashboard includes:

1. **HTTP Request Rate (5m)** - Line chart showing request throughput
2. **Active HTTP Requests** - Gauge showing current concurrent requests
3. **Total HTTP Requests by Status** - Stacked bar chart showing requests distribution

## Configuration Files

### prometheus.yml

- Defines scrape intervals (how often to collect metrics)
- Configures Flask app as a target
- Default scrape interval: 15 seconds globally, 10 seconds for Flask

### Grafana Provisioning

- **datasources/prometheus.yml**: Configures Prometheus as data source
- **dashboards/dashboards.yml**: Enables dashboard provisioning
- **dashboards/flask-monitoring.json**: Pre-built dashboard definition

## Monitoring Best Practices

### 1. **Alert Rules** (Optional Enhancement)

Create `prometheus-alerts.yml` for automated alerting:

```yaml
groups:
  - name: flask_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(flask_http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High 5xx error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, flask_http_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "High request latency detected"
```

### 2. **Custom Metrics** (Future Enhancement)

Add custom metrics to track business logic:

```python
from prometheus_client import Counter, Gauge

# Example: Track file uploads
file_upload_counter = Counter(
    'file_uploads_total',
    'Total file uploads',
    ['status']
)

# Example: Track storage size
storage_size_gauge = Gauge(
    'storage_size_bytes',
    'Current storage size in bytes'
)
```

### 3. **Retention Policies**

- Prometheus stores data in `/prometheus` volume
- Default retention: 15 days
- Modify in docker-compose.yml: `--storage.tsdb.retention.time=30d`

## Troubleshooting

### Prometheus not scraping Flask app

1. Check Flask app is running: `curl http://localhost:5000/metrics`
2. Verify `prometheus.yml` target configuration
3. Check Prometheus logs: `docker logs <prometheus-container>`
4. Restart: `docker-compose restart prometheus`

### Grafana not showing data

1. Verify data source: Grafana → Configuration → Data Sources
2. Test connection to Prometheus
3. Check dashboard queries in Grafana UI
4. Ensure Prometheus has collected metrics (wait 30+ seconds)

### Metrics not appearing

1. Generate traffic: `curl http://localhost:5000/api/health`
2. Wait for scrape interval (default 10s for Flask)
3. Check metrics endpoint: `curl http://localhost:5000/metrics`

## Next Steps for Production

1. **Enable Authentication**: Set up OAuth/LDAP in Grafana
2. **Persistent Storage**: Use named volumes or NFS
3. **Alert Management**: Integrate with Slack/PagerDuty
4. **Service Discovery**: Use Consul or Kubernetes service discovery
5. **Log Aggregation**: Add ELK stack or Loki for centralized logging
6. **Distributed Tracing**: Add Jaeger for request tracing

## References

- Prometheus Documentation: https://prometheus.io/docs/
- Grafana Documentation: https://grafana.com/docs/
- Prometheus Client Library (Python): https://github.com/prometheus/client_python
- PromQL Cheat Sheet: https://promlabs.com/promql-cheat-sheet/
