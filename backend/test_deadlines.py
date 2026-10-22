
from datetime import date

from extraction import ExtractedTask
from deadline_engine import build_deadline_report


tasks = [
    ExtractedTask(
        title="Submit AI assignment",
        deadline=date(2026, 10, 25),
        deadline_text="25 October 2026",
        category="assignment",
        status="new",
        evidence="Submit the AI assignment by 25 October 2026.",
        source_message_ids=[1],
    ),
    ExtractedTask(
        title="Lab submissions",
        deadline=date(2026, 10, 22),
        deadline_text="tomorrow",
        category="submission",
        status="reminder",
        evidence="lab submissions close tomorrow.",
        source_message_ids=[2],
    ),
    ExtractedTask(
        title="Presentation",
        deadline=date(2026, 10, 28),
        deadline_text="28 October",
        category="event",
        status="update",
        evidence="The presentation is postponed to 28 October.",
        source_message_ids=[3],
    ),
    ExtractedTask(
        title="Complete project registration",
        deadline=None,
        deadline_text=None,
        category="other",
        status="new",
        evidence="Complete project registration.",
        source_message_ids=[4],
    ),
]

report = build_deadline_report(
    tasks,
    today=date(2026, 10, 22),
)

for item in report:
    print("-" * 45)
    print("Task:", item["title"])
    print("Deadline:", item["deadline"])
    print("Urgency:", item["urgency"])
    print("Warnings:", item["warnings"])
