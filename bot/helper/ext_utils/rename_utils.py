from bot import MongoClient

from .media_utils import extract_metadata

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


# Check if autorename is enabled for the user
async def is_autorename_enabled(user_id: int) -> bool:
    doc = await RENAMER_DB.find_one({"_id": user_id})
    return bool(doc and doc.get("enabled", False))


# Main handler to apply renaming pattern using user format and media metadata
async def apply_rename_pattern(message, original_name: str):
    user_id = message.from_user.id
    format_string = await get_user_format(user_id)

    if not format_string:
        return original_name

    metadata = await extract_metadata(message, original_name)
    if not metadata:
        return original_name

    new_name = format_filename(format_string, metadata)
    return new_name or original_name
