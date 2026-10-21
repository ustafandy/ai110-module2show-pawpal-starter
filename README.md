# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

The core logic lives in `pawpal_system.py`:

- **Task** represents one care activity (title, duration, priority, completion status).
- **Pet** stores a pet's details and manages its tasks (add, remove, list pending).
- **Owner** manages multiple pets and exposes all of their tasks as `(Pet, Task)` pairs, so each task keeps its pet context.
- **Scheduler** retrieves tasks through the Owner and builds the daily plan: it skips completed tasks, orders the rest by priority (shorter tasks first on ties), fits them into the owner's available minutes, and explains why each task was scheduled or skipped.

`main.py` is a CLI demo with one owner and two pets, and `tests/test_pawpal.py` contains automated tests for the core behavior.

## 🖥️ Sample Output

Actual output from `python main.py`:

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
```

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

## 📐 Smarter Scheduling

Each `Task` now also has a scheduled `time` (`"HH:MM"`, 24-hour), a `frequency` (`"none"`, `"daily"`, or `"weekly"`), and a `due_date`. All three have defaults, so older code like `Task("Walk", 30, "high")` still works. Every method below works across all of the owner's pets and returns `(Pet, Task)` pairs, so each task keeps its pet.

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by `due_date`, then by `time`. Zero-padded `"HH:MM"` strings sort chronologically, so times are compared directly. Sorts all of the owner's tasks by default, or a list you pass in (for example, a filtered list). |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Filters by pet name (case-insensitive), by completion status, or both. A filter left as `None` is not applied. Returns the original Task objects, not copies. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task(task)` | `complete_task` marks a task done and, for `"daily"` (+1 day) or `"weekly"` (+7 days) tasks, adds a new copy with the next `due_date` to the same pet. Completing an already-completed task does nothing, so repeated calls never create duplicates. `generate_plan()` only plans tasks due today or earlier, so tomorrow's copy is not added to today's plan. |
| Conflict detection | `Scheduler.detect_conflicts()` | Groups unfinished tasks by `(due_date, time)` and returns a warning for every slot with more than one task, including tasks for different pets. It returns warnings instead of raising errors. Only exact start-time matches are detected; overlapping durations are not. |

Example conflict warning from `python main.py`:

```
WARNING: Conflict on 2026-10-20 at 12:30: 'Feeding' (Biscuit), 'Give medication' (Mochi)
```

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
