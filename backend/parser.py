
from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ChatMessage:
    timestamp: datetime
    sender: str | None
    body: str
    source_file: str


# Supports common Android/iOS export variants.

MESSAGE_START = re.compile(
    r"^(?:"
    r"\[(?P<bracket_date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*"
    r"(?P<bracket_time>\d{1,2}:\d{2}(?::\d{2})?"
    r"(?:\s?[apAP]\.?[mM]\.?)?)\]\s*"
    r"|"
    r"(?P<plain_date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*"
    r"(?P<plain_time>\d{1,2}:\d{2}(?::\d{2})?"
    r"(?:\s?[apAP]\.?[mM]\.?)?)\s*-\s*"
    r")(?P<content>.*)$"
)


SENDER_PREFIX = re.compile(r"^(?P<sender>[^:\n]+):\s?(?P<body>.*)$")

DATE_FORMATS = (
    "%d/%m/%y, %H:%M",
    "%d/%m/%Y, %H:%M",
    "%m/%d/%y, %H:%M",
    "%m/%d/%Y, %H:%M",
    "%d/%m/%y, %I:%M %p",
    "%d/%m/%Y, %I:%M %p",
    "%m/%d/%y, %I:%M %p",
    "%m/%d/%Y, %I:%M %p",
    "%d/%m/%y, %H:%M:%S",
    "%d/%m/%Y, %H:%M:%S",
    "%m/%d/%y, %H:%M:%S",
    "%m/%d/%Y, %H:%M:%S",
    "%d/%m/%y, %I:%M:%S %p",
    "%d/%m/%Y, %I:%M:%S %p",
    "%m/%d/%y, %I:%M:%S %p",
    "%m/%d/%Y, %I:%M:%S %p",
)


def parse_timestamp(date_text: str, time_text: str) -> datetime:
    normalized_time = re.sub(
        r"(?i)(a\.m\.|p\.m\.|am|pm)$",
        lambda match: match.group(0).replace(".", "").upper(),
        time_text.strip(),
    )

    combined = f"{date_text}, {normalized_time}"

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(combined, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unsupported timestamp format: {combined}")


def parse_chat_text(text: str, source_file: str = "chat.txt") -> list[ChatMessage]:
    messages: list[ChatMessage] = []
    current: ChatMessage | None = None

    for line in text.lstrip("\ufeff").splitlines():
        match = MESSAGE_START.match(line)

        if match:
            if current is not None:
                messages.append(current)

            date_text = match.group("bracket_date") or match.group("plain_date")
            time_text = match.group("bracket_time") or match.group("plain_time")
            content = match.group("content")

            try:
                timestamp = parse_timestamp(date_text, time_text)
            except ValueError:
                # Do not silently misdate a message.
                current = None
                continue

            sender_match = SENDER_PREFIX.match(content)

            if sender_match:
                sender = sender_match.group("sender").strip()
                body = sender_match.group("body")
            else:
                # System notifications such as group encryption notices.
                sender = None
                body = content

            current = ChatMessage(
                timestamp=timestamp,
                sender=sender,
                body=body,
                source_file=source_file,
            )

        elif current is not None:
            # Continuation line: retain multiline message content.
            current.body += "\n" + line

    if current is not None:
        messages.append(current)

    return messages


def parse_whatsapp_zip(zip_path: str | Path) -> list[ChatMessage]:
    zip_path = Path(zip_path)

    if not zip_path.is_file():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        candidates = [
            name for name in archive.namelist()
            if Path(name).name.lower().endswith("_chat.txt")
            and not name.startswith("__MACOSX/")
        ]

        # Some exports or renamed archives may contain chat.txt.
        if not candidates:
            candidates = [
                name for name in archive.namelist()
                if Path(name).name.lower() == "chat.txt"
                and not name.startswith("__MACOSX/")
            ]

        if not candidates:
            raise ValueError(
                "No *_chat.txt or chat.txt file found inside the ZIP."
            )

        if len(candidates) > 1:
            raise ValueError(
                "Multiple chat text files found. Upload one conversation "
                "per ZIP for this version."
            )

        member = candidates[0]
        raw_text = archive.read(member).decode("utf-8-sig", errors="replace")

    messages = parse_chat_text(raw_text, source_file=Path(member).name)

    if not messages:
        raise ValueError(
            "No messages could be parsed. The export format may differ "
            "from the formats currently supported."
        )

    return messages


def group_messages_by_day(
    messages: list[ChatMessage],
) -> dict[str, list[ChatMessage]]:
    grouped: dict[str, list[ChatMessage]] = {}

    for message in sorted(messages, key=lambda item: item.timestamp):
        day = message.timestamp.date().isoformat()
        grouped.setdefault(day, []).append(message)

    return grouped
