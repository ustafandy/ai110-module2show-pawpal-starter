# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a busy pet owner plan daily care across all of their pets. It tracks care tasks (walks, feeding, medication, grooming, enrichment), builds a daily plan that fits the owner's available time and respects task priority, and explains why each task was scheduled or skipped.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The system was designed first as a UML diagram, then implemented in Python, tested with pytest, and connected to a Streamlit UI.

## ✨ Features

- **Multi-pet management:** one owner can have any number of pets. Every task keeps its pet context, so Biscuit's "Feeding" and Mochi's "Feeding" are never confused.
- **Task management:** each task has a title, duration, priority (low/medium/high), start time (`HH:MM`), repeat frequency (none/daily/weekly), due date, and completion status. Invalid times and unknown frequencies are rejected with a clear `ValueError`.
- **Priority- and time-based scheduling:** `Scheduler.generate_plan()` takes all pending tasks due today or earlier, orders them by priority (high first, shorter tasks first on ties), and adds them until the owner's available minutes run out. Tasks that don't fit are skipped, and `explain_plan()` explains every decision.
- **Sorting:** `Scheduler.sort_by_time()` orders tasks by due date, then by start time, across all pets.
- **Filtering:** `Scheduler.filter_tasks()` filters tasks by pet name (case-insensitive), completion status, or both.
- **Recurring daily/weekly tasks:** completing a recurring task with `Pet.complete_task()` automatically adds its next occurrence (+1 day or +7 days). Completing the same task twice never creates duplicates, and future occurrences stay out of today's plan.
- **Conflict detection:** `Scheduler.detect_conflicts()` warns when two or more pending tasks share the same date and start time, including tasks for different pets.
- **Streamlit UI:** add pets and tasks, view, sort, and filter tasks, mark tasks complete, see conflict warnings, and generate an explained daily schedule in the browser.
- **Automated testing:** 17 pytest tests cover scheduling, sorting, filtering, recurrence, conflict detection, and edge cases.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py   # interactive web app
python main.py         # CLI demo with sample data
python -m pytest       # automated tests
```

### Project files

| File | Purpose |
|------|---------|
| `pawpal_system.py` | Core classes: `Task`, `Pet`, `Owner`, `Scheduler` |
| `app.py` | Streamlit UI built on the core classes |
| `main.py` | CLI demo of scheduling, sorting, recurrence, filtering, and conflicts |
| `tests/test_pawpal.py` | Automated pytest suite |
| `diagrams/uml.mmd` | Original Phase 1 UML design |
| `diagrams/uml_final.mmd` | Final UML matching the finished code |
| `reflection.md` | Design, testing, and AI-collaboration reflection |

## 🧩 Implementation Summary

The core logic lives in `pawpal_system.py`:

- **Task** represents one care activity (title, duration, priority, completion status, start time, frequency, and due date). It can mark itself complete, create its next occurrence if it repeats, and turn its priority into a number for sorting.
- **Pet** stores a pet's details and manages its tasks (add, remove, list pending, and complete a task, which adds the next occurrence for recurring tasks).
- **Owner** manages multiple pets and exposes all of their tasks as `(Pet, Task)` pairs, so each task keeps its pet context.
- **Scheduler** retrieves tasks through the Owner and builds the daily plan: it skips completed and future tasks, orders the rest by priority (shorter tasks first on ties), fits them into the owner's available minutes, and explains why each task was scheduled or skipped. It also sorts, filters, and checks tasks for conflicts.

The final class diagram is in `diagrams/uml_final.mmd`. The original design is kept in `diagrams/uml.mmd` for comparison.

## 📐 Smarter Scheduling

Each `Task` also has a scheduled `time` (`"HH:MM"`, 24-hour), a `frequency` (`"none"`, `"daily"`, or `"weekly"`), and a `due_date`. All three have defaults, so older code like `Task("Walk", 30, "high")` still works. Every method below works across all of the owner's pets and returns `(Pet, Task)` pairs, so each task keeps its pet.

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by `due_date`, then by `time`. Zero-padded `"HH:MM"` strings sort chronologically, so times are compared directly. Sorts all of the owner's tasks by default, or a list you pass in (for example, a filtered list). |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Filters by pet name (case-insensitive), by completion status, or both. A filter left as `None` is not applied. Returns the original Task objects, not copies. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task(task)` | `complete_task` marks a task done and, for `"daily"` (+1 day) or `"weekly"` (+7 days) tasks, adds a new copy with the next `due_date` to the same pet. Completing an already-completed task does nothing, so repeated calls never create duplicates. `generate_plan()` only plans tasks due today or earlier, so tomorrow's copy is not added to today's plan. |
| Conflict detection | `Scheduler.detect_conflicts()` | Groups unfinished tasks by `(due_date, time)` and returns a warning for every slot with more than one task, including tasks for different pets. It returns warnings instead of raising errors. Only exact start-time matches are detected; overlapping durations are not. |

