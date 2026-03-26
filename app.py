import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Session State ────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care planner")

# ── Section 1: Owner Setup ───────────────────────────────────────────────────
st.header("👤 Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name")
    available_mins = st.number_input(
        "How many minutes do you have today?", min_value=10, max_value=480, value=90
    )
    submitted = st.form_submit_button("Save Owner")
    if submitted and owner_name:
        st.session_state.owner = Owner(
            name=owner_name,
            available_minutes=int(available_mins)
        )
        st.success(f"Owner '{owner_name}' saved!")

# ── Section 2: Add a Pet ─────────────────────────────────────────────────────
if st.session_state.owner:
    st.header("🐶 Add a Pet")

    with st.form("pet_form"):
        pet_name    = st.text_input("Pet name")
        pet_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
        pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
        add_pet     = st.form_submit_button("Add Pet")

        if add_pet and pet_name:
            new_pet = Pet(name=pet_name, species=pet_species, age=int(pet_age))
            st.session_state.owner.add_pet(new_pet)
            st.session_state.pets = st.session_state.owner.get_pets()
            st.success(f"Pet '{pet_name}' added!")

# ── Section 3: Add a Task ────────────────────────────────────────────────────
if st.session_state.pets:
    st.header("📋 Add a Task")

    pet_names = [p.name for p in st.session_state.pets]

    with st.form("task_form"):
        selected_pet  = st.selectbox("Assign task to", pet_names)
        task_title    = st.text_input("Task title (e.g. Morning Walk)")
        task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=20)
        task_priority = st.slider("Priority (1=low, 5=high)", 1, 5, 3)
        task_category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
        task_time     = st.selectbox("Time of day", ["morning", "afternoon", "evening"])
        recurring     = st.checkbox("Recurring daily?")
        add_task      = st.form_submit_button("Add Task")

        if add_task and task_title:
            new_task = Task(
                title=task_title,
                duration_minutes=int(task_duration),
                priority=task_priority,
                category=task_category,
                time_of_day=task_time,
                is_recurring=recurring
            )
            # Find the right pet and add the task
            for pet in st.session_state.pets:
                if pet.name == selected_pet:
                    pet.add_task(new_task)
            st.success(f"Task '{task_title}' added to {selected_pet}!")

# ── Section 4: Generate Schedule ─────────────────────────────────────────────
if st.session_state.pets:
    st.header("📅 Generate Schedule")

    if st.button("Generate Today's Plan"):
        scheduler = Scheduler(st.session_state.owner)
        schedule  = scheduler.generate_schedule()
        conflicts = scheduler.detect_conflicts()

        if conflicts:
            for c in conflicts:
                st.warning(c)

        if not schedule:
            st.error("No tasks fit in your available time.")
        else:
            total = sum(t.duration_minutes for t in schedule)
            st.success(f"Scheduled {len(schedule)} tasks — {total} min total")

            for i, task in enumerate(schedule, 1):
                status = "✅" if task.completed else "⬜"
                st.markdown(
                    f"**{i}. {status} {task.title}** — "
                    f"{task.duration_minutes} min | "
                    f"Priority {task.priority} | "
                    f"{task.time_of_day or 'anytime'}"
                )
