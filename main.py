"""CLI demo for PawPal+: builds a sample owner with two pets, prints today's schedule,
and demonstrates sorting, filtering, recurring tasks, and conflict detection."""

from pawpal_system import Owner, Pet, Scheduler, Task

DAY_START_MINUTES = 8 * 60  # display start times beginning at 08:00


def format_clock(total_minutes: int) -> str:
    """Turn minutes since midnight into an HH:MM string."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def print_header(title: str) -> None:
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def print_pairs(pairs) -> None:
    for pet, task in pairs:
        status = "done" if task.completed else "pending"
        print(
            f"  {task.due_date} {task.time}  {task.title:<18} for {pet.name:<8} "
            f"[{task.frequency}, {status}]"
        )


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="Dog")
    mochi = Pet(name="Mochi", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added deliberately out of chronological order.
    biscuit.add_task(Task("Fetch in the yard", 40, "low", time="17:00"))
    biscuit.add_task(Task("Morning walk", 30, "high", time="07:00", frequency="daily"))
    biscuit.add_task(Task("Feeding", 10, "high", time="12:30"))
    mochi.add_task(Task("Brush fur", 15, "medium", time="19:15", frequency="weekly"))
    mochi.add_task(Task("Feeding", 5, "high", time="06:45"))
    mochi.add_task(Task("Give medication", 5, "medium", time="12:30"))  # same time as Biscuit's feeding

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print_header(f"Today's Schedule for {owner.name}'s pets")

    clock = DAY_START_MINUTES
    for pet, task in plan:
        print(
            f"  {format_clock(clock)}  {task.title:<18} for {pet.name:<8} "
            f"({task.duration_minutes} min) [priority: {task.priority}]"
        )
        clock += task.duration_minutes

    if scheduler.skipped_tasks:
        print("\nSkipped (not enough time):")
        for pet, task in scheduler.skipped_tasks:
            print(f"  - {task.title} for {pet.name} ({task.duration_minutes} min)")

    print("\nWhy this plan:")
    print(scheduler.explain_plan())

    print_header("1. Sorting: all tasks by scheduled time")
    print_pairs(scheduler.sort_by_time())

    print_header("2. Recurring: completing daily and weekly tasks")
    walk = biscuit.tasks[1]
    next_walk = biscuit.complete_task(walk)
    print(f"  Completed '{walk.title}' due {walk.due_date} ({walk.frequency})")
    print(f"  -> next occurrence added for {next_walk.due_date} at {next_walk.time}")
    brush = mochi.tasks[0]
    next_brush = mochi.complete_task(brush)
    print(f"  Completed '{brush.title}' due {brush.due_date} ({brush.frequency})")
    print(f"  -> next occurrence added for {next_brush.due_date} at {next_brush.time}")
    again = biscuit.complete_task(walk)
    print(f"  Completing '{walk.title}' again creates: {again} (no duplicate)")

    print_header("3. Filtering")
    print("Biscuit's tasks:")
    print_pairs(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit")))
    print("Completed tasks (any pet):")
    print_pairs(scheduler.filter_tasks(completed=True))
    print("Mochi's pending tasks:")
    print_pairs(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)))

    print_header("4. Conflict detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts found.")


if __name__ == "__main__":
    main()
