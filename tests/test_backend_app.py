from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


class BackendAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["LANA_LOG_ROOT"] = os.path.join(self.temp_dir.name, "logs")
        os.environ["LANA_BACKUP_ROOT"] = os.path.join(self.temp_dir.name, "backups")
        os.environ["LANA_RUNTIME_ROOT"] = os.path.join(self.temp_dir.name, "runtime")
        os.environ["LANA_AUDIT_ROOT"] = os.path.join(self.temp_dir.name, "audit")
        os.environ["SYNC_FOLDER_PATH"] = os.path.join(self.temp_dir.name, "sync")
        os.environ["TELEGRAM_BOT_TOKEN"] = "dummy-token"
        os.environ["ADMIN_TELEGRAM_ID"] = "123456"
        os.environ["MCP_BEARER_TOKEN_REF"] = "MCP_BEARER_TOKEN"
        os.environ["MCP_BEARER_TOKEN"] = "super-secret"
        from backend.config import get_settings

        get_settings.cache_clear()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_health_and_status_endpoints(self) -> None:
        from backend.main import app

        with TestClient(app) as client:
            health_response = client.get("/health")
            status_response = client.get("/status")
        self.assertEqual(health_response.status_code, 200)
        self.assertTrue(health_response.json()["ok"])
        self.assertEqual(status_response.status_code, 200)
        self.assertIn("routing", status_response.json())

    def test_chat_endpoint_uses_router_and_persists_memory(self) -> None:
        from backend.main import app
        from backend.router.agent_router import ChatRouteResult

        with TestClient(app) as client:
            with patch.object(
                app.state.context.agent_router,
                "route_chat",
                new=AsyncMock(return_value=ChatRouteResult(provider="lmstudio", reply="Hallo", attempts=[])),
            ):
                response = client.post("/v1/chat", json={"prompt": "Hi Lana", "session_id": "sess-1"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["reply"], "Hallo")
        self.assertEqual(payload["provider"], "lmstudio")


if __name__ == "__main__":
    unittest.main()
