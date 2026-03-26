from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care activity with scheduling metadata."""

    title: str
    duration_minutes: int
    priority: int          # 1 (low) to 5 (high)
    category: str          # "walk", "feeding", "meds", "grooming", etc.
    is_recurring: bool = False
    completed: bool = False
    time_of_day: Optional[str] = None  # "morning", "afternoon", "evening"

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def __str__(self):
        """Return a human-readable string representation of the task."""
        status = "✅" if self.completed else "⬜"
        time = f" [{self.time_of_day}]" if self.time_of_day else ""
        return f"{status} {self.title}{time} ({self.duration_minutes} min, priority {self.priority})"


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
        return f"Owner: {self.name} | Available: {self.available_minutes} min/day | Pets: {len(self.pets)}"


class Scheduler:
    """Generates and manages a daily care schedule based on priority and available time."""

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

    def detect_conflicts(self) -> List[str]:
        """Flag if total task duration exceeds the owner's available time."""
        conflicts = []
        total = self.get_total_duration()
        if total > self.owner.available_minutes:
            conflicts.append(
                f"Total tasks ({total} min) exceed available time "
                f"({self.owner.available_minutes} min)."
            )
        return conflicts

    def get_total_duration(self) -> int:
        """Return the total duration in minutes of all loaded tasks."""
        return sum(t.duration_minutes for t in self.tasks)

    def generate_schedule(self) -> List[Task]:
        """Build a daily plan by fitting highest-priority tasks into available time."""
        self.load_tasks()
        sorted_tasks = self.sort_by_priority()
        schedule = []
        time_used = 0

        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                schedule.append(task)
                time_used += task.duration_minutes

        return schedule

    def print_schedule(self) -> None:
        """Print the generated daily schedule to the console."""
        schedule = self.generate_schedule()
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