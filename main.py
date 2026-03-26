from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ────────────────────────────────────────────────────────────────────
owner = Owner(name="Sasha", available_minutes=120)

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Luna", species="Cat", age=5)

# Add tasks OUT OF ORDER to test sorting
dog.add_task(Task("Evening Walk",    30, priority=4, category="walk",    time_of_day="evening",   is_recurring=True))
dog.add_task(Task("Flea Medicine",    5, priority=3, category="meds",    time_of_day="afternoon", is_recurring=False))
dog.add_task(Task("Morning Walk",    30, priority=5, category="walk",    time_of_day="morning",   is_recurring=True))
dog.add_task(Task("Breakfast",       10, priority=5, category="feeding", time_of_day="morning",   is_recurring=True))

cat.add_task(Task("Dinner Feeding",  10, priority=4, category="feeding", time_of_day="evening",   is_recurring=True))
cat.add_task(Task("Brush Fur",       15, priority=2, category="grooming",time_of_day="afternoon", is_recurring=False))
cat.add_task(Task("Afternoon Nap",    5, priority=1, category="enrichment", time_of_day="afternoon", is_recurring=True))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)
scheduler.load_tasks()

# ── Test 1: Sort by Time of Day ──────────────────────────────────────────────
print("\n🕐 Tasks sorted by time of day:")
for task in scheduler.sort_by_time():
    print(f"  {task}")

# ── Test 2: Sort by Priority ─────────────────────────────────────────────────
print("\n⭐ Tasks sorted by priority:")
for task in scheduler.sort_by_priority():
    print(f"  {task}")

# ── Test 3: Filter by Pet ────────────────────────────────────────────────────
print("\n🐶 Buddy's tasks only:")
for task in scheduler.filter_by_pet("Buddy"):
    print(f"  {task}")

print("\n🐱 Luna's tasks only:")
for task in scheduler.filter_by_pet("Luna"):
    print(f"  {task}")

# ── Test 4: Filter Incomplete ────────────────────────────────────────────────
# Mark one task complete first
scheduler.tasks[0].mark_complete()
print("\n⬜ Incomplete tasks only:")
for task in scheduler.filter_incomplete():
    print(f"  {task}")

# ── Test 5: Recurring Reset ──────────────────────────────────────────────────
print("\n🔄 After resetting recurring tasks:")
scheduler.reset_recurring()
for task in scheduler.tasks:
    print(f"  {task}")

# ── Test 6: Full Schedule ────────────────────────────────────────────────────
scheduler.print_schedule()