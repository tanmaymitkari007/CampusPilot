
from parser import parse_chat_text, group_messages_by_day


sample = """\
[21/10/26, 9:15:00 AM] Class Rep: Submit the AI assignment by 25 October 2026.
Bring your project report too.
[21/10/26, 10:30:00 AM] Professor: Reminder: lab submissions close tomorrow.
[22/10/26, 8:00:00 AM] Class Rep: The presentation is postponed to 28 October.
"""

messages = parse_chat_text(sample)
grouped = group_messages_by_day(messages)

print(f"Parsed messages: {len(messages)}")
print(f"Calendar days: {len(grouped)}")

for day, day_messages in grouped.items():
    print(f"\n--- {day} ---")
    for message in day_messages:
        print(f"{message.timestamp} | {message.sender}")
        print(message.body)
