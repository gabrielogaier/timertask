from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from csv_store import append_record, monthly_csv_path, read_records_for_date


class CsvStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_folder = self.temp_dir.name
        self.record = {
            "registro_id": "fixed-uuid",
            "usuario": "Usuário Teste",
            "origem_registro": "MANUAL",
            "projeto": "Projeto Público",
            "tipo_atividade": "Documentação",
            "descricao": "Criar README",
            "inicio": "2026-07-11 10:00:00",
            "fim": "2026-07-11 10:30:00",
            "duracao_segundos": 1800,
            "duracao_formatada": "00:30:00",
            "observacao": "Concluído",
            "computador": "PC-TESTE",
            "data_registro": "2026-07-11 10:30:00",
        }

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_append_is_idempotent(self) -> None:
        first_path = append_record(self.base_folder, self.record)
        second_path = append_record(self.base_folder, self.record)
        self.assertEqual(first_path, second_path)

        with first_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            rows = list(csv.DictReader(csv_file, delimiter=";"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["registro_id"], "fixed-uuid")
        self.assertEqual(rows[0]["origem_registro"], "MANUAL")

    def test_read_records_for_selected_date(self) -> None:
        append_record(self.base_folder, self.record)
        rows = read_records_for_date(
            self.base_folder,
            self.record["usuario"],
            datetime(2026, 7, 11),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["projeto"], "Projeto Público")

    def test_monthly_path_is_separated_by_user(self) -> None:
        path = monthly_csv_path(
            self.base_folder,
            "Usuário Teste",
            datetime(2026, 7, 11),
        )
        self.assertEqual(path.name, "2026-07.csv")
        self.assertEqual(path.parent.name, "Usuário_Teste")
        self.assertEqual(path.parent.parent.name, "registros")


if __name__ == "__main__":
    unittest.main()
