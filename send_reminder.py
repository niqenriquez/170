#!/usr/bin/env python3
"""
Telegram reminder with a year-end countdown, sent up to 3x/day.

Reads today's project info from topics.json (keyed by "MM-DD"), where
each date maps to an object with "morning" / "afternoon" / "evening"
messages. Each message is either a string or a list of lines. Falls
back to "default" if today isn't listed. Which slot gets sent is
controlled by the SLOT environment variable.
"""

import json
import os
import sys
from datetime import date

import requests

TOPICS_FILE = os.path.join(os.path.dirname(__file__), "topics.json")
VALID_SLOTS = ("morning", "afternoon", "evening")


def days_left_in_year(today: date) -> int:
    end_of_year = date(today.year, 12, 31)
    return (end_of_year - today).days


def get_todays_entry(today: date) -> dict:
    key = today.strftime("%m-%d")
    try:
        with open(TOPICS_FILE, "r") as f:
            topics = json.load(f)
    except FileNotFoundError:
        return {}

    if key in topics:
        return topics[key]
    return topics.get("default", {})


def render(value) -> str:
    """A slot may be a plain string or a list of lines; "" makes a blank line."""
    if isinstance(value, list):
        return "\n".join(value)
    return value


def get_slot_message(entry: dict, slot: str) -> str:
    if slot in entry and entry[slot]:
        return render(entry[slot])
    defaults = {
        "morning": "No specific focus set for today — pick something and go.",
        "afternoon": "Checking in — how's today's focus coming along?",
        "evening": "Wrap-up time — how did today go?",
    }
    return defaults[slot]


def build_message(today: date, slot: str) -> str:
    entry = get_todays_entry(today)
    text = get_slot_message(entry, slot)

    if slot == "morning":
        remaining = days_left_in_year(today)
        return (
            f"📅 {today.strftime('%A, %B %d, %Y')}\n"
            f"⏳ {remaining} day{'s' if remaining != 1 else ''} left in {today.year}\n\n"
            f"🎯 Today's focus:\n{text}"
        )
    elif slot == "afternoon":
        return f"☀️ Afternoon check-in:\n{text}"
    else:  # evening
        return f"🌙 Evening wrap-up:\n{text}"


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": text})
    resp.raise_for_status()


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    slot = os.environ.get("SLOT", "morning").strip().lower()

    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables.", file=sys.stderr)
        sys.exit(1)

    if slot not in VALID_SLOTS:
        print(f"Invalid SLOT '{slot}', must be one of {VALID_SLOTS}. Defaulting to 'morning'.", file=sys.stderr)
        slot = "morning"

    today = date.today()
    message = build_message(today, slot)
    send_telegram_message(token, chat_id, message)
    print(f"Sent [{slot}]:\n" + message)


if __name__ == "__main__":
    main()
