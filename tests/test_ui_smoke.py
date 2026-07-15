from __future__ import annotations

import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_TEST_LOCALAPPDATA = tempfile.mkdtemp(prefix="timertask-user-ui-")
os.environ["LOCALAPPDATA"] = _TEST_LOCALAPPDATA

try:
    from PySide6.QtCore import QDate
    from PySide6.QtWidgets import QApplication, QMessageBox
except ImportError:  # Permite executar os testes de dados sem a dependência gráfica.
    QApplication = None


@unittest.skipIf(QApplication is None, "PySide6 não está instalado")
class UiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.qt_app = QApplication.instance() or QApplication([])

    def test_delete_preserves_original_and_creates_audit(self) -> None:
        from app import MainWindow
        from csv_store import append_record
        from database import Database

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            csv_base = root / "base"
            db = Database(root / "timertask.db")
            db.set_setting("user_name", "Usuário Teste")
            db.set_setting("base_folder", str(csv_base))
            record = {
                "registro_id": "delete-flow-1",
                "usuario": "Usuário Teste",
                "origem_registro": "MANUAL",
                "projeto": "Projeto Fluxo",
                "tipo_atividade": "Documentação",
                "descricao": "Lançamento incorreto",
                "inicio": "2026-07-13 13:00:00",
                "fim": "2026-07-13 14:00:00",
                "duracao_segundos": 3600,
                "duracao_formatada": "01:00:00",
                "observacao": "",
                "computador": "PC-TESTE",
                "data_registro": "2026-07-13 14:00:00",
            }
            original_path = append_record(str(csv_base), record)
            window = MainWindow(db)
            window.history_date.setDate(QDate(2026, 7, 13))
            window.refresh_history()
            self.assertEqual(window.history_table.rowCount(), 1)
            window.history_table.selectRow(0)

            with (
                patch("app.QInputDialog.getMultiLineText", return_value=("Registro duplicado", True)),
                patch("app.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes),
                patch("app.QMessageBox.information"),
            ):
                window.delete_selected_history_record()

            with original_path.open("r", newline="", encoding="utf-8-sig") as handle:
                self.assertEqual(len(list(csv.DictReader(handle, delimiter=";"))), 1)

            actions = db.list_audit_actions()
            self.assertEqual(len(actions), 1)
            self.assertEqual(actions[0]["status"], "SINCRONIZADO")
            self.assertEqual(actions[0]["data"]["motivo"], "Registro duplicado")

            window.history_status_filter.setCurrentText("Excluídos")
            window.refresh_history()
            self.assertEqual(window.history_table.rowCount(), 1)
            self.assertEqual(window.history_table.item(0, 7).text(), "EXCLUÍDO")
            self.assertEqual(window.history_total_label.text(), "Total válido: 00:00:00")
            window.force_quit = True
            window.close()


if __name__ == "__main__":
    unittest.main()
