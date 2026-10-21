"""PawPal+ core system classes.

Mirrors diagrams/uml.mmd. Tasks travel from Owner to Scheduler as
(Pet, Task) pairs so the plan always knows which pet each task is for.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Higher number = more important. Used to sort tasks.
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

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

        pending = [(pet, task) for pet, task in self.owner.get_all_tasks() if not task.completed]

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
