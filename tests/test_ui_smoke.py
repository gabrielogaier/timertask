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

    def test_timer_tab_refreshes_total_for_current_date(self) -> None:
        from app import MainWindow
        from csv_store import append_record
        from database import Database

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            csv_base = root / "base"
            today = QDate.currentDate()
            today_text = today.toString("yyyy-MM-dd")
            db = Database(root / "timertask.db")
            db.set_setting("user_name", "Usuário Teste")
            db.set_setting("base_folder", str(csv_base))
            append_record(
                str(csv_base),
                {
                    "registro_id": "today-total-ui-1",
                    "usuario": "Usuário Teste",
                    "origem_registro": "TIMER",
                    "projeto": "Projeto UI",
                    "tipo_atividade": "Teste",
                    "descricao": "Registro de hoje",
                    "inicio": f"{today_text} 08:00:00",
                    "fim": f"{today_text} 08:01:30",
                    "duracao_segundos": 90,
                    "duracao_formatada": "00:01:30",
                    "observacao": "",
                    "computador": "PC",
                    "data_registro": f"{today_text} 08:01:30",
                },
            )
            window = MainWindow(db)
            window.tabs.setCurrentWidget(window.manual_tab)
            window.history_date.setDate(today.addDays(-1))
            window.today_total_label.setText("Total registrado hoje: 06:22:27")

            window.tabs.setCurrentWidget(window.timer_tab)

            self.assertEqual(window.history_date.date(), today)
            self.assertEqual(
                window.today_total_label.text(),
                "Total registrado hoje: 00:01:30",
            )
            window.force_quit = True
            window.close()

    def test_double_click_opens_complete_history_details(self) -> None:
        from app import HistoryDetailsDialog, MainWindow
        from csv_store import append_record
        from database import Database

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            csv_base = root / "base"
            db = Database(root / "timertask.db")
            db.set_setting("user_name", "Usuário Teste")
            db.set_setting("base_folder", str(csv_base))
            append_record(
                str(csv_base),
                {
                    "registro_id": "history-details-1",
                    "usuario": "Usuário Teste",
                    "origem_registro": "MANUAL",
                    "projeto": "Projeto Detalhes",
                    "tipo_atividade": "Documentação",
                    "descricao": "Descrição completa da atividade",
                    "inicio": "2026-08-03 08:00:00",
                    "fim": "2026-08-03 09:15:00",
                    "duracao_segundos": 4500,
                    "duracao_formatada": "01:15:00",
                    "observacao": "Observação completa do registro",
                    "computador": "PC-DETALHES",
                    "data_registro": "2026-08-03 09:15:01",
                },
            )
            window = MainWindow(db)
            window.history_date.setDate(QDate(2026, 8, 3))
            window.refresh_history()

            dialog = HistoryDetailsDialog(window.history_rows[0])
            self.assertEqual(
                set(dialog.value_labels),
                {key for key, _label in HistoryDetailsDialog.DETAIL_FIELDS},
            )
            self.assertEqual(dialog.value_labels["status"].text(), "ATIVO")
            self.assertEqual(
                dialog.value_labels["descricao"].text(),
                "Descrição completa da atividade",
            )
            self.assertEqual(
                dialog.value_labels["observacao"].text(),
                "Observação completa do registro",
            )
            dialog.close()

            deleted_dialog = HistoryDetailsDialog(
                {
                    **window.history_rows[0],
                    "excluido": "1",
                    "usuario_exclusao": "Gestor Teste",
                    "data_exclusao": "2026-08-03 10:00:00",
                    "motivo_exclusao": "Registro duplicado",
                    "acao_id_exclusao": "audit-details-1",
                }
            )
            self.assertEqual(deleted_dialog.value_labels["status"].text(), "EXCLUÍDO")
            self.assertEqual(
                deleted_dialog.value_labels["motivo_exclusao"].text(),
                "Registro duplicado",
            )
            deleted_dialog.close()

            with patch.object(HistoryDetailsDialog, "exec", return_value=0) as modal_exec:
                window.history_table.cellDoubleClicked.emit(0, 4)
            modal_exec.assert_called_once_with()

            window.force_quit = True
            window.close()

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
