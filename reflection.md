# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design includes four classes: Owner, Pet, Task, and Scheduler.

- Owner: Holds the pet owner's name and available time for the day. Responsible for managing a list of pets.
- Pet: Represents a pet with a name, species, and age. Holds a list of tasks assigned to it.
- Task: A dataclass that stores a task's title, duration, priority, category, and whether it recurs daily.
- Scheduler: The brain of the app. Takes the owner and their pets' tasks, sorts them by priority, detects conflicts, and generates a daily care plan.

Three core actions a user can perform:
1. Add owner and pet info (name, species, available time)
2. Add or edit care tasks for a pet (e.g., walk, feeding, meds) with duration and priority
3. Generate a daily schedule that organizes tasks based on priority and time constraints

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, After AI review of the skeleton, three potential improvements 
were identified:

1. Scheduler needs to explicitly loop through owner.pets to 
   gather all tasks — this relationship was missing.
2. Task may need a time_of_day field to support precise 
   scheduling (not just priority ordering).
3. A completed boolean field on Task would help track which 
   tasks are done vs pending.

These changes will be implemented in Phase 2.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler checks for slot overload (total minutes per time slot)
but does not track exact start/end times for each task. This means
two 30-minute tasks both labeled "morning" are flagged as a conflict
even if they could realistically run back-to-back. This tradeoff
keeps the logic simple and readable, but a more precise version would
assign start times and check for true overlaps using time ranges.

I chose simplicity over precision because the app is designed for
casual pet owners, not minute-by-minute scheduling.---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
