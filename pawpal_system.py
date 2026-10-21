"""PawPal+ core system classes.

Mirrors diagrams/uml.mmd. Tasks travel from Owner to Scheduler as
(Pet, Task) pairs so the plan always knows which pet each task is for.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

# Higher number = more important. Used to sort tasks.
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}

# How far ahead the next occurrence of a recurring task is scheduled.
RECURRENCE_STEPS = {"none": None, "daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    completed: bool = False
    time: str = "08:00"  # scheduled start time, "HH:MM" (24-hour)
    frequency: str = "none"  # "none", "daily", or "weekly"
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Validate the time and frequency, and normalize time to zero-padded HH:MM."""
        try:
            parsed = datetime.strptime(self.time, "%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time '{self.time}'. Use HH:MM, e.g. 07:30.") from None
        self.time = parsed.strftime("%H:%M")

        self.frequency = self.frequency.lower()
        if self.frequency not in RECURRENCE_STEPS:
            raise ValueError(f"Unknown frequency '{self.frequency}'. Use none, daily, or weekly.")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy of this task for its next due date, or None if it doesn't repeat."""
        step = RECURRENCE_STEPS[self.frequency]
        if step is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + step)

    def priority_rank(self) -> int:
        """Return a numeric rank for the priority so tasks can be sorted."""
        priority = self.priority.lower()
        if priority not in PRIORITY_RANKS:
            raise ValueError(f"Unknown priority '{self.priority}'. Use low, medium, or high.")
        return PRIORITY_RANKS[priority]


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        for task in self.tasks:
            if task.title == title:
                self.tasks.remove(task)
                return
        raise ValueError(f"{self.name} has no task named '{title}'.")

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and, if it recurs, add and return its next occurrence.

        Completing an already-completed task does nothing, so repeated calls
        (e.g. Streamlit reruns) never create duplicate occurrences.
        """
        if task.completed:
            return None
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Owner:
    """A pet owner, their daily constraints, and their pets."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all of this owner's pets, paired with its pet."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for one owner with an empty plan."""
        self.owner: Owner = owner
        self.scheduled_tasks: list[tuple[Pet, Task]] = []
        self.skipped_tasks: list[tuple[Pet, Task]] = []

    def generate_plan(self) -> list[tuple[Pet, Task]]:
        """Choose and order tasks that fit the owner's available time, by priority."""
        self.scheduled_tasks = []
        self.skipped_tasks = []

        # Only tasks due today (or overdue); future recurring occurrences wait their turn.
        today = date.today()
        pending = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed and task.due_date <= today
        ]

        # Highest priority first; among equal priorities, shorter tasks first.
        pending.sort(key=lambda pair: (-pair[1].priority_rank(), pair[1].duration_minutes))

        minutes_left = self.owner.available_minutes
        for pet, task in pending:
            if task.duration_minutes <= minutes_left:
                self.scheduled_tasks.append((pet, task))
                minutes_left -= task.duration_minutes
            else:
                self.skipped_tasks.append((pet, task))

        return self.scheduled_tasks

    def explain_plan(self) -> str:
        """Describe why each task was scheduled or skipped."""
        lines = [f"{self.owner.name} has {self.owner.available_minutes} minutes available today."]
        lines.append("Tasks are chosen by priority (high first), then shorter tasks first.")

        used = 0
        for pet, task in self.scheduled_tasks:
            used += task.duration_minutes
            lines.append(
                f"- Scheduled '{task.title}' for {pet.name}: {task.priority} priority, "
                f"{task.duration_minutes} min (total so far: {used} min)."
            )

        for pet, task in self.skipped_tasks:
            lines.append(
                f"- Skipped '{task.title}' for {pet.name}: needs {task.duration_minutes} min, "
                f"but only {self.owner.available_minutes - used} min were left."
            )

        if not self.scheduled_tasks and not self.skipped_tasks:
            lines.append("- There are no pending tasks to schedule.")

        return "\n".join(lines)

    def sort_by_time(
        self, pairs: list[tuple[Pet, Task]] | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (Pet, Task) pairs ordered by due date, then scheduled HH:MM time.

        Defaults to all of the owner's tasks. Zero-padded "HH:MM" strings sort
        chronologically, so they can be compared directly.
        """
        if pairs is None:
            pairs = self.owner.get_all_tasks()
        return sorted(pairs, key=lambda pair: (pair[1].due_date, pair[1].time))

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (Pet, Task) pairs matching a pet name and/or completion status.

        Leaving a filter as None means "don't filter on this".
        """
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if (pet_name is None or pet.name.lower() == pet_name.lower())
            and (completed is None or task.completed == completed)
        ]

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each date/time slot shared by two or more pending tasks.

        Only exact start-time matches are detected; overlapping durations are not.
        """
        slots: dict[tuple[date, str], list[tuple[Pet, Task]]] = {}
        for pet, task in self.filter_tasks(completed=False):
            slots.setdefault((task.due_date, task.time), []).append((pet, task))

        warnings = []
        for (due_date, time), pairs in sorted(slots.items()):
            if len(pairs) > 1:
                names = ", ".join(f"'{task.title}' ({pet.name})" for pet, task in pairs)
                warnings.append(f"Conflict on {due_date} at {time}: {names}")
        return warnings
