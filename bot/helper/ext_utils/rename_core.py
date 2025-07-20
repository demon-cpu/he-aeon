from bot.modules.telegram_helper.db_mongo import get_user_settings_db


async def get_user_settings(user_id):
    return await get_user_settings_db(user_id)


async def is_autorename_enabled(settings):
    return settings.get("autorename", False)


async def extract_metadata(filename):
    import re

    name = filename.rsplit(".", 1)[0]
    pattern = r"(S\d{2})[\s._-]?(E\d{2})"
    match = re.search(pattern, name, re.IGNORECASE)
    season = episode = quality = None
    if match:
        season = match.group(1).upper()
        episode = match.group(2).upper()
    quality_match = re.search(r"\b(480p|720p|1080p|4k)\b", name, re.IGNORECASE)
    if quality_match:
        quality = quality_match.group(1)
    return {
        "filename": name,
        "season": season,
        "episode": episode,
        "quality": quality,
    }


async def apply_rename_pattern(pattern, metadata):
    name = pattern
    for key, value in metadata.items():
        if value:
            name = name.replace(f"{{{key}}}", value)
        else:
            name = name.replace(f"{{{key}}}", "")
    return name.strip().replace("..", ".").replace("__", "_").replace("  ", " ")
