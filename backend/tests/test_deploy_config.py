"""Deploy-config sanity checks.

Deploy artifacts (compose files, Dockerfile, Caddyfile) aren't exercised by
the app test suite, so these guard against silent typos: valid YAML, expected
services, prod target wired, secrets file gitignored.
"""
from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO = Path(__file__).resolve().parent.parent.parent


def _load(name: str) -> dict:
    return yaml.safe_load((REPO / name).read_text(encoding="utf-8"))


def test_dev_compose_targets_dev_stage():
    compose = _load("docker-compose.yml")
    for svc in ("backend", "worker"):
        assert compose["services"][svc]["build"]["target"] == "dev", svc


def test_prod_compose_has_expected_services():
    compose = _load("docker-compose.prod.yml")
    services = compose["services"]
    for svc in ("db", "redis", "backend", "worker", "caddy", "backup"):
        assert svc in services, f"prod compose missing {svc}"


def test_prod_backend_uses_prod_target_and_production_env():
    compose = _load("docker-compose.prod.yml")
    backend = compose["services"]["backend"]
    assert backend["build"]["target"] == "prod"
    assert backend["environment"]["EQUALISE_ENV"] == "production"
    worker = compose["services"]["worker"]
    assert worker["build"]["target"] == "prod"


def test_prod_caddy_publishes_tls_ports():
    compose = _load("docker-compose.prod.yml")
    ports = compose["services"]["caddy"]["ports"]
    published = {p.split(":")[0] for p in ports}
    assert {"80", "443"} <= published


def test_backend_dockerfile_defines_dev_and_prod_targets():
    text = (REPO / "backend" / "Dockerfile").read_text(encoding="utf-8")
    assert "AS base" in text
    assert "AS dev" in text
    assert "AS prod" in text
    assert "gunicorn" in text
    assert "USER app" in text  # prod runs non-root


def test_caddyfile_proxies_api_and_serves_spa():
    text = (REPO / "infra" / "caddy" / "Caddyfile").read_text(encoding="utf-8")
    assert "reverse_proxy backend:8000" in text
    assert "try_files" in text  # SPA fallback


def test_env_prod_is_gitignored():
    gi = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert ".env.prod" in gi
    # but the example template is allowed
    assert "!.env.prod.example" in gi


def test_backup_script_present_and_executable_intent():
    script = REPO / "infra" / "backup" / "backup.sh"
    assert script.exists()
    text = script.read_text(encoding="utf-8")
    assert "pg_dump" in text
    assert "RETENTION" in text
