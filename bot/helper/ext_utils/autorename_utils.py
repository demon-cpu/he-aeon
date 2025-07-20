import re

async def extract_metadata(filename: str) -> dict:
    """
    Extracts metadata like title, season, episode, year, quality, audio from a filename.
    Adjust the regex patterns as per your naming convention if needed.
    """
    metadata = {
        "title": "Unknown",
        "season": "00",
        "episode": "00",
        "year": "0000",
        "quality": "NA",
        "audio": "NA"
    }

    name = filename.rsplit(".", 1)[0]

    # Title
    title_match = re.match(r"^(.*?)(S\d+E\d+|$)", name, re.IGNORECASE)
    if title_match:
        metadata["title"] = title_match.group(1).replace(".", " ").strip()

    # Season & Episode
    se_match = re.search(r"[Ss](\d+)[Ee](\d+)", name)
    if se_match:
        metadata["season"] = se_match.group(1).zfill(2)
        metadata["episode"] = se_match.group(2).zfill(2)

    # Year
    year_match = re.search(r"(19|20)\d{2}", name)
    if year_match:
        metadata["year"] = year_match.group(0)

    # Quality
    quality_match = re.search(r"(480p|720p|1080p|2160p|4K)", name, re.IGNORECASE)
    if quality_match:
        metadata["quality"] = quality_match.group(0).upper()

    # Audio
    audio_match = re.search(r"(5\.1|2\.0|Atmos|AAC|DDP)", name, re.IGNORECASE)
    if audio_match:
        metadata["audio"] = audio_match.group(0).upper()

    return metadata