## 📸 Demo Walkthrough

### What you can do in the app

Run `streamlit run app.py`. The page has three sections:

| Section | Actions |
|---------|---------|
| **Owner & Pets** | Set the owner's name and available minutes for today. Add pets (name and species); duplicate pet names are rejected. A table lists each pet and its task count. |
| **Tasks** | Add a task for a chosen pet with title, duration, priority, start time, repeat frequency, and due date. View all tasks sorted by date and time, and filter by pet and by status (all/pending/completed). Mark a pending task complete. Conflict warnings, or a "no conflicts" confirmation, appear below the task list. |
| **Build Schedule** | Click **Generate schedule** to see today's plan as a table, the minutes used, any skipped tasks, a conflict reminder, and a "Why this plan?" explanation. |

Pets and tasks are kept in `st.session_state`, so they persist while you use the app. The UI calls the `Scheduler` methods directly and has no scheduling logic of its own.

### Example workflow

1. **Create the owner and pets.** Enter owner name `Jordan` with `90` available minutes. Add `Biscuit` (dog) and `Mochi` (cat).
2. **Add tasks.**
   - Biscuit: "Morning walk" (30 min, high, 07:00, daily), "Feeding" (10 min, high, 12:30), "Fetch in the yard" (40 min, low, 17:00).
   - Mochi: "Feeding" (5 min, high, 06:45), "Give medication" (5 min, medium, 12:30), "Brush fur" (15 min, medium, 19:15, weekly).
3. **Review the task list.** The table is sorted by date and time. Set **Show pet** to `Mochi` to see only Mochi's tasks, or **Show status** to `Pending` to hide finished ones.
4. **Check conflicts.** Biscuit's "Feeding" and Mochi's "Give medication" are both at 12:30 today, so a warning appears: `Conflict on <today> at 12:30: 'Feeding' (Biscuit), 'Give medication' (Mochi)`.
5. **Generate the schedule.** The plan includes the three high-priority tasks and the two medium-priority tasks (65 of 90 minutes). "Fetch in the yard" (40 min) is skipped because only 25 minutes are left, and the explanation says so.
6. **Complete a recurring task.** Mark Biscuit's "Morning walk" complete. A confirmation appears, and a new "Morning walk" is added for tomorrow at 07:00. It appears in the task list but is not part of today's plan.

### Scheduler behavior to notice

- **Plan order vs. time order:** the generated plan is ordered by **priority**, then duration, which decides what fits in the available time. The task list is ordered by **date and time** using `sort_by_time()`.
- **Filtering** only changes which tasks are shown. The scheduler still plans across every pet.
- **Recurrence** happens when a task is completed. The next occurrence is a new, pending task with a later due date. Completing the same task again does nothing.
- **Conflict warnings** flag pending tasks with the same date and start time. Completed tasks and tasks on different days are ignored, and overlapping durations (for example, a 30-minute walk at 07:00 and a feeding at 07:15) are not flagged.

### CLI demo

`python main.py` runs the same scenario with sample data. Actual output (run on 2026-10-20):

