Grafana dashboard and provisioning notes

- Dashboard: `grafana/dashboards/products-dashboard.json`
  - Sections: RED, USE, Golden Signals, Live Tail logs (Loki)
  - Default time range: last 15 minutes

- Loki datasource provisioning:
  - File: `observability/grafana/provisioning/datasources/loki.yaml`
  - The datasource is provisioned with `uid: loki` and `url: http://loki:3100` so the dashboard can reference it by UID.
  - If your Grafana instance uses a different Loki datasource UID, update `products-dashboard.json` and change the `datasource.uid` to the correct value.

- Live tail panel:
  - Uses a logs panel with target `{job="varlogs"}`. Ensure your `observability/promtail-config.yaml` labels logs with `job: varlogs` or update the query to match your labels (for example `{app="products-api"}`).

- Running locally:
  - Start the stack: `docker compose up --build` (this will provision Grafana datasources and dashboards automatically).
  - Grafana UI: http://localhost:3000 (default user: admin / admin)

- Notes on Loki permissions:
  - On Docker Desktop (Windows/Mac) the compose file runs Loki as root to avoid permission issues with named volumes. For production or Linux hosts, prefer running Loki as non-root and set correct volume ownership or use an init step to chown volumes.
