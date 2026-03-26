import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Helpers ──────────────────────────────────────────────────────────────────
def make_task(title="Walk", duration=20, priority=3,
              category="walk", time_of_day="morning",
              frequency="none", due_date=None):
    return Task(
        title=title,
        duration_minutes=duration,
        priority=priority,
        category=category,
        time_of_day=time_of_day,
        frequency=frequency,
        is_recurring=(frequency != "none"),
        due_date=due_date or date.today()
    )

def make_scheduler(available_minutes=120):
    owner = Owner(name="Tester", available_minutes=available_minutes)
    pet   = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)


# ── 1. Task Completion ────────────────────────────────────────────────────────
def test_mark_complete_changes_status():
    """Happy path: completing a task sets completed=True."""
    task = make_task("Morning Walk")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


# ── 2. Task Addition ──────────────────────────────────────────────────────────
def test_add_task_increases_pet_task_count():
    """Happy path: adding tasks grows the pet's task list."""
    pet = Pet(name="Luna", species="Cat", age=2)
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task("Feeding"))
    pet.add_task(make_task("Grooming"))
    assert len(pet.get_tasks()) == 2


# ── 3. Sorting Correctness ────────────────────────────────────────────────────
def test_sort_by_time_returns_chronological_order():
    """Tasks should be ordered morning → afternoon → evening."""
    owner, pet, scheduler = make_scheduler()
    pet.add_task(make_task("Evening Task",   time_of_day="evening"))
    pet.add_task(make_task("Morning Task",   time_of_day="morning"))
    pet.add_task(make_task("Afternoon Task", time_of_day="afternoon"))
    scheduler.load_tasks()

    sorted_tasks = scheduler.sort_by_time()
    times = [t.time_of_day for t in sorted_tasks]
    assert times == ["morning", "afternoon", "evening"]


def test_sort_by_priority_highest_first():
    """Higher priority tasks should appear before lower ones."""
    owner, pet, scheduler = make_scheduler()
    pet.add_task(make_task("Low",    priority=1))
    pet.add_task(make_task("High",   priority=5))
    pet.add_task(make_task("Medium", priority=3))
    scheduler.load_tasks()

    sorted_tasks = scheduler.sort_by_priority()
    priorities = [t.priority for t in sorted_tasks]
    assert priorities == [5, 3, 1]


# ── 4. Recurrence Logic ───────────────────────────────────────────────────────
def test_daily_task_creates_next_occurrence():
    """Completing a daily task should auto-create one due tomorrow."""
    owner, pet, scheduler = make_scheduler()
    task = make_task("Morning Walk", frequency="daily", due_date=date.today())
    pet.add_task(task)

    pet.complete_task("Morning Walk")

    tasks = pet.get_tasks()
    assert len(tasks) == 2  # original + new occurrence
    new_task = tasks[1]
    assert new_task.due_date == date.today() + timedelta(days=1)
    assert new_task.completed == False


def test_weekly_task_creates_next_occurrence():
    """Completing a weekly task should auto-create one due in 7 days."""
    owner, pet, scheduler = make_scheduler()
    task = make_task("Bath Time", frequency="weekly", due_date=date.today())
    pet.add_task(task)

    pet.complete_task("Bath Time")

    tasks = pet.get_tasks()
    assert len(tasks) == 2
    assert tasks[1].due_date == date.today() + timedelta(weeks=1)


def test_one_time_task_does_not_recur():
    """Completing a non-recurring task should NOT create a new occurrence."""
    owner, pet, scheduler = make_scheduler()
    task = make_task("Vet Visit", frequency="none")
    pet.add_task(task)

    pet.complete_task("Vet Visit")

    assert len(pet.get_tasks()) == 1  # no new task added
    assert pet.get_tasks()[0].completed == True


# ── 5. Conflict Detection ─────────────────────────────────────────────────────
def test_conflict_detected_when_time_exceeded():
    """Scheduler should warn when total task time exceeds available minutes."""
    owner, pet, scheduler = make_scheduler(available_minutes=20)
    pet.add_task(make_task("Long Task", duration=60))
    scheduler.load_tasks()

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0
    assert any("exceed" in c for c in conflicts)


def test_duplicate_task_conflict_detected():
    """Scheduler should warn when the same task appears twice in a slot."""
    owner, pet, scheduler = make_scheduler(available_minutes=120)
    pet.add_task(make_task("Morning Walk", time_of_day="morning"))
    pet.add_task(make_task("Morning Walk", time_of_day="morning"))  # duplicate
    scheduler.load_tasks()

    conflicts = scheduler.detect_conflicts()
    assert any("duplicate" in c.lower() for c in conflicts)


def test_no_conflict_when_schedule_fits():
    """No conflicts should be reported when tasks fit within available time."""
    owner, pet, scheduler = make_scheduler(available_minutes=120)
    pet.add_task(make_task("Short Walk", duration=20, time_of_day="morning"))
    scheduler.load_tasks()

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


# ── 6. Edge Cases ─────────────────────────────────────────────────────────────
def test_scheduler_with_no_tasks():
    """Scheduler should handle a pet with no tasks without crashing."""
    owner, pet, scheduler = make_scheduler()
    # no tasks added
    schedule = scheduler.generate_schedule()
    assert schedule == []


def test_filter_incomplete_excludes_done_tasks():
    """filter_incomplete should only return tasks not yet completed."""
    owner, pet, scheduler = make_scheduler()
    pet.add_task(make_task("Done Task"))
    pet.add_task(make_task("Pending Task"))
    scheduler.load_tasks()
    scheduler.tasks[0].mark_complete()

    incomplete = scheduler.filter_incomplete()
    assert len(incomplete) == 1
    assert incomplete[0].title == "Pending Task"


def test_scheduler_does_not_exceed_available_time():
    """Generated schedule total should never exceed available minutes."""
    owner, pet, scheduler = make_scheduler(available_minutes=30)
    pet.add_task(make_task("Task A", duration=25, priority=5))
    pet.add_task(make_task("Task B", duration=20, priority=3))

    schedule = scheduler.generate_schedule()
    total = sum(t.duration_minutes for t in schedule)
    assert total <= 30