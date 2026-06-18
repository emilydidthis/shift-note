#!/usr/bin/env python3
"""
Shift Note Migration Script
Converts old single-sheet JSON-blob format to new multi-sheet row-based format.
Uses employee IDs instead of names for assignees and authors.

Usage:
    python3 migrate.py "Shift Note Data - ShiftNote.csv"

Output:
    Creates migrated/ folder with 9 CSVs for the new sheet structure.
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone


def read_input_csv(filepath):
    """Read the old key-value CSV and parse JSON blobs."""
    data = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row["key"].strip()
            value = row["value"].strip()
            try:
                data[key] = json.loads(value)
            except json.JSONDecodeError:
                data[key] = value
    return data


def write_csv(filepath, headers, rows):
    """Write a CSV file with headers and data rows."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([row.get(h, "") for h in headers])


def build_name_to_id(employees):
    """Build a mapping from employee name to ID."""
    return {name: str(i) for i, name in enumerate(employees, start=1)}


def convert_assignees(assignees, name_to_id):
    """Convert assignee names to IDs."""
    return [name_to_id.get(a, a) for a in assignees]


def convert_completions(completions, name_to_id):
    """Convert completion keys from names to IDs."""
    return {name_to_id.get(k, k): v for k, v in completions.items()}


def migrate_employees(employees, outdir):
    """Employees: array of name strings -> rows with auto-generated IDs."""
    headers = ["id", "name", "createdAt"]
    rows = []
    now = datetime.now(timezone.utc).isoformat()
    for i, name in enumerate(employees, start=1):
        rows.append({
            "id": str(i),
            "name": name,
            "createdAt": now,
        })
    write_csv(os.path.join(outdir, "Employees.csv"), headers, rows)
    print(f"  Employees.csv: {len(rows)} rows")


def migrate_announcements(announcements, name_to_id, outdir):
    """Announcements: author name -> author ID."""
    headers = ["id", "content", "author", "timestamp", "updatedAt"]
    rows = []
    for a in announcements:
        rows.append({
            "id": a.get("id", ""),
            "content": a.get("content", ""),
            "author": name_to_id.get(a.get("author", ""), ""),
            "timestamp": a.get("timestamp", ""),
            "updatedAt": str(a.get("updatedAt", "")),
        })
    write_csv(os.path.join(outdir, "Announcements.csv"), headers, rows)
    print(f"  Announcements.csv: {len(rows)} rows")


def migrate_todos(todos, name_to_id, outdir):
    """Todos: assignees and author names -> IDs, completions keys -> IDs."""
    headers = ["id", "content", "assignees", "completions", "author", "timestamp", "dueDate", "completedAt", "updatedAt"]
    rows = []
    for t in todos:
        raw_assignees = t.get("assignees", [])
        raw_completions = t.get("completions", {})
        rows.append({
            "id": t.get("id", ""),
            "content": t.get("content", ""),
            "assignees": json.dumps(convert_assignees(raw_assignees, name_to_id)),
            "completions": json.dumps(convert_completions(raw_completions, name_to_id)),
            "author": name_to_id.get(t.get("author", ""), ""),
            "timestamp": t.get("timestamp", ""),
            "dueDate": t.get("dueDate", ""),
            "completedAt": t.get("completedAt", "") or "",
            "updatedAt": str(t.get("updatedAt", "")),
        })
    write_csv(os.path.join(outdir, "Todos.csv"), headers, rows)
    print(f"  Todos.csv: {len(rows)} rows")


def migrate_events(events, outdir):
    """Events: array of objects -> one row each."""
    headers = ["id", "content", "timestamp"]
    rows = []
    for e in events:
        rows.append({
            "id": e.get("id", ""),
            "content": e.get("content", ""),
            "timestamp": e.get("timestamp", ""),
        })
    write_csv(os.path.join(outdir, "Events.csv"), headers, rows)
    print(f"  Events.csv: {len(rows)} rows")


def migrate_shopping(items, outdir):
    """Shopping/Faire: array of objects with purchased flag -> one row each."""
    headers = ["id", "content", "purchased", "timestamp"]
    rows = []
    for item in items:
        rows.append({
            "id": item.get("id", ""),
            "content": item.get("content", ""),
            "purchased": str(item.get("purchased", False)).lower(),
            "timestamp": "",
        })
    write_csv(os.path.join(outdir, "ShoppingList.csv"), headers, rows)
    print(f"  ShoppingList.csv: {len(rows)} rows")


def migrate_faire(items, outdir):
    """Faire: same structure as shopping."""
    headers = ["id", "content", "purchased", "timestamp"]
    rows = []
    for item in items:
        rows.append({
            "id": item.get("id", ""),
            "content": item.get("content", ""),
            "purchased": str(item.get("purchased", False)).lower(),
            "timestamp": "",
        })
    write_csv(os.path.join(outdir, "FaireList.csv"), headers, rows)
    print(f"  FaireList.csv: {len(rows)} rows")


