from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import Database, FAILED_STATUS, SYNCED_STATUS


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp_dir.name) / "timertask.db")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_default_catalogs_are_created(self) -> None:
        projects = self.db.list_items("projects", active_only=True)
        activity_types = self.db.list_items("activity_types", active_only=True)
        self.assertGreaterEqual(len(projects), 1)
        self.assertGreaterEqual(len(activity_types), 1)

    def test_task_record_lifecycle_keeps_local_history_after_sync(self) -> None:
        record = {
            "registro_id": "record-1",
            "usuario": "Teste",
            "origem_registro": "TIMER",
            "projeto": "Geral",
            "tipo_atividade": "Teste",
            "descricao": "Validação",
            "inicio": "2026-07-11 08:00:00",
            "fim": "2026-07-11 09:00:00",
            "duracao_segundos": 3600,
            "duracao_formatada": "01:00:00",
            "observacao": "",
            "computador": "TESTE",
            "data_registro": "2026-07-11 09:00:00",
        }
        self.db.add_task_record(record)
        self.assertEqual(self.db.pending_count(), 1)

        self.db.mark_task_error("record-1", "Falha simulada")
        pending = self.db.list_task_records(pending_only=True)[0]
        self.assertEqual(pending["status"], FAILED_STATUS)
        self.assertEqual(pending["attempts"], 1)

        self.db.mark_task_synced("record-1")
        self.assertEqual(self.db.pending_count(), 0)
        records = self.db.list_task_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], SYNCED_STATUS)

    def test_pending_records_are_migrated_without_deletion(self) -> None:
        db_path = Path(self.temp_dir.name) / "legacy.db"
        connection = sqlite3.connect(db_path)
        try:
            connection.execute(
                """
                CREATE TABLE pending_records (
                    record_id TEXT PRIMARY KEY, data_json TEXT NOT NULL, created_at TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'PENDENTE', last_attempt_at TEXT NOT NULL DEFAULT ''
                )
                """
            )
            connection.execute(
                "INSERT INTO pending_records VALUES (?, ?, ?, 2, ?, 'FALHA', ?)",
                ("legacy-1", '{"registro_id":"legacy-1","usuario":"Teste"}', "2026-08-01 10:00:00", "Rede", "2026-08-01 10:01:00"),
            )
            connection.commit()
        finally:
            connection.close()
        migrated = Database(db_path)
        self.assertEqual(len(migrated.list_task_records()), 1)
        self.assertEqual(migrated.list_task_records()[0]["status"], FAILED_STATUS)
        verification_connection = sqlite3.connect(db_path)
        try:
            self.assertEqual(
                verification_connection.execute("SELECT COUNT(*) FROM pending_records").fetchone()[0],
                1,
            )
        finally:
            verification_connection.close()

    def test_import_ignores_existing_record_ids(self) -> None:
        record = {"registro_id": "csv-1", "usuario": "Teste", "inicio": "2026-08-01 09:00:00"}
        self.assertEqual(self.db.import_task_records([record]), 1)
        self.assertEqual(self.db.import_task_records([record]), 0)
        self.assertEqual(self.db.list_task_records()[0]["status"], SYNCED_STATUS)

class AuditDatabaseTests(unittest.TestCase):
    def test_audit_action_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            db = Database(Path(temporary) / "timertask.db")
            action = {
                "acao_id": "action-1",
                "registro_id": "record-1",
                "acao": "EXCLUIR",
                "usuario_acao": "Teste",
                "inicio": "2026-07-11 08:00:00",
            }
            db.add_audit_action(action)
            self.assertEqual(db.audit_pending_count(), 1)
            db.mark_audit_error("action-1", "Rede indisponível")
            pending = db.list_audit_actions(pending_only=True)[0]
            self.assertEqual(pending["status"], FAILED_STATUS)
            db.mark_audit_synced("action-1")
            self.assertEqual(db.audit_pending_count(), 0)
            self.assertEqual(len(db.list_audit_actions()), 1)


if __name__ == "__main__":
    unittest.main()
