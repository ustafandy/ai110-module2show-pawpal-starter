from datetime import date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 1, 15)


def make_owner_with_two_pets():
    owner = Owner(name="Jordan", available_minutes=60)
    biscuit = Pet(name="Biscuit", species="Dog")
    mochi = Pet(name="Mochi", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    return owner, biscuit, mochi


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, "high"))

    assert len(pet.tasks) == 1


def test_get_all_tasks_keeps_pet_context():
    owner = Owner(name="Jordan", available_minutes=60)
    biscuit = Pet(name="Biscuit", species="Dog")
    mochi = Pet(name="Mochi", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    biscuit.add_task(Task("Feeding", 10, "high"))
    mochi.add_task(Task("Feeding", 5, "high"))

    pairs = owner.get_all_tasks()

    assert [(pet.name, task.title) for pet, task in pairs] == [
        ("Biscuit", "Feeding"),
        ("Mochi", "Feeding"),
    ]


def test_scheduler_uses_all_pets_and_respects_time_and_priority():
    owner = Owner(name="Jordan", available_minutes=40)
    biscuit = Pet(name="Biscuit", species="Dog")
    mochi = Pet(name="Mochi", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    biscuit.add_task(Task("Fetch", 30, "low"))
    biscuit.add_task(Task("Walk", 30, "high"))
    mochi.add_task(Task("Medication", 5, "medium"))
    done = Task("Feeding", 5, "high")
    done.mark_complete()
    mochi.add_task(done)

    plan = Scheduler(owner).generate_plan()

    assert [(pet.name, task.title) for pet, task in plan] == [
        ("Biscuit", "Walk"),
        ("Mochi", "Medication"),
    ]


# --- Phase 4: algorithmic layer ---


def test_sort_by_time_orders_tasks_chronologically_across_pets():
    owner, biscuit, mochi = make_owner_with_two_pets()
    biscuit.add_task(Task("Evening walk", 30, "high", time="18:00", due_date=DAY))
    mochi.add_task(Task("Breakfast", 5, "high", time="7:05", due_date=DAY))  # normalized to 07:05
    biscuit.add_task(Task("Lunch", 10, "medium", time="12:00", due_date=DAY))

    ordered = Scheduler(owner).sort_by_time()

    assert [(pet.name, task.time) for pet, task in ordered] == [
        ("Mochi", "07:05"),
        ("Biscuit", "12:00"),
        ("Biscuit", "18:00"),
    ]


def test_invalid_time_is_rejected():
    with pytest.raises(ValueError):
        Task("Walk", 30, "high", time="25:99")


def test_filter_tasks_by_pet_and_completion():
    owner, biscuit, mochi = make_owner_with_two_pets()
    walk = Task("Walk", 30, "high", due_date=DAY)
    walk.mark_complete()
    biscuit.add_task(walk)
    biscuit.add_task(Task("Feeding", 10, "high", due_date=DAY))
    mochi.add_task(Task("Feeding", 5, "high", due_date=DAY))
    scheduler = Scheduler(owner)

    by_pet = scheduler.filter_tasks(pet_name="biscuit")
    pending = scheduler.filter_tasks(completed=False)
    both = scheduler.filter_tasks(pet_name="Biscuit", completed=True)

    assert [task.title for _, task in by_pet] == ["Walk", "Feeding"]
    assert [(pet.name, task.title) for pet, task in pending] == [
        ("Biscuit", "Feeding"),
        ("Mochi", "Feeding"),
    ]
    assert len(both) == 1 and both[0][1] is walk  # same Task object, not a copy


def test_next_occurrence_dates():
    assert Task("Walk", 30, "high", frequency="daily", due_date=DAY).next_occurrence().due_date == date(2026, 1, 16)
    assert Task("Bath", 30, "low", frequency="weekly", due_date=DAY).next_occurrence().due_date == date(2026, 1, 22)
    assert Task("Vet", 60, "high", due_date=DAY).next_occurrence() is None


def test_complete_recurring_task_adds_one_next_occurrence():
    pet = Pet(name="Biscuit", species="Dog")
    walk = Task("Walk", 30, "high", time="07:00", frequency="daily", due_date=date(2026, 1, 31))
    pet.add_task(walk)

    next_walk = pet.complete_task(walk)
    repeat = pet.complete_task(walk)  # e.g. a Streamlit rerun

    assert walk.completed is True
    assert repeat is None
    assert len(pet.tasks) == 2
    assert next_walk is pet.tasks[1]
    assert next_walk.completed is False
    assert next_walk.due_date == date(2026, 2, 1)  # rolls over the month correctly
    assert (next_walk.title, next_walk.time, next_walk.frequency) == ("Walk", "07:00", "daily")


def test_complete_non_recurring_task_adds_nothing():
    pet = Pet(name="Mochi", species="Cat")
    vet = Task("Vet visit", 60, "high", due_date=DAY)
    pet.add_task(vet)

    assert pet.complete_task(vet) is None
    assert len(pet.tasks) == 1


def test_generate_plan_skips_future_occurrences():
    owner, biscuit, _ = make_owner_with_two_pets()
    walk = Task("Walk", 30, "high", frequency="daily")  # due today
    biscuit.add_task(walk)
    biscuit.complete_task(walk)  # next occurrence is tomorrow

    assert Scheduler(owner).generate_plan() == []


def test_detect_conflicts_flags_same_time_across_pets():
    owner, biscuit, mochi = make_owner_with_two_pets()
    biscuit.add_task(Task("Walk", 30, "high", time="08:00", due_date=DAY))
    mochi.add_task(Task("Medication", 5, "high", time="08:00", due_date=DAY))
    mochi.add_task(Task("Brush", 15, "low", time="09:00", due_date=DAY))

    conflicts = Scheduler(owner).detect_conflicts()

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Walk" in conflicts[0] and "Biscuit" in conflicts[0]
    assert "Medication" in conflicts[0] and "Mochi" in conflicts[0]


def test_detect_conflicts_ignores_completed_and_other_days():
    owner, biscuit, mochi = make_owner_with_two_pets()
    done = Task("Walk", 30, "high", time="08:00", due_date=DAY)
    done.mark_complete()
    biscuit.add_task(done)
    mochi.add_task(Task("Medication", 5, "high", time="08:00", due_date=DAY))
    mochi.add_task(Task("Feeding", 5, "high", time="08:00", due_date=date(2026, 1, 16)))

    assert Scheduler(owner).detect_conflicts() == []


# --- Phase 5: edge cases ---


def test_sort_by_time_orders_by_date_before_time():
    owner, biscuit, mochi = make_owner_with_two_pets()
    biscuit.add_task(Task("Tomorrow walk", 30, "high", time="07:00", due_date=date(2026, 1, 16)))
    mochi.add_task(Task("Tonight feeding", 5, "high", time="19:00", due_date=DAY))

    ordered = Scheduler(owner).sort_by_time()

    assert [task.title for _, task in ordered] == ["Tonight feeding", "Tomorrow walk"]


def test_invalid_frequency_is_rejected_and_case_is_normalized():
    with pytest.raises(ValueError):
        Task("Walk", 30, "high", frequency="monthly")

    assert Task("Walk", 30, "high", frequency="Daily").frequency == "daily"


def test_task_that_exactly_fills_remaining_time_is_scheduled():
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 20, "high"))
    pet.add_task(Task("Brush", 10, "low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert [task.title for _, task in plan] == ["Walk", "Brush"]
    assert scheduler.skipped_tasks == []


def test_owner_with_pet_but_no_tasks_is_handled_gracefully():
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Biscuit", species="Dog"))
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks(pet_name="Biscuit") == []
    assert scheduler.detect_conflicts() == []
    assert "no pending tasks" in scheduler.explain_plan()
