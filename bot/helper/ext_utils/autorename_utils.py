import re


async def ask_for_rename_pattern(client, message):
    await message.reply_text(
        "Please send the auto-rename pattern.\n\n"
        "You can use these placeholders:\n"
        "`{title}`, `{season}`, `{episode}`, `{year}`, `{quality}`, `{audio}`, `{ext}`\n\n"
        "**Example:**\n`{title} - S{season}E{episode} - {quality}.{ext}`"
    )
    response = await client.listen(message.chat.id)
    return response.text.strip()


def is_autorename_enabled(user_settings: dict) -> bool:
    """
    Checks if auto rename is enabled for the user.
    """
    return user_settings.get("auto_rename_enabled", False)


def extract_extension(filename: str) -> str:
    if "." in filename:
        return filename.rsplit(".", 1)[-1]
    return ""


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


def format_rename(metadata: dict, ext: str, pattern: str) -> str:
    return pattern.format(
        title=metadata.get("title", "Unknown"),
        season=metadata.get("season", "00"),
        episode=metadata.get("episode", "00"),
        year=metadata.get("year", "0000"),
        quality=metadata.get("quality", "NA"),
        audio=metadata.get("audio", "NA"),
        ext=ext.lstrip(".")
    )
