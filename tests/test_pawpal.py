import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pawpal_system import Owner, Pet, Task, Scheduler


# --- Helper to create a sample task ---
def make_task(title="Walk", duration=20, priority=3):
    return Task(
        title=title,
        duration_minutes=duration,
        priority=priority,
        category="walk",
        is_recurring=False
    )


# --- Test 1: Task Completion ---
def test_mark_complete_changes_status():
    task = make_task("Morning Walk")
    assert task.completed == False  # starts incomplete
    task.mark_complete()
    assert task.completed == True   # should now be complete


# --- Test 2: Task Addition ---
def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.get_tasks()) == 0  # starts with no tasks
    pet.add_task(make_task("Walk"))
    pet.add_task(make_task("Feeding"))
    assert len(pet.get_tasks()) == 2  # should now have 2 tasks


# --- Bonus Test 3: Scheduler respects available time ---
def test_scheduler_fits_tasks_in_available_time():
    owner = Owner(name="Sasha", available_minutes=30)
    pet = Pet(name="Luna", species="Cat", age=2)
    pet.add_task(make_task("Big Task", duration=25, priority=5))
    pet.add_task(make_task("Small Task", duration=10, priority=3))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()
    total = sum(t.duration_minutes for t in schedule)
    assert total <= 30  # should never exceed available time