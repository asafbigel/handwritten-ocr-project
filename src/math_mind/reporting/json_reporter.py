import json
from pathlib import Path

from ..interfaces.reporter import Reporter
from ..models.report import BatchResult


class JsonReporter(Reporter):
    """Writes a detailed JSON report including per-question breakdown."""

    def generate(self, result: BatchResult, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"report_{result.folder.name}.json"

        data = {
            "folder": str(result.folder),
            "processed_at": result.processed_at.isoformat(),
            "total": result.total,
            "graded": result.graded,
            "failed": result.failed,
            "reports": [
                {
                    "exam_id": r.exam_id,
                    "image_path": str(r.image_path),
                    "status": r.status,
                    "grading_result": (
                        r.grading_result.model_dump() if r.grading_result else None
                    ),
                    "errors": r.errors,
                }
                for r in result.reports
            ],
        }
        out_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return out_path
