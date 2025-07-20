from bot import MongoClient

# MongoDB collection
RENAMER_DB = MongoClient.auto_renamer

# Default format
DEFAULT_FORMAT = "{title} S{season}E{episode} [{quality}][{audio}] ({year})"


# Save or update user renaming format
async def set_user_format(user_id: int, format_string: str):
    await RENAMER_DB.update_one(
        {"_id": user_id},
        {"$set": {"format": format_string, "enabled": True}},
        upsert=True,
    )


# Disable auto renaming
async def disable_user_renamer(user_id: int):
    await RENAMER_DB.update_one(
        {"_id": user_id},
        {"$set": {"enabled": False}},
    )


# Get current format (returns format string or None if disabled)
async def get_user_format(user_id: int):
    doc = await RENAMER_DB.find_one({"_id": user_id})
    if doc and doc.get("enabled", False):
        return doc.get("format", DEFAULT_FORMAT)
    return None


# Format renaming based on user input + extracted metadata
def format_filename(format_string, metadata: dict, ext: str = ".mkv"):
    try:
        formatted = format_string.format(**metadata)
        return f"{formatted}{ext}"
    except KeyError:
        return None


# 🔁 STEP 3: Auto Rename Function
async def apply_rename_pattern(message, original_name: str) -> str:
    import os
    import re

    from bot.helper.ext_utils.rename_utils import format_filename, get_user_format

    user_id = message.from_user.id
    fmt = await get_user_format(user_id)
    if not fmt:
        return original_name

    # Try to extract metadata from original_name
    pattern = r"(.*?)[.\s_-]*[Ss](\d+)[.\s_-]*[Ee](\d+).*?(\d{3,4}p)?[.\s_-]*([a-zA-Z0-9]+)?"
    match = re.search(pattern, original_name)
    if not match:
        return original_name

    metadata = {
        "title": match.group(1).replace(".", " ").replace("_", " ").strip(),
        "season": match.group(2).zfill(2),
        "episode": match.group(3).zfill(2),
        "quality": match.group(4) or "720p",
        "audio": match.group(5) or "DDP",
        "year": "2024",
    }

    ext = os.path.splitext(original_name)[-1]
    renamed = format_filename(fmt, metadata, ext)
    return renamed or original_name
