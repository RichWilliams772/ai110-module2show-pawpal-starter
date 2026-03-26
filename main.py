from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Only 40 minutes available — intentionally tight
owner = Owner(name="Sasha", available_minutes=40)
dog   = Pet(name="Buddy", species="Dog", age=3)

# Two tasks in the same morning slot (will overload it)
dog.add_task(Task("Morning Walk",    30, priority=5, category="walk",
                  time_of_day="morning", frequency="daily", due_date=date.today()))
dog.add_task(Task("Breakfast",       20, priority=5, category="feeding",
                  time_of_day="morning", frequency="daily", due_date=date.today()))
dog.add_task(Task("Morning Walk",    30, priority=5, category="walk",
                  time_of_day="morning", frequency="daily", due_date=date.today()))  # duplicate!
dog.add_task(Task("Flea Medicine",   10, priority=3, category="meds",
                  time_of_day="afternoon", due_date=date.today()))

owner.add_pet(dog)

scheduler = Scheduler(owner)
scheduler.load_tasks()

print("── Conflict Detection Report ──")
conflicts = scheduler.detect_conflicts()

if conflicts:
    for c in conflicts:
        print(f"  {c}")
else:
    print("  No conflicts found!")

print()
scheduler.print_schedule()