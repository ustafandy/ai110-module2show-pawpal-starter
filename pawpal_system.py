"""PawPal+ core system classes (Phase 1: architecture skeleton only).

Mirrors diagrams/uml.mmd. Method bodies are intentionally left
unimplemented; scheduling logic comes in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        raise NotImplementedError

    def priority_rank(self) -> int:
        """Return a numeric rank for the priority so tasks can be sorted."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        raise NotImplementedError

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        raise NotImplementedError

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner, their daily constraints, and their pets."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all of this owner's pets, paired with its pet."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner
        self.scheduled_tasks: list[tuple[Pet, Task]] = []
        self.skipped_tasks: list[tuple[Pet, Task]] = []

    def generate_plan(self) -> list[tuple[Pet, Task]]:
        """Choose and order tasks that fit the owner's available time, by priority."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Describe why each task was scheduled or skipped."""
        raise NotImplementedError
