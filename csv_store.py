from __future__ import annotations

import csv
import os
import re
import shutil
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator


CSV_FIELDS = [
    "registro_id",
    "usuario",
    "origem_registro",
    "projeto",
    "tipo_atividade",
    "descricao",
    "inicio",
    "fim",
    "duracao_segundos",
    "duracao_formatada",
    "observacao",
    "computador",
    "data_registro",
]


def safe_folder_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9À-ÿ._-]+", "_", value.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "usuario"


def monthly_csv_path(base_folder: str, user_name: str, reference: datetime) -> Path:
    return (
        Path(base_folder)
        / "registros"
        / safe_folder_name(user_name)
        / f"{reference:%Y-%m}.csv"
    )


def test_write_access(base_folder: str) -> None:
    base = Path(base_folder)
    base.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="timertask_test_", suffix=".tmp", dir=base)
    os.close(fd)
    Path(temporary_name).unlink(missing_ok=True)


@contextmanager
def _csv_lock(file_path: Path, timeout_seconds: float = 8.0) -> Iterator[None]:
    """Evita duas gravações simultâneas no mesmo CSV, inclusive em pasta de rede."""
    lock_path = file_path.with_suffix(file_path.suffix + ".lock")
    deadline = time.monotonic() + timeout_seconds
    descriptor: int | None = None

    while descriptor is None:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, f"pid={os.getpid()}\ncreated={time.time()}\n".encode("ascii"))
        except FileExistsError:
            try:
                # Remove somente travas claramente abandonadas.
                if time.time() - lock_path.stat().st_mtime > 120:
                    lock_path.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise TimeoutError(f"O arquivo está em uso por outra gravação: {file_path.name}")
            time.sleep(0.15)

    try:
        yield
    finally:
        try:
            if descriptor is not None:
                os.close(descriptor)
        finally:
            lock_path.unlink(missing_ok=True)


def _record_exists(file_path: Path, record_id: str) -> bool:
    if not file_path.exists() or file_path.stat().st_size == 0:
        return False
    with file_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        return any(row.get("registro_id") == record_id for row in reader)


def _ensure_csv_schema(file_path: Path) -> list[str]:
    """
    Acrescenta novas colunas ao cabeçalho de um CSV antigo preservando todas as linhas.

    A migração é feita sob a trava do CSV, cria um backup único e substitui o arquivo
    apenas depois que o temporário foi gravado completamente.
    """
    if not file_path.exists() or file_path.stat().st_size == 0:
        return list(CSV_FIELDS)

    with file_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        existing_fields = [field for field in (reader.fieldnames or []) if field]
        rows = list(reader)

    target_fields = list(CSV_FIELDS)
    target_fields.extend(field for field in existing_fields if field not in target_fields)
    if existing_fields == target_fields:
        return target_fields

    backup_path = file_path.with_suffix(file_path.suffix + ".pre-origem-registro.bak")
    if not backup_path.exists():
        shutil.copy2(file_path, backup_path)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{file_path.stem}_schema_",
        suffix=".tmp",
        dir=file_path.parent,
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)

    try:
        with temporary_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=target_fields,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in rows:
                # Registros antigos, sem a coluna de origem, eram gerados pelo timer.
                row["origem_registro"] = row.get("origem_registro") or "TIMER"
                writer.writerow(row)
            csv_file.flush()
            os.fsync(csv_file.fileno())
        os.replace(temporary_path, file_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return target_fields


def append_record(base_folder: str, record: dict[str, Any]) -> Path:
    """
    Acrescenta uma linha sem duplicar o registro.

    O UUID em registro_id torna a operação idempotente: se a linha já existir,
    uma nova tentativa é considerada concluída, mas não grava outra linha.
    """
    if not base_folder.strip():
        raise ValueError("A pasta compartilhada não está configurada")

    reference = datetime.fromisoformat(str(record["inicio"]))
    file_path = monthly_csv_path(base_folder, str(record["usuario"]), reference)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    record_to_write = dict(record)
    record_to_write["origem_registro"] = (
        str(record_to_write.get("origem_registro") or "TIMER").strip().upper()
    )

    with _csv_lock(file_path):
        file_exists = file_path.exists() and file_path.stat().st_size > 0
        fieldnames = _ensure_csv_schema(file_path) if file_exists else list(CSV_FIELDS)

        if file_exists and _record_exists(file_path, str(record_to_write["registro_id"])):
            return file_path

        with file_path.open("a", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
                extrasaction="ignore",
            )
            if not file_exists:
                writer.writeheader()
            writer.writerow(record_to_write)
            csv_file.flush()
            os.fsync(csv_file.fileno())

    return file_path


def read_records_for_date(
    base_folder: str,
    user_name: str,
    selected_date: datetime,
) -> list[dict[str, str]]:
    if not base_folder.strip():
        return []
    file_path = monthly_csv_path(base_folder, user_name, selected_date)
    if not file_path.exists():
        return []

    selected_prefix = selected_date.strftime("%Y-%m-%d")
    with file_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        rows = [row for row in reader if row.get("inicio", "").startswith(selected_prefix)]

    for row in rows:
        row["origem_registro"] = row.get("origem_registro") or "TIMER"
    rows.sort(key=lambda row: row.get("inicio", ""))
    return rows