```
==================================================
Today's Schedule for Jordan's pets
==================================================
  08:00  Feeding            for Mochi    (5 min) [priority: high]
  08:05  Feeding            for Biscuit  (10 min) [priority: high]
  08:15  Morning walk       for Biscuit  (30 min) [priority: high]
  08:45  Give medication    for Mochi    (5 min) [priority: medium]
  08:50  Brush fur          for Mochi    (15 min) [priority: medium]

Skipped (not enough time):
  - Fetch in the yard for Biscuit (40 min)

Why this plan:
Jordan has 90 minutes available today.
Tasks are chosen by priority (high first), then shorter tasks first.
- Scheduled 'Feeding' for Mochi: high priority, 5 min (total so far: 5 min).
- Scheduled 'Feeding' for Biscuit: high priority, 10 min (total so far: 15 min).
- Scheduled 'Morning walk' for Biscuit: high priority, 30 min (total so far: 45 min).
- Scheduled 'Give medication' for Mochi: medium priority, 5 min (total so far: 50 min).
- Scheduled 'Brush fur' for Mochi: medium priority, 15 min (total so far: 65 min).
- Skipped 'Fetch in the yard' for Biscuit: needs 40 min, but only 25 min were left.

==================================================
1. Sorting: all tasks by scheduled time
==================================================
  2026-10-20 06:45  Feeding            for Mochi    [none, pending]
  2026-10-20 07:00  Morning walk       for Biscuit  [daily, pending]
  2026-10-20 12:30  Feeding            for Biscuit  [none, pending]
  2026-10-20 12:30  Give medication    for Mochi    [none, pending]
  2026-10-20 17:00  Fetch in the yard  for Biscuit  [none, pending]
  2026-10-20 19:15  Brush fur          for Mochi    [weekly, pending]

==================================================
2. Recurring: completing daily and weekly tasks
==================================================
  Completed 'Morning walk' due 2026-10-20 (daily)
  -> next occurrence added for 2026-10-21 at 07:00
  Completed 'Brush fur' due 2026-10-20 (weekly)
  -> next occurrence added for 2026-10-27 at 19:15
  Completing 'Morning walk' again creates: None (no duplicate)

==================================================
3. Filtering
==================================================
Biscuit's tasks:
  2026-10-20 07:00  Morning walk       for Biscuit  [daily, done]
  2026-10-20 12:30  Feeding            for Biscuit  [none, pending]
  2026-10-20 17:00  Fetch in the yard  for Biscuit  [none, pending]
  2026-10-21 07:00  Morning walk       for Biscuit  [daily, pending]
Completed tasks (any pet):
  2026-10-20 07:00  Morning walk       for Biscuit  [daily, done]
  2026-10-20 19:15  Brush fur          for Mochi    [weekly, done]
Mochi's pending tasks:
  2026-10-20 06:45  Feeding            for Mochi    [none, pending]
  2026-10-20 12:30  Give medication    for Mochi    [none, pending]
  2026-10-27 19:15  Brush fur          for Mochi    [weekly, pending]

==================================================
4. Conflict detection
==================================================
  WARNING: Conflict on 2026-10-20 at 12:30: 'Feeding' (Biscuit), 'Give medication' (Mochi)
```

In the CLI, the clock times in the first section are display slots starting at 08:00 in plan order. They show how the plan would run back to back. Dates in the output depend on the day you run it.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite in `tests/test_pawpal.py` covers:

- **Sorting:** `sort_by_time()` orders tasks by due date and then by time, across pets. It also checks that `"7:05"` is stored as `"07:05"` so the times sort correctly.
- **Recurrence:** completing a daily or weekly task adds exactly one next occurrence (+1 day or +7 days, including across a month end). Completing a task twice doesn't create duplicates, one-time tasks don't repeat, and tomorrow's copy is left out of today's plan.
- **Conflict detection:** pending tasks at the same date and time are flagged, including across pets. Completed tasks and tasks on other days are ignored.
- **Scheduling:** tasks are planned by priority across all pets, completed tasks are skipped, and the plan stays within the available minutes. A task that exactly fills the remaining time is still scheduled.
- **Filtering:** by pet name (case-insensitive), by completion status, or both.
- **Edge cases and invalid input:** a pet with no tasks gives an empty plan with a clear explanation. Invalid times and unknown frequencies raise `ValueError`.

Test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
collected 17 items

tests\test_pawpal.py .................                                   [100%]

============================= 17 passed in 0.08s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

Each core feature has tests for both the normal case and its key edge cases, using fixed dates so results are repeatable. It isn't 5 stars because of these known gaps:

- Conflict detection only catches identical start times, not overlapping durations.
- An invalid priority is only rejected when a plan is generated, not when the task is created.
- `generate_plan()` depends on the real current date.
- The Streamlit UI is not tested automatically.
