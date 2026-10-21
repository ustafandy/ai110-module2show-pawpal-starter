import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
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
    st.table([{"name": pet.name, "species": pet.species} for pet in owner.pets])
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

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Please enter a task title.")
        else:
            pet = next(pet for pet in owner.pets if pet.name == task_pet_name)
            pet.add_task(
                Task(title=task_title.strip(), duration_minutes=int(duration), priority=priority)
            )
            st.success(f"Added '{task_title.strip()}' for {pet.name}.")
else:
    st.caption("Add a pet first to start adding tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": pet.name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "completed": task.completed,
            }
            for pet, task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Builds today's plan from all pets' tasks using the Scheduler.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if plan:
        st.success(f"Scheduled {len(plan)} task(s).")
        st.table(
            [
                {
                    "pet": pet.name,
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                }
                for pet, task in plan
            ]
        )
    else:
        st.warning("No tasks could be scheduled.")
    st.markdown("**Why this plan:**")
    st.text(scheduler.explain_plan())
