# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. Enter basic information about themselves and their pet, such as their name, the pet's name and species, and how much time they have available for pet care today.
2. Add and edit care tasks for a pet, such as a walk, feeding, or medication, giving each task a duration and a priority.
3. Generate a daily care plan that fits their available time, ordered by priority, and see an explanation of why each task was included or left out.

- Briefly describe your initial UML design.

  My design has four classes. An Owner has zero or more Pets, and each Pet has zero or more Tasks. A Scheduler is created for one Owner and reaches the Tasks through that Owner's Pets. Owner, Pet, and Task are dataclasses because they mainly hold data. Scheduler is a regular class because it holds the planning behavior.

- What classes did you include, and what responsibilities did you assign to each?

  - **Owner**: stores the owner's name, how many minutes they have available for pet care, their preferences, and their pets. It can add a pet and collect every task across all pets, so the Scheduler has one place to get them.
  - **Pet**: stores the pet's name, species, and its care tasks. It is responsible for adding and removing tasks and returning the tasks that are not yet done.
  - **Task**: represents one care activity with a title, duration in minutes, priority (low, medium, or high), and whether it is completed. It can mark itself complete and turn its priority into a number so tasks can be sorted.
  - **Scheduler**: builds the daily plan for an Owner. It chooses and orders tasks that fit the available time by priority, keeps track of which tasks were scheduled and which were skipped, and explains why.

**b. Design changes**

- Did your design change during implementation?

  Yes. While reviewing the Phase 1 design, before writing any scheduling logic, I made one change.

- If yes, describe at least one change and why you made it.

  - **Issue:** `Owner.get_all_tasks()` returned a flat list of Tasks, and a Task does not know which Pet it belongs to. Once the tasks were passed to the Scheduler, the pet information was lost. With two pets that both have a "Feeding" task, the plan could not tell them apart.
  - **Change:** Tasks now travel to the Scheduler as `(Pet, Task)` pairs. `Owner.get_all_tasks()`, `Scheduler.generate_plan()`, and the Scheduler's `scheduled_tasks` and `skipped_tasks` all use `list[tuple[Pet, Task]]`. I updated the UML to match and added a dependency from Scheduler to Pet. I chose pairs over adding a `pet_name` field to Task so the pet's name is not stored twice and cannot get out of sync.
  - **Why it matters:** The plan has to say which pet each task is for, such as "Feeding (Mochi)". `explain_plan()` also needs the pet to explain why a task was scheduled or skipped. Keeping the pair means the Scheduler always has that information without searching through the Owner's pets to find where a task came from.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

  Conflict detection only checks for unfinished tasks with the exact same due date and start time, such as two tasks at 08:00 on the same day, even if they belong to different pets. It does not detect overlapping durations. For example, a 30-minute walk at 07:00 and a feeding at 07:15 overlap, but they are not reported as a conflict.

- Why is that tradeoff reasonable for this scenario?

  The most common scheduling mistake is booking two tasks for the same time. Checking exact start times catches that and keeps the logic simple and easy to test. Full overlap detection would need start and end times for every task, plus extra rules, for example for tasks one person can do at the same time. That was more than this phase needed.

  I also compared other ways to write `detect_conflicts()`. Comparing every pair of tasks takes O(n²) time and reports three warnings when three tasks share a slot, instead of one. Sorting the tasks and then grouping neighbors with `itertools.groupby` is slightly shorter, but no faster, and it only works if the tasks are sorted first, which is easy to get wrong. I kept the current version, which groups tasks in a dictionary by `(due_date, time)`. It runs in roughly linear time and reads directly as "group tasks by time slot, then report any slot with more than one task." If I add overlap detection later, I would revisit this, because grouping by exact time cannot detect tasks that overlap.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

  I used AI for a design review and for implementation. During the Phase 1 design review, the AI pointed out that having `Owner.get_all_tasks()` return a flat list of Tasks would lose which Pet each Task belonged to. In Phase 2, I used AI to turn the approved UML skeleton into working code for Task, Pet, Owner, and Scheduler, to write the `main.py` CLI demo, and to write the tests.

- What kinds of prompts or questions were most helpful?

  The most helpful prompts were specific and set limits: implement the existing design without redesigning it, keep the code beginner-friendly, preserve the `(Pet, Task)` design, and do not build future-phase features. Asking the AI to state its plan before editing and to report any design assumptions afterward made its work easy to review.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

  I accepted the `(Pet, Task)` pair approach only after checking that it solved a real problem: the Scheduler needs pet context to plan for multiple pets, for example to tell Biscuit's "Feeding" apart from Mochi's. I also deliberately kept the implementation to the current phase. I did not add enums for priority, recurring-task logic, conflict handling, or extra architecture, because none of those were needed yet and they would have made the code harder to follow.

- How did you evaluate or verify what the AI suggested?

  I ran `python main.py` and checked that the schedule was correct: each task appeared with the right pet, tasks were ordered by priority, and a task that did not fit the available time was skipped with an explanation. I then ran `python -m pytest`, and all 4 tests passed. Two tests were required (marking a task complete, and adding a task to a pet). The other two check that `Owner.get_all_tasks()` keeps pet context across multiple pets and that the Scheduler pulls tasks from all pets, leaves out completed tasks, sorts by priority, and stays within the available time.

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
