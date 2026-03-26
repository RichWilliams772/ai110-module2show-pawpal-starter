from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Sasha", available_minutes=120)
dog   = Pet(name="Buddy", species="Dog", age=3)

# Daily recurring task
dog.add_task(Task(
    title="Morning Walk",
    duration_minutes=30,
    priority=5,
    category="walk",
    is_recurring=True,
    frequency="daily",
    time_of_day="morning",
    due_date=date.today()
))

# Weekly recurring task
dog.add_task(Task(
    title="Bath Time",
    duration_minutes=20,
    priority=3,
    category="grooming",
    is_recurring=True,
    frequency="weekly",
    time_of_day="afternoon",
    due_date=date.today()
))

# One-time task
dog.add_task(Task(
    title="Vet Appointment",
    duration_minutes=60,
    priority=5,
    category="meds",
    is_recurring=False,
    frequency="none",
    time_of_day="afternoon",
    due_date=date.today()
))

owner.add_pet(dog)

print("── Before completing tasks ──")
for t in dog.get_tasks():
    print(f"  {t}")

print("\n── Completing tasks ──")
dog.complete_task("Morning Walk")   # daily → next due tomorrow
dog.complete_task("Bath Time")      # weekly → next due in 7 days
dog.complete_task("Vet Appointment") # one-time → no new task

print("\n── All tasks after completion ──")
for t in dog.get_tasks():
    print(f"  {t}")