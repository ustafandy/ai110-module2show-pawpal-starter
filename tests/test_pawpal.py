from pawpal_system import Owner, Pet, Scheduler, Task


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
