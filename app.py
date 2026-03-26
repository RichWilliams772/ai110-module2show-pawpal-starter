import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

# ── Session State ─────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart daily pet care planner")

# ── Section 1: Owner Setup ────────────────────────────────────────────────────
st.header("👤 Owner Info")
with st.form("owner_form"):
    owner_name     = st.text_input("Your name")
    available_mins = st.number_input(
        "How many minutes do you have today?",
        min_value=10, max_value=480, value=90
    )
    if st.form_submit_button("Save Owner") and owner_name:
        st.session_state.owner = Owner(
            name=owner_name,
            available_minutes=int(available_mins)
        )
        st.success(f"✅ Owner '{owner_name}' saved with {available_mins} min available!")

# ── Section 2: Add a Pet ──────────────────────────────────────────────────────
if st.session_state.owner:
    st.header("🐶 Add a Pet")
    with st.form("pet_form"):
        pet_name    = st.text_input("Pet name")
        pet_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
        pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
        if st.form_submit_button("Add Pet") and pet_name:
            new_pet = Pet(name=pet_name, species=pet_species, age=int(pet_age))
            st.session_state.owner.add_pet(new_pet)
            st.session_state.pets = st.session_state.owner.get_pets()
            st.success(f"✅ {pet_species} '{pet_name}' added!")

    # Show current pets
    if st.session_state.pets:
        st.subheader("Your Pets")
        for pet in st.session_state.pets:
            st.markdown(f"- **{pet.name}** ({pet.species}, age {pet.age})")

# ── Section 3: Add a Task ─────────────────────────────────────────────────────
if st.session_state.pets:
    st.header("📋 Add a Task")
    pet_names = [p.name for p in st.session_state.pets]

    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_pet  = st.selectbox("Assign to pet", pet_names)
            task_title    = st.text_input("Task title")
            task_duration = st.number_input("Duration (min)", min_value=1, max_value=120, value=20)
            task_priority = st.slider("Priority (1=low, 5=high)", 1, 5, 3)
        with col2:
            task_category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
            task_time     = st.selectbox("Time of day", ["morning", "afternoon", "evening"])
            task_freq     = st.selectbox("Frequency", ["none", "daily", "weekly"])
            recurring     = task_freq != "none"

        if st.form_submit_button("Add Task") and task_title:
            new_task = Task(
                title=task_title,
                duration_minutes=int(task_duration),
                priority=task_priority,
                category=task_category,
                time_of_day=task_time,
                frequency=task_freq,
                is_recurring=recurring,
                due_date=date.today()
            )
            for pet in st.session_state.pets:
                if pet.name == selected_pet:
                    pet.add_task(new_task)
            st.success(f"✅ '{task_title}' added to {selected_pet}!")

    # Show tasks per pet
    st.subheader("Current Tasks")
    for pet in st.session_state.pets:
        if pet.get_tasks():
            st.markdown(f"**{pet.name}**")
            for task in pet.get_tasks():
                freq = f" 🔁 {task.frequency}" if task.frequency != "none" else ""
                st.markdown(
                    f"  - {task.title} | {task.duration_minutes} min | "
                    f"Priority {task.priority} | {task.time_of_day}{freq}"
                )

# ── Section 4: Generate Schedule ──────────────────────────────────────────────
if st.session_state.pets:
    st.header("📅 Generate Today's Schedule")

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox(
            "Filter by pet (optional)",
            ["All pets"] + [p.name for p in st.session_state.pets]
        )
    with col2:
        sort_mode = st.radio("Sort by", ["Time of day", "Priority"], horizontal=True)

    if st.button("🗓 Generate Today's Plan"):
        scheduler = Scheduler(st.session_state.owner)
        scheduler.load_tasks()

        # Apply pet filter
        if filter_pet != "All pets":
            tasks_to_show = scheduler.filter_by_pet(filter_pet)
            scheduler.tasks = tasks_to_show

        # Apply sort
        if sort_mode == "Time of day":
            schedule = scheduler.sort_by_time()
        else:
            schedule = scheduler.sort_by_priority()

        # Filter to only incomplete + due today
        schedule = [t for t in schedule if not t.completed]

        # ── Conflict Warnings ──────────────────────────────────────────────
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.subheader("⚠️ Scheduling Conflicts")
            for c in conflicts:
                st.warning(c)

        # ── Schedule Display ───────────────────────────────────────────────
        if not schedule:
            st.info("No pending tasks for today!")
        else:
            total = sum(t.duration_minutes for t in schedule)
            available = st.session_state.owner.available_minutes

            # Progress bar showing time used
            pct = min(total / available, 1.0)
            st.subheader("Today's Plan")
            st.progress(pct, text=f"{total} / {available} min used")

            if total > available:
                st.error(f"⚠️ You're {total - available} min over your available time!")
            else:
                st.success(f"✅ {len(schedule)} tasks scheduled — {total} min total")

            # Display tasks as a clean table
            table_data = []
            for i, task in enumerate(schedule, 1):
                freq = f"🔁 {task.frequency}" if task.frequency != "none" else "—"
                table_data.append({
                    "#":         i,
                    "Task":      task.title,
                    "Time":      task.time_of_day or "anytime",
                    "Duration":  f"{task.duration_minutes} min",
                    "Priority":  "⭐" * task.priority,
                    "Category":  task.category,
                    "Recurring": freq
                })
            st.table(table_data)