def migrate_links(links, outdir):
    """ImportantLinks: array of objects with title/url -> one row each."""
    headers = ["id", "title", "url"]
    rows = []
    for link in links:
        rows.append({
            "id": link.get("id", ""),
            "title": link.get("title", ""),
            "url": link.get("url", ""),
        })
    write_csv(os.path.join(outdir, "ImportantLinks.csv"), headers, rows)
    print(f"  ImportantLinks.csv: {len(rows)} rows")


def migrate_daily_info(daily_info, name_to_id, outdir):
    """DailyInfo: single object -> single row. open/close assignees -> IDs."""
    headers = ["folksWorking", "registerOpen", "registerClose", "openAssignee", "closeAssignee", "monthlyGoalCurrent", "monthlyGoalTarget", "updatedAt"]
    rows = [{
        "folksWorking": daily_info.get("folks_working", ""),
        "registerOpen": str(daily_info.get("register_open", "")),
        "registerClose": str(daily_info.get("register_close", "")),
        "openAssignee": name_to_id.get(daily_info.get("open_assignee", ""), ""),
        "closeAssignee": name_to_id.get(daily_info.get("close_assignee", ""), ""),
        "monthlyGoalCurrent": str(daily_info.get("monthly_goal_current", "")),
        "monthlyGoalTarget": str(daily_info.get("monthly_goal_target", "")),
        "updatedAt": str(daily_info.get("_updatedAt", "")),
    }]
    write_csv(os.path.join(outdir, "DailyInfo.csv"), headers, rows)
    print(f"  DailyInfo.csv: {len(rows)} row")


def migrate_lists(events, shopping, faire, links, outdir):
    """Combine Events, ShoppingList, FaireList, ImportantLinks into one Lists sheet."""
    headers = ["id", "category", "content", "purchased", "timestamp", "title", "url"]
    rows = []
    for e in events:
        rows.append({
            "id": e.get("id", ""),
            "category": "event",
            "content": e.get("content", ""),
            "purchased": "",
            "timestamp": e.get("timestamp", ""),
            "title": "",
            "url": "",
        })
    for s in shopping:
        rows.append({
            "id": s.get("id", ""),
            "category": "shopping",
            "content": s.get("content", ""),
            "purchased": str(s.get("purchased", False)).lower(),
            "timestamp": "",
            "title": "",
            "url": "",
        })
    for f in faire:
        rows.append({
            "id": f.get("id", ""),
            "category": "faire",
            "content": f.get("content", ""),
            "purchased": str(f.get("purchased", False)).lower(),
            "timestamp": "",
            "title": "",
            "url": "",
        })
    for l in links:
        rows.append({
            "id": l.get("id", ""),
            "category": "link",
            "content": "",
            "purchased": "",
            "timestamp": "",
            "title": l.get("title", ""),
            "url": l.get("url", ""),
        })
    write_csv(os.path.join(outdir, "Lists.csv"), headers, rows)
    print(f"  Lists.csv: {len(rows)} rows ({len(events)} events, {len(shopping)} shopping, {len(faire)} faire, {len(links)} links)")


def migrate_archive(outdir):
    """Archive: empty sheet with headers only."""
    headers = ["id", "type", "content", "assignees", "author", "timestamp", "completedAt", "archivedAt"]
    write_csv(os.path.join(outdir, "Archive.csv"), headers, [])
    print(f"  Archive.csv: 0 rows (headers only)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 migrate.py <input_csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(script_dir, "migrated")

    print(f"Reading: {input_file}")
    data = read_input_csv(input_file)

    # Build name-to-ID mapping from employees
    employees = data.get("employees", [])
    name_to_id = build_name_to_id(employees)
    print(f"\nEmployee mapping:")
    for name, eid in name_to_id.items():
        print(f"  {eid}: {name}")

    print(f"\nMigrating to: {outdir}/")
    os.makedirs(outdir, exist_ok=True)

    # Employees
    if employees:
        migrate_employees(employees, outdir)
    else:
        print("  Employees.csv: SKIPPED (no data)")

    # Announcements
    if "announcements" in data:
        migrate_announcements(data["announcements"], name_to_id, outdir)
    else:
        print("  Announcements.csv: SKIPPED (no data)")

    # Todos
    if "todos" in data:
        migrate_todos(data["todos"], name_to_id, outdir)
    else:
        print("  Todos.csv: SKIPPED (no data)")

    # DailyInfo + nested categories
    daily_info = data.get("dailyInfo", {})
    if daily_info:
        migrate_daily_info(daily_info, name_to_id, outdir)
        migrate_lists(
            daily_info.get("events", []),
            daily_info.get("shopping_list", []),
            daily_info.get("faire_list", []),
            daily_info.get("important_links", []),
            outdir
        )
    else:
        print("  DailyInfo.csv: SKIPPED (no data)")

    # Archive (empty)
    migrate_archive(outdir)

    print(f"\nDone! {len(os.listdir(outdir))} CSVs created in {outdir}/")
    print("\nNext steps:")
    print("1. Create new Google Sheet with 6 sheets: Employees, Announcements, Todos, Lists, DailyInfo, Archive")
    print("2. Import each CSV: File -> Import -> Upload -> Replace sheet")
    print("3. Deploy new Apps Script code")
    print("4. Update index.html with new Apps Script URL")


if __name__ == "__main__":
    main()
