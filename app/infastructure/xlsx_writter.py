from __future__ import annotations

from pathlib import Path
from typing import Iterable

from openpyxl import Workbook

from app.application.report_service import ReportRaw


def write_report_xlsx(rows: Iterable[ReportRaw], output_path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Report"

    ws.append(["lemma", "total_count", "per_line_counts"])

    for row in rows:
        per_line_str = ",".join(str(x) for x in row.per_line_counts)
        ws.append([row.lemma, row.total_count, per_line_str])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)