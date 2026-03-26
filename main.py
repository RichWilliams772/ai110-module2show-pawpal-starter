from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Sasha", available_minutes=90)

# Create pets
dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Luna", species="Cat", age=5)

# Add tasks to dog
dog.add_task(Task(
    title="Morning Walk",
    duration_minutes=30,
    priority=5,
    category="walk",
    is_recurring=True,
    time_of_day="morning"
))
dog.add_task(Task(
    title="Breakfast Feeding",
    duration_minutes=10,
    priority=4,
    category="feeding",
    is_recurring=True,
    time_of_day="morning"
))
dog.add_task(Task(
    title="Flea Medicine",
    duration_minutes=5,
    priority=3,
    category="meds",
    is_recurring=False,
    time_of_day="afternoon"
))

# Add tasks to cat
cat.add_task(Task(
    title="Brush Fur",
    duration_minutes=15,
    priority=2,
    category="grooming",
    is_recurring=False,
    time_of_day="evening"
))
cat.add_task(Task(
    title="Dinner Feeding",
    duration_minutes=10,
    priority=4,
    category="feeding",
    is_recurring=True,
    time_of_day="evening"
))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Run scheduler
scheduler = Scheduler(owner)
scheduler.print_schedule()