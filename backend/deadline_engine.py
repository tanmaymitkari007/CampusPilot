
from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from difflib import SequenceMatcher

from extraction import ExtractedTask


def normalize_title(title: str) -> str:
    """Normalize task names for basic duplicate comparison."""
    text = title.lower()
    text = re.sub(r"\b(submit|complete|finish|do|the|a|an)\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def has_explicit_year(text: str | None) -> bool:
    if not text:
        return False

    return bool(re.search(r"\b(?:19|20)\d{2}\b", text))


def urgency_for(deadline: date | None, today: date) -> tuple[str, int]:
    """
    Return a human-readable urgency and a sortable score.
    Higher scores mean more urgent.
    """
    if deadline is None:
        return "Needs deadline review", 0

    days_left = (deadline - today).days

    if days_left < 0:
        return "Overdue", 5
    if days_left == 0:
        return "Due today", 4
    if days_left <= 3:
        return "Due soon", 3
    if days_left <= 7:
        return "Upcoming", 2

    return "Later", 1


def build_deadline_report(
    tasks: list[ExtractedTask],
    today: date | None = None,
) -> list[dict]:
    today = today or date.today()

    report = []

    for task in tasks:
        urgency, score = urgency_for(task.deadline, today)
        warnings = []

        if task.deadline is None:
            warnings.append("No confirmed deadline")

        elif task.deadline_text and not has_explicit_year(
            task.deadline_text
        ):
            warnings.append(
                "Year was not explicit in the source; verify the date"
            )

        if task.uncertainty:
            warnings.append(task.uncertainty)

        report.append({
            "title": task.title,
            "description": task.description,
            "deadline": (
                task.deadline.isoformat()
                if task.deadline else None
            ),
            "deadline_text": task.deadline_text,
            "category": task.category,
            "status": task.status,
            "evidence": task.evidence,
            "source_message_ids": task.source_message_ids,
            "urgency": urgency,
            "priority_score": score,
            "warnings": warnings,
            "conflict": False,
            "possible_duplicate": False,
        })

    # Compare task names and deadlines to flag possible conflicts.
    for i, first in enumerate(report):
        first_name = normalize_title(first["title"])

        for second in report[i + 1:]:
            second_name = normalize_title(second["title"])

            similarity = SequenceMatcher(
                None, first_name, second_name
            ).ratio()

            if similarity < 0.72:
                continue

            first_deadline = first["deadline"]
            second_deadline = second["deadline"]

            if (
                first_deadline
                and second_deadline
                and first_deadline != second_deadline
            ):
                first["conflict"] = True
                second["conflict"] = True

                warning = (
                    f"Possible deadline conflict with "
                    f"'{second['title']}' ({second_deadline})"
                )
                if warning not in first["warnings"]:
                    first["warnings"].append(warning)

                warning = (
                    f"Possible deadline conflict with "
                    f"'{first['title']}' ({first_deadline})"
                )
                if warning not in second["warnings"]:
                    second["warnings"].append(warning)

            elif first_deadline == second_deadline:
                first["possible_duplicate"] = True
                second["possible_duplicate"] = True

    # Sort urgent tasks first; unknown deadlines remain visible.
    report.sort(
        key=lambda item: (
            -item["priority_score"],
            item["deadline"] or "9999-12-31",
            item["title"].lower(),
        )
    )

    return report
