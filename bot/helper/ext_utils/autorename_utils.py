import re

async def extract_metadata(filename: str) -> dict:
    metadata = {
        "title": "Unknown",
        "season": "00",
        "episode": "00",
        "year": "0000",
        "quality": "NA",
        "audio": "NA",
    }

    name = filename.rsplit(".", 1)[0]

    title_match = re.match(r"^(.*?)(S\d+E\d+|$)", name, re.IGNORECASE)
    if title_match:
        metadata["title"] = title_match.group(1).replace(".", " ").strip()

    se_match = re.search(r"[Ss](\d+)[Ee](\d+)", name)
    if se_match:
        metadata["season"] = se_match.group(1).zfill(2)
        metadata["episode"] = se_match.group(2).zfill(2)

    year_match = re.search(r"(19|20)\d{2}", name)
    if year_match:
        metadata["year"] = year_match.group(0)

    quality_match = re.search(r"(480p|720p|1080p|2160p|4K)", name, re.IGNORECASE)
    if quality_match:
        metadata["quality"] = quality_match.group(0).upper()

    audio_match = re.search(r"(5\.1|2\.0|Atmos|AAC|DDP)", name, re.IGNORECASE)
    if audio_match:
        metadata["audio"] = audio_match.group(0).upper()

    return metadata

def apply_rename_pattern(metadata: dict, pattern: str) -> str:
    return pattern.format(
        title=metadata.get("title", "Unknown"),
        season=metadata.get("season", "00"),
        episode=metadata.get("episode", "00"),
        year=metadata.get("year", "0000"),
        quality=metadata.get("quality", "NA"),
        audio=metadata.get("audio", "NA"),
    )

def is_autorename_enabled(user_settings: dict) -> bool:
    return user_settings.get("auto_rename_enabled", False)

def toggle_user_rename(user_settings: dict, state: bool) -> dict:
    """Toggle the auto rename setting for a user."""
    user_settings["auto_rename_enabled"] = state
    return user_settings
