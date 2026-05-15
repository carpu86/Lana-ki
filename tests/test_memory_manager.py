from __future__ import annotations

import os
import tempfile
import unittest


class MemoryManagerTests(unittest.TestCase):
    def test_remember_recall_and_forget(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["LANA_LOG_ROOT"] = os.path.join(temp_dir, "logs")
            os.environ["LANA_BACKUP_ROOT"] = os.path.join(temp_dir, "backups")
            os.environ["LANA_RUNTIME_ROOT"] = os.path.join(temp_dir, "runtime")
            os.environ["LANA_AUDIT_ROOT"] = os.path.join(temp_dir, "audit")
            os.environ["SYNC_FOLDER_PATH"] = os.path.join(temp_dir, "sync")
            os.environ["TELEGRAM_BOT_TOKEN"] = "dummy-token"
            os.environ["ADMIN_TELEGRAM_ID"] = "123456"
            os.environ["MCP_BEARER_TOKEN_REF"] = "MCP_BEARER_TOKEN"
            os.environ["MCP_BEARER_TOKEN"] = "super-secret"

            from backend.config import get_settings

            get_settings.cache_clear()

            from backend.memory.manager import MemoryManager

            manager = MemoryManager(get_settings())
            entry = manager.remember("Lana merkt sich etwas", agent="lana", type="note", tags=["test"])
            results = manager.recall("merkt")
            deleted = manager.forget_before(days=0)

            self.assertIsNotNone(entry.id)
            self.assertGreaterEqual(len(results), 1)
            self.assertGreaterEqual(deleted, 1)


if __name__ == "__main__":
    unittest.main()
