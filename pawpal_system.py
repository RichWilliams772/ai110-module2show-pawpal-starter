from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, timedelta


@dataclass
class Task:
    """Represents a single pet care activity with scheduling metadata."""

    title: str
    duration_minutes: int
    priority: int                    # 1 (low) to 5 (high)
    category: str                    # "walk", "feeding", "meds", "grooming", etc.
    is_recurring: bool = False
    frequency: str = "none"          # "daily", "weekly", or "none"
    completed: bool = False
    time_of_day: Optional[str] = None  # "morning", "afternoon", "evening"
    due_date: Optional[date] = None    # when this task is next due

    def mark_complete(self) -> Optional["Task"]:
        """
        Mark this task as completed.
        If the task is recurring, returns a new Task instance
        scheduled for the next occurrence. Otherwise returns None.
        """
        self.completed = True

        if self.frequency == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                is_recurring=self.is_recurring,
                frequency=self.frequency,
                completed=False,
                time_of_day=self.time_of_day,
                due_date=next_due
            )

        elif self.frequency == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(weeks=1)
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                is_recurring=self.is_recurring,
                frequency=self.frequency,
                completed=False,
                time_of_day=self.time_of_day,
                due_date=next_due
            )

        return None  # non-recurring tasks return nothing

    def __str__(self):
        """Return a human-readable string representation of the task."""
        status = "✅" if self.completed else "⬜"
        time   = f" [{self.time_of_day}]" if self.time_of_day else ""
        due    = f" (due {self.due_date})" if self.due_date else ""
        freq   = f" 🔁{self.frequency}" if self.frequency != "none" else ""
        return (
            f"{status} {self.title}{time}{freq}{due} "
            f"({self.duration_minutes} min, priority {self.priority})"
        )


@dataclass
class Pet:
    """Represents a pet with its personal details and associated care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def complete_task(self, title: str) -> None:
        """
        Mark a task complete by title. If it's recurring,
        automatically add the next occurrence to this pet's task list.
        """
        for task in self.tasks:
            if task.title.lower() == title.lower() and not task.completed:
                next_task = task.mark_complete()
                if next_task:
                    self.tasks.append(next_task)
                    print(f"🔁 '{task.title}' completed — next due {next_task.due_date}")
                else:
                    print(f"✅ '{task.title}' completed (one-time task)")
                return
        print(f"⚠️  Task '{title}' not found or already completed.")

    def __str__(self):
        """Return a human-readable string representation of the pet."""
        return f"{self.name} ({self.species}, age {self.age})"


class Owner:
    """Represents a pet owner with available time and a list of pets."""

    def __init__(self, name: str, available_minutes: int):
        """Initialize the owner with a name and daily available time in minutes."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list of pets."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Collect and return all tasks across all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def __str__(self):
        """Return a human-readable summary of the owner."""
        return (
            f"Owner: {self.name} | "
            f"Available: {self.available_minutes} min/day | "
            f"Pets: {len(self.pets)}"
        )


class Scheduler:
    """Generates and manages a daily care schedule based on priority and available time."""

    TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, None: 3}

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner whose pets and tasks will be scheduled."""
        self.owner = owner
        self.tasks: List[Task] = []

    def load_tasks(self) -> None:
        """Pull all tasks from all of the owner's pets into the scheduler."""
        self.tasks = self.owner.get_all_tasks()

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def sort_by_time(self) -> List[Task]:
        """Return tasks sorted by time of day: morning → afternoon → evening."""
        return sorted(
            self.tasks,
            key=lambda t: self.TIME_ORDER.get(t.time_of_day, 3)
        )

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return only tasks belonging to the pet with the given name."""
        for pet in self.owner.get_pets():
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    def filter_incomplete(self) -> List[Task]:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def filter_by_category(self, category: str) -> List[Task]:
        """Return only tasks matching the given category."""
        return [t for t in self.tasks if t.category.lower() == category.lower()]

    def filter_due_today(self) -> List[Task]:
        """Return only tasks due today or with no due date set."""
        today = date.today()
        return [
            t for t in self.tasks
            if t.due_date is None or t.due_date <= today
        ]

    def reset_recurring(self) -> None:
        """Reset completion status for all recurring tasks (call at start of new day)."""
        for task in self.tasks:
            if task.is_recurring:
                task.completed = False

    def detect_conflicts(self) -> List[str]:
        """
        Detect scheduling conflicts including:
        - Total time exceeding available minutes
        - A single time slot exceeding 60 minutes
        - Duplicate tasks scheduled in the same slot
        Returns a list of warning strings (never crashes).
        """
        conflicts = []

        # 1. Total time conflict
        total = self.get_total_duration()
        if total > self.owner.available_minutes:
            conflicts.append(
                f"⚠️  Total tasks ({total} min) exceed available time "
                f"({self.owner.available_minutes} min)."
            )

        # 2. Per-slot overload (over 60 min in one slot is too much)
        slot_totals: dict = {"morning": 0, "afternoon": 0, "evening": 0}
        for task in self.tasks:
            if task.time_of_day in slot_totals:
                slot_totals[task.time_of_day] += task.duration_minutes
        for slot, slot_total in slot_totals.items():
            if slot_total > 60:
                conflicts.append(
                    f"⚠️  '{slot}' slot is overloaded ({slot_total} min). "
                    f"Consider moving some tasks."
                )

        # 3. Duplicate task titles in the same time slot
        seen: dict = {}  # {(title, time_of_day): count}
        for task in self.tasks:
            key = (task.title.lower(), task.time_of_day)
            seen[key] = seen.get(key, 0) + 1
        for (title, slot), count in seen.items():
            if count > 1:
                conflicts.append(
                    f"⚠️  '{title}' appears {count} times in the "
                    f"'{slot}' slot — possible duplicate."
                )

        return conflicts

    def get_total_duration(self) -> int:
        """Return the total duration in minutes of all loaded tasks."""
        return sum(t.duration_minutes for t in self.tasks)

    def generate_schedule(self) -> List[Task]:
        """Build a daily plan sorted by time of day, fitting tasks into available time."""
        self.load_tasks()
        due_today = self.filter_due_today()
        sorted_tasks = sorted(
            due_today,
            key=lambda t: (self.TIME_ORDER.get(t.time_of_day, 3), -t.priority)
        )
        schedule  = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                schedule.append(task)
                time_used += task.duration_minutes
        return schedule

    def print_schedule(self) -> None:
        """Print the generated daily schedule to the console."""
        schedule  = self.generate_schedule()
        conflicts = self.detect_conflicts()

        print(f"\n📅 Daily Schedule for {self.owner.name}")
        print(f"⏱  Available time: {self.owner.available_minutes} min\n")

        if conflicts:
            print("⚠️  Conflicts detected:")
            for c in conflicts:
                print(f"   - {c}")
            print()

        if not schedule:
            print("No tasks fit in the available time.")
            return

        for i, task in enumerate(schedule, 1):
            print(f"{i}. {task}")

        total = sum(t.duration_minutes for t in schedule)
        print(f"\nTotal scheduled time: {total} min")