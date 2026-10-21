"""CLI demo for PawPal+: builds a sample owner with two pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task

DAY_START_MINUTES = 8 * 60  # display start times beginning at 08:00


def format_clock(total_minutes: int) -> str:
    """Turn minutes since midnight into an HH:MM string."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="Dog")
    mochi = Pet(name="Mochi", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", 30, "high"))
    biscuit.add_task(Task("Feeding", 10, "high"))
    biscuit.add_task(Task("Fetch in the yard", 40, "low"))
    mochi.add_task(Task("Feeding", 5, "high"))
    mochi.add_task(Task("Give medication", 5, "medium"))
    mochi.add_task(Task("Brush fur", 15, "medium"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("=" * 50)
    print(f"Today's Schedule for {owner.name}'s pets")
    print("=" * 50)

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


if __name__ == "__main__":
    main()
