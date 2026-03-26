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
The scheduler considers three main constraints:

1. Time: The owner's available_minutes caps how many tasks can fit
   in a day. Tasks are only added to the schedule if they fit within
   the remaining time budget.

2. Priority: Tasks are ranked 1–5. Higher priority tasks are scheduled
   first, so critical tasks like meds or feeding are never bumped by
   lower-priority ones like grooming.

3. Time of day: Tasks are tagged morning, afternoon, or evening and
   sorted chronologically so the schedule flows naturally through the day.

I decided that time was the most important constraint because no matter
how high a task's priority is, it cannot be scheduled if there is no
time for it. Priority comes second because it determines which tasks
get the limited time slots. Time of day is last because it affects
order, not inclusion — a task can still run even if its preferred
slot is flexible.
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

I used GitHub Copilot throughout the project in several ways:
- Phase 1: Used Copilot Chat to generate the initial Mermaid UML diagram
  from my brainstormed class descriptions.
- Phase 2: Used Inline Chat to flesh out method implementations and 
  suggest the get_all_tasks() pattern for Scheduler.
- Phase 4: Used Edit Mode to add timedelta logic for recurring tasks.
- Phase 5: Used Generate Tests to draft the initial test structure,
  then manually added edge cases.

The most effective features were Inline Chat for quick method 
suggestions and #file references for context-aware feedback.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?


One AI suggestion I rejected: Copilot suggested using a dictionary 
to map pet names to task lists in Scheduler instead of looping through 
owner.pets. While slightly faster, it would have broken the single 
source of truth — tasks live on Pet objects, not the Scheduler.
Keeping the loop made the relationship between classes cleaner and 
easier to test.

Using separate chat sessions for each phase helped me avoid context 
confusion. The testing session stayed focused on pytest patterns 
without mixing in UML or UI questions.

As lead architect, I learned that AI is best used for scaffolding 
and boilerplate — but design decisions like "where does data live?" 
and "what should each class be responsible for?" require human judgment.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the following behaviors:

1. Task completion: Verified that mark_complete() correctly changes 
   a task's status from False to True.

2. Task addition: Confirmed that adding tasks to a Pet object 
   increases the task count correctly.

3. Sorting: Verified that sort_by_time() returns tasks in morning → 
   afternoon → evening order, and sort_by_priority() returns highest 
   priority first.

4. Recurring logic: Confirmed that completing a daily task creates a 
   new task due tomorrow, a weekly task creates one due in 7 days, 
   and a one-time task creates no new occurrence.

5. Conflict detection: Verified warnings fire when total time is 
   exceeded and when duplicate tasks appear in the same slot.

6. Edge cases: Tested that an empty pet (no tasks) returns an empty 
   schedule without crashing, and that the scheduler never exceeds 
   the owner's available minutes.

These tests were important because scheduling logic is easy to break 
silently — a bug in sort order or recurrence wouldn't crash the app 
but would give the user wrong results.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence level: ⭐⭐⭐⭐ (4/5)

I am confident the core behaviors work correctly — all 13 tests pass 
and cover both happy paths and edge cases.

If I had more time, I would test:
- A pet with 10+ tasks to check performance at scale
- Two pets sharing the same task name to check filter_by_pet accuracy
- A task with no due_date set to verify filter_due_today handles None
- What happens when available_minutes is set to 0
- Recurring tasks that are completed multiple times in a row
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the algorithmic layer in Phase 4. Building 
sorting, filtering, recurring tasks, and conflict detection from scratch 
using Python gave me a clear understanding of how a real scheduling 
system works under the hood. Seeing all 13 tests pass confirmed that 
the logic was solid and not just "working by accident."

I also found the CLI-first workflow valuable — testing in main.py 
before connecting to the UI meant I caught bugs in the logic early, 
before they became harder-to-debug UI problems.
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration I would redesign two things:

1. Time slot precision: Right now tasks are grouped into morning, 
   afternoon, and evening. A better version would assign actual start 
   times (e.g. 8:00 AM) and check for true overlaps using time ranges, 
   not just slot totals.

2. Multi-pet conflict detection: The current conflict detector treats 
   all tasks as one pool. A future version would check conflicts 
   per-pet so an overloaded morning for one pet doesn't block 
   another pet's schedule.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The most important thing I learned is that AI is a powerful 
scaffolding tool, but it cannot make architectural decisions for you. 
Copilot could generate method bodies quickly, but every time I asked 
"where should this logic live?" — in Task, Pet, or Scheduler — I had 
to reason through it myself using OOP principles.
Being the "lead architect" means using AI to build faster while 
staying responsible for the design. The cleaner the design, the 
more useful AI assistance becomes — because good structure gives 
AI the context it needs to make accurate suggestions.

