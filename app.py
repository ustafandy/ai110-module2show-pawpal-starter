from datetime import date
from datetime import time as clock_time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a busy pet owner plan daily care across all of their pets. Add your pets and
their care tasks, then let the scheduler build a plan that fits your available time,
puts high-priority tasks first, and warns you about tasks booked at the same time.
"""
)

with st.expander("How scheduling works"):
    st.markdown(
        """
- **Priority first:** high-priority tasks are planned before medium and low; on ties, shorter tasks go first.
- **Time budget:** tasks are added until your available minutes run out; anything that doesn't fit is skipped and explained.
- **Due today only:** completed tasks and tasks due on a later date are left out of today's plan.
- **Recurring tasks:** completing a daily or weekly task automatically adds its next occurrence.
- **Conflicts:** pending tasks with the same date and start time are flagged (overlapping durations are not checked).
"""
    )

st.divider()

st.subheader("Owner & Pets")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=1440, value=60
)

# Create the Owner once; later reruns reuse it so pets and tasks persist.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
owner: Owner = st.session_state.owner
owner.name = owner_name
owner.available_minutes = int(available_minutes)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    clean_name = pet_name.strip()
    if not clean_name:
        st.error("Please enter a pet name.")
    elif any(pet.name.lower() == clean_name.lower() for pet in owner.pets):
        st.error(f"{owner.name} already has a pet named {clean_name}.")
    else:
        owner.add_pet(Pet(name=clean_name, species=species))
        st.success(f"Added {clean_name} the {species}.")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": pet.name, "species": pet.species, "tasks": len(pet.tasks)}
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add care tasks for each pet. These feed into the scheduler.")

if owner.pets:
    task_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        task_time = st.time_input("Start time", value=clock_time(8, 0))
    with col5:
        frequency = st.selectbox("Repeats", ["none", "daily", "weekly"])
    with col6:
        due_date = st.date_input("Due date", value=date.today())

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Please enter a task title.")
        else:
            pet = next(pet for pet in owner.pets if pet.name == task_pet_name)
            pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    time=task_time.strftime("%H:%M"),
                    frequency=frequency,
                    due_date=due_date,
                )
            )
            st.success(f"Added '{task_title.strip()}' for {pet.name} at {task_time.strftime('%H:%M')}.")
else:
    st.caption("Add a pet first to start adding tasks.")

scheduler = Scheduler(owner)


def task_rows(pairs):
    """Turn (Pet, Task) pairs into table rows for display."""
    return [
        {
            "due date": str(task.due_date),
            "time": task.time,
            "pet": pet.name,
            "title": task.title,
            "minutes": task.duration_minutes,
            "priority": task.priority,
            "repeats": task.frequency,
            "status": "done" if task.completed else "pending",
        }
        for pet, task in pairs
    ]


if owner.get_all_tasks():
    st.write("Current tasks (sorted by date and time):")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [pet.name for pet in owner.pets])
    with filter_col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])

    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    if filtered:
        st.table(task_rows(scheduler.sort_by_time(filtered)))
    else:
        st.info("No tasks match these filters.")

    # Completing a recurring task adds its next occurrence through Pet.complete_task().
    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if pending:
        choice = st.selectbox(
            "Mark a task complete",
            range(len(pending)),
            format_func=lambda i: (
                f"{pending[i][1].due_date} {pending[i][1].time} – "
                f"{pending[i][1].title} ({pending[i][0].name})"
            ),
        )
        if st.button("Mark complete"):
            done_pet, done_task = pending[choice]
            next_task = done_pet.complete_task(done_task)
            message = f"Completed '{done_task.title}' for {done_pet.name}."
            if next_task is not None:
                message += (
                    f" It repeats {next_task.frequency}, so the next one was added for "
                    f"{next_task.due_date} at {next_task.time}."
                )
            # Rerun so the tables above refresh; show the message after the rerun.
            st.session_state.completed_message = message
            st.rerun()

    if "completed_message" in st.session_state:
        st.success(st.session_state.pop("completed_message"))

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.markdown("**Scheduling conflicts**")
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")
        st.caption("Consider moving one of these tasks to a different start time.")
    else:
        st.success("No scheduling conflicts: no two pending tasks share the same date and time.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Builds today's plan from all pets' pending tasks due today or earlier, "
    "by priority, within your available minutes."
)

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if plan:
        used = sum(task.duration_minutes for _, task in plan)
        st.success(
            f"Scheduled {len(plan)} task(s) using {used} of {owner.available_minutes} minutes."
        )
        st.table(
            [
                {
                    "order": index,
                    "time": task.time,
                    "pet": pet.name,
                    "title": task.title,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                }
                for index, (pet, task) in enumerate(plan, start=1)
            ]
        )
    else:
        st.warning("No tasks could be scheduled for today.")

    if scheduler.skipped_tasks:
        st.warning(
            "Skipped (not enough time): "
            + ", ".join(f"{task.title} ({pet.name})" for pet, task in scheduler.skipped_tasks)
        )

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(f"{len(conflicts)} time conflict(s) found. See the Tasks section above.")

    with st.expander("Why this plan?", expanded=True):
        st.text(scheduler.explain_plan())
