import re

from bot.helper.ext_utils.autorename_utils import (
    ask_for_rename_pattern,
    toggle_user_rename,
)


# Extracts metadata like title, season, episode, year, etc. from a file name
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


# Applies the user-defined rename pattern
def apply_rename_pattern(metadata: dict, pattern: str) -> str:
    try:
        return pattern.format(
            title=metadata.get("title", "Unknown"),
            season=metadata.get("season", "00"),
            episode=metadata.get("episode", "00"),
            year=metadata.get("year", "0000"),
            quality=metadata.get("quality", "NA"),
            audio=metadata.get("audio", "NA"),
        )
    except KeyError as e:
        return f"Invalid pattern: Missing key {e}"


# Checks if auto rename is enabled for the user
def is_autorename_enabled(user_settings: dict) -> bool:
    return user_settings.get("auto_rename_enabled", False)


# Get the user's custom rename pattern (fallback to default)
def get_user_rename_pattern(user_settings: dict) -> str:
    return user_settings.get(
        "rename_pattern",
        "{title} - S{season}E{episode} [{quality}]",
    )


# Toggle auto rename ON/OFF
def toggle_user_rename(user_settings: dict) -> dict:
    user_settings["auto_rename_enabled"] = not user_settings.get(
        "auto_rename_enabled",
        False,
    )
    return user_settings


# Ask for rename pattern input message
def ask_for_rename_pattern() -> str:
    return (
        "✍️ Please send your custom rename pattern.\n\n"
        "You can use the following placeholders:\n"
        "`{title}`, `{season}`, `{episode}`, `{year}`, `{quality}`, `{audio}`\n\n"
        "Example:\n"
        "`{title} - S{season}E{episode} [{quality}]`\n\n"
        "To reset, type `default`."
    )
