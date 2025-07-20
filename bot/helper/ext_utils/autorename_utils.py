import re

from bot import LOGGER
from bot.modules.users_settings import update_user_settings_db


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
    try:
        return pattern.format(
            title=metadata.get("title", "Unknown"),
            season=metadata.get("season", "00"),
            episode=metadata.get("episode", "00"),
            year=metadata.get("year", "0000"),
            quality=metadata.get("quality", "NA"),
            audio=metadata.get("audio", "NA"),
        )
    except Exception as e:
        LOGGER.error(f"Rename pattern error: {e}")
        return f"{metadata.get('title', 'Unknown')} - RENAMING ERROR"


def is_autorename_enabled(user_settings: dict) -> bool:
    return user_settings.get("auto_rename_enabled", False)


async def ask_for_rename_pattern(bot, message):
    user_id = message.from_user.id
    sent = await message.reply_text(
        "**📝 Send your rename pattern.**\n\n"
        "You can use:\n"
        "`{title}` – Title\n"
        "`{season}` – Season\n"
        "`{episode}` – Episode\n"
        "`{year}` – Year\n"
        "`{quality}` – Quality (e.g. 720p)\n"
        "`{audio}` – Audio (e.g. 5.1, AAC)\n\n"
        "Example:\n`{title} S{season}E{episode} [{quality} - {audio}]`\n\n"
        "_Reply with your desired format now._",
        quote=True,
    )

    def check(m):
        return (
            m.from_user.id == user_id
            and m.reply_to_message
            and m.reply_to_message.message_id == sent.message_id
        )

    try:
        user_response = await bot.listen(message.chat.id, check=check, timeout=300)
        pattern = user_response.text.strip()

        if not pattern:
            return await message.reply("❌ Pattern cannot be empty.")

        await update_user_settings_db(user_id, {"rename_pattern": pattern})
        return await message.reply(
            f"✅ Your rename pattern has been set to:\n`{pattern}`"
        )

    except TimeoutError:
        return await message.reply("⌛ Timed out. Please try again.")
