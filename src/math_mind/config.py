from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment / .env file.

    Per-folder crop region design
    ─────────────────────────────
    Each input folder (keyed by its directory name) may define its own
    crop region — the rectangle that is blacked-out to anonymise student
    identity information.  Region format: (x, y, width, height) in pixels.

    Priority:
      1. crop_regions[folder_name]   — exact folder match
      2. default_crop_region          — fallback
      3. None                         — skip anonymisation region (warn)

    .env example
    ────────────
      CROP_REGIONS={"10A": [0, 0, 300, 80], "10B": [10, 5, 280, 70]}
      DEFAULT_CROP_REGION=[0, 0, 300, 80]
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Gemini ---
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    # --- Per-folder anonymisation regions ---
    # Key   = exact folder name (stem)
    # Value = (x, y, width, height) in pixels
    crop_regions: dict[str, tuple[int, int, int, int]] = Field(default_factory=dict)

    # Used when the folder name is not present in crop_regions
    default_crop_region: tuple[int, int, int, int] | None = None

    # --- I/O ---
    input_dir: Path = Path("input")
    output_dir: Path = Path("output")
    report_formats: list[str] = Field(default=["csv", "json"])

    # --- Rate limiting ---
    rpm_limit: int = 15
    rpd_limit: int = 1500

    def get_crop_region(self, folder_name: str) -> tuple[int, int, int, int] | None:
        """Return the crop region for *folder_name*, falling back to the default."""
        return self.crop_regions.get(folder_name, self.default_crop_region)
