import csv
from pathlib import Path

from ..interfaces.reporter import Reporter
from ..models.report import BatchResult


class CsvReporter(Reporter):
    """Writes a flat CSV summary — one row per exam."""

    def generate(self, result: BatchResult, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"report_{result.folder.name}.csv"

        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                ["exam_id", "status", "total_score", "max_score", "errors"]
            )
            for report in result.reports:
                gr = report.grading_result
                writer.writerow(
                    [
                        report.exam_id,
                        report.status,
                        gr.total_score if gr else "",
                        gr.max_score if gr else "",
                        " | ".join(report.errors),
                    ]
                )
        return out_path
