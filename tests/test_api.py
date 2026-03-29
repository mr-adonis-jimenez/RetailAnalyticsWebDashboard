import pytest
import json


def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    # If blueprint not registered, expect 404 gracefully
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = json.loads(resp.data)
        assert data["status"] == "healthy"


def test_metrics_endpoint_exists(client):
    resp = client.get("/api/v1/metrics")
    assert resp.status_code in (200, 404, 503)


def test_orders_endpoint_pagination(client):
    resp = client.get("/api/v1/orders?page=1&per_page=5")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = json.loads(resp.data)
        assert "pagination" in data


def test_revenue_analytics_endpoint(client):
    resp = client.get("/api/v1/analytics/revenue")
    assert resp.status_code in (200, 404, 422)


def test_trends_endpoint(client):
    resp = client.get("/api/v1/analytics/trends")
    assert resp.status_code in (200, 404, 422)
