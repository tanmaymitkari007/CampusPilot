
from __future__ import annotations

from datetime import date
from pathlib import Path

from parser import parse_whatsapp_zip, group_messages_by_day
from extraction import extract_tasks, ExtractedTask
from deadline_engine import build_deadline_report

BATCH_SIZE = 40


def process_whatsapp_zip(
    zip_path: str | Path,
    today: date | None = None,
) -> dict:
    messages = parse_whatsapp_zip(zip_path)
    grouped = group_messages_by_day(messages)

    # Keep each message's original calendar date.
    dated_messages = [
        (day, message)
        for day, day_messages in grouped.items()
        for message in day_messages
    ]

    all_tasks = []
    providers_used = set()
    extraction_errors = []
    source_metadata = {}

    # Process several days per AI call rather than one call per day.
    for start in range(0, len(dated_messages), BATCH_SIZE):
        batch = dated_messages[start:start + BATCH_SIZE]
        batch_messages = [message for _, message in batch]
        batch_number = start // BATCH_SIZE + 1

        # extract_tasks assigns IDs starting at 1 within each batch.
        local_metadata = {
            local_id: {
                "source_date": str(day),
                "source_file": message.source_file,
            }
            for local_id, (day, message) in enumerate(batch, start=1)
        }

        try:
            result, provider = extract_tasks(batch_messages)
            providers_used.add(provider)

            for task in result.tasks:
                task_data = task.model_dump(mode="json")
                local_ids = task_data.get("source_message_ids", [])

                # Convert batch-local IDs to unique IDs across the
                # entire export so different batches cannot collide.
                global_ids = [
                    start + int(local_id)
                    for local_id in local_ids
                ]
                task_data["source_message_ids"] = global_ids

                first_source = (
                    local_metadata.get(int(local_ids[0]), {})
                    if local_ids else {}
                )

                task_data["source_date"] = first_source.get("source_date")
                task_data["source_file"] = first_source.get("source_file")

                for local_id, global_id in zip(local_ids, global_ids):
                    source_metadata[global_id] = local_metadata.get(
                        int(local_id), {}
                    )

                all_tasks.append(task_data)

        except Exception as exc:
            extraction_errors.append({
                "batch": batch_number,
                "messages": len(batch_messages),
                "error": str(exc),
            })

    validated_tasks = [
        ExtractedTask.model_validate({
            key: value
            for key, value in task.items()
            if key not in {"source_date", "source_file"}
        })
        for task in all_tasks
    ]

    report = build_deadline_report(validated_tasks, today=today)

    # Attach the original source metadata using globally unique IDs.
    for item in report:
        source_ids = item.get("source_message_ids", [])
        first_source = next(
            (
                source_metadata.get(int(source_id), {})
                for source_id in source_ids
                if int(source_id) in source_metadata
            ),
            {},
        )
        item["source"] = first_source

    return {
        "status": "completed" if not extraction_errors else "partial",
        "message_count": len(messages),
        "calendar_days": len(grouped),
        "batches_total": (
            len(dated_messages) + BATCH_SIZE - 1
        ) // BATCH_SIZE,
        "providers_used": sorted(providers_used),
        "tasks_found": len(report),
        "tasks": report,
        "extraction_errors": extraction_errors,
    }
