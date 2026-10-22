
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from parser import parse_chat_text, group_messages_by_day
from extraction import extract_tasks


sample = """\
[21/10/26, 9:15:00 AM] Class Rep: Submit the AI assignment by 25 October 2026.
Bring your project report too.
[21/10/26, 10:30:00 AM] Professor: Reminder: lab submissions close tomorrow.
[22/10/26, 8:00:00 AM] Class Rep: The presentation is postponed to 28 October.
"""

messages = parse_chat_text(sample)
grouped = group_messages_by_day(messages)

for day, day_messages in grouped.items():
    print(f"\nProcessing {day} ({len(day_messages)} messages)")

    try:
        result, provider = extract_tasks(day_messages)
        print("Provider:", provider)

        for task in result.tasks:
            print("-" * 50)
            print("Task:", task.title)
            print("Deadline:", task.deadline)
            print("Original wording:", task.deadline_text)
            print("Status:", task.status)
            print("Evidence:", task.evidence)
            print("Source IDs:", task.source_message_ids)
            print("Uncertainty:", task.uncertainty)

    except Exception as exc:
        print(f"Extraction failed for {day}: {exc}")
