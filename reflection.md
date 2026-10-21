# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. Enter basic information about themselves and their pet, such as their name, the pet's name and species, and how much time they have available for pet care today.
2. Add and edit care tasks for a pet, such as a walk, feeding, or medication, giving each task a duration and a priority.
3. Generate a daily care plan that fits their available time, ordered by priority, and see an explanation of why each task was included or left out.

- Briefly describe your initial UML design.

  My design has four classes: Owner, Pet, Task, and Scheduler. An Owner has zero or more Pets, and each Pet has zero or more Tasks. A Scheduler is created for one Owner and reaches the Tasks through that Owner's Pets. Owner, Pet, and Task are dataclasses because they mainly hold data. Scheduler is a regular class because it holds the planning behavior.

- What classes did you include, and what responsibilities did you assign to each?

  - **Owner**: stores the owner's name, how many minutes they have available for pet care, their preferences, and their pets. It can add a pet and collect every task across all pets, so the Scheduler has one place to get them.
  - **Pet**: stores the pet's name, species, and its care tasks. It is responsible for adding and removing tasks and returning the tasks that are not yet done.
  - **Task**: represents one care activity with a title, duration in minutes, priority (low, medium, or high), and whether it is completed. It can mark itself complete and turn its priority into a number so tasks can be sorted.
  - **Scheduler**: builds the daily plan for an Owner. It chooses and orders tasks that fit the available time by priority, keeps track of which tasks were scheduled and which were skipped, and explains why.

**b. Design changes**

- Did your design change during implementation?

  Yes. While reviewing the Phase 1 design, before writing any scheduling logic, I made one important change. Later, in Phase 4, I extended the design without changing its structure.

- If yes, describe at least one change and why you made it.

  - **Issue:** `Owner.get_all_tasks()` returned a flat list of Tasks, and a Task does not know which Pet it belongs to. Once the tasks were passed to the Scheduler, the pet information was lost. With two pets that both have a "Feeding" task, the plan could not tell them apart.
  - **Change:** Tasks now travel to the Scheduler as `(Pet, Task)` pairs. `Owner.get_all_tasks()`, `Scheduler.generate_plan()`, and the Scheduler's `scheduled_tasks` and `skipped_tasks` all use `list[tuple[Pet, Task]]`. I updated the UML to match and added a dependency from Scheduler to Pet. I chose pairs over adding a `pet_name` field to Task so the pet's name is not stored twice and cannot get out of sync.
  - **Why it matters:** The plan has to say which pet each task is for, such as "Feeding (Mochi)". `explain_plan()` also needs the pet to explain why a task was scheduled or skipped. Keeping the pair means the Scheduler always has that information without searching through the Owner's pets to find where a task came from.
  - **How it paid off later:** Every Phase 4 method (`sort_by_time()`, `filter_tasks()`, and `detect_conflicts()`) also returns or uses `(Pet, Task)` pairs. Filtering by pet name works because the pet travels with the task. A conflict warning can say `'Feeding' (Biscuit), 'Give medication' (Mochi)`, and if both pets had a "Feeding" task at 12:30, the warning still shows which pet each one belongs to. With a flat list of bare Tasks, the warning would just say "Feeding, Feeding", which is not useful.
  - **Phase 4 extension:** I added `time`, `frequency`, and `due_date` to Task, `next_occurrence()` to Task, and `complete_task()` to Pet for recurring tasks. All three new fields have defaults, so the existing code and tests kept working. The final design is in `diagrams/uml_final.mmd`, and the original is kept in `diagrams/uml.mmd`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

  The scheduler considers:
  - **Available time:** the owner's `available_minutes` is a hard limit. Tasks are added only while they fit, and anything that doesn't fit is skipped with an explanation.
  - **Priority:** high-priority tasks are planned first, then medium, then low.
  - **Duration:** among tasks with the same priority, shorter tasks go first, so more tasks fit in the time left.
  - **Completion status and due date:** completed tasks and tasks due on a later date (such as tomorrow's copy of a daily walk) are left out of today's plan.
  - **Start time:** used for sorting the task list and for detecting conflicts, not for choosing what goes in the plan.

  Owner `preferences` exist in the model but are not used by the scheduler yet.

- How did you decide which constraints mattered most?

  I started from what a busy owner actually needs: the important care (feeding, medication, a walk) must happen even on a short day. That made available time the hard limit and priority the main ordering rule. Putting shorter tasks first on ties was a simple way to fit more care into the time left. I kept preferences out of the algorithm because there was no clear, testable rule for them, and adding vague logic would have made the plan harder to explain.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

  Conflict detection only checks for unfinished tasks with the exact same due date and start time, such as two tasks at 08:00 on the same day, even if they belong to different pets. It does not detect overlapping durations. For example, a 30-minute walk at 07:00 and a feeding at 07:15 overlap, but they are not reported as a conflict.

  A second tradeoff is that the plan is greedy: it goes through tasks in priority order and takes each one that fits. That is not always the combination that uses the most minutes, but it guarantees that a high-priority task is never dropped to make room for low-priority ones.

- Why is that tradeoff reasonable for this scenario?

  The most common scheduling mistake is booking two tasks for the same time. Checking exact start times catches that and keeps the logic simple and easy to test. Full overlap detection would need start and end times for every task, plus extra rules, for example for tasks one person can do at the same time. That was more than this phase needed.

  I also compared other ways to write `detect_conflicts()`. Comparing every pair of tasks takes O(n²) time and reports three warnings when three tasks share a slot, instead of one. Sorting the tasks and then grouping neighbors with `itertools.groupby` is slightly shorter, but no faster, and it only works if the tasks are sorted first, which is easy to get wrong. I kept the current version, which groups tasks in a dictionary by `(due_date, time)`. It runs in roughly linear time and reads directly as "group tasks by time slot, then report any slot with more than one task." If I add overlap detection later, I would revisit this, because grouping by exact time cannot detect tasks that overlap.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

  I used AI in every phase, with me reviewing and deciding at each step:
  - **Design (Phase 1):** brainstorming the four-class architecture and reviewing the UML. The AI pointed out that having `Owner.get_all_tasks()` return a flat list of Tasks would lose which Pet each Task belonged to, which led to the `(Pet, Task)` change.
  - **Implementation (Phases 2–3):** turning the approved UML skeleton into working code for Task, Pet, Owner, and Scheduler, writing the `main.py` CLI demo, and connecting the classes to the Streamlit UI.
  - **Algorithms (Phase 4):** adding sorting, filtering, recurring tasks, and conflict detection, and comparing different ways to implement them.
  - **Testing (Phase 5):** generating tests for normal behavior and edge cases, such as month rollover for recurring tasks, a task that exactly fills the remaining time, and a pet with no tasks.
  - **Finalization (Phase 6):** polishing the UI, updating the final UML, and reviewing the README and this reflection.

  I used a separate AI chat for each of these stages. That kept each conversation focused on one job. The design chat didn't get mixed up with implementation details, and the testing chat started from the finished code instead of from earlier drafts. When I started a new chat, I gave it the current files and the decisions already made (such as keeping `(Pet, Task)` pairs), so the AI worked from the real state of the project instead of from an older version it remembered.

- What kinds of prompts or questions were most helpful?

  The most helpful prompts were specific and set limits: implement the existing design without redesigning it, keep the code beginner-friendly, preserve the `(Pet, Task)` design, and do not build future-phase features. Asking the AI to state its plan before editing and to report any design assumptions afterward made its work easy to review. For algorithms, asking it to compare a few alternatives with their tradeoffs was more useful than asking for "the best" solution.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

  During the algorithms phase, the AI suggested replacing my dictionary-based `detect_conflicts()` with an alternative: either comparing every pair of tasks, or sorting the tasks and grouping them with `itertools.groupby`. I evaluated both and rejected them. Pairwise comparison is O(n²) and reports three separate warnings when three tasks share a slot. The `groupby` version is not faster and only works correctly if the input is sorted first, which adds a hidden requirement. The existing version was already efficient, readable, and tested, so changing it would have added risk without a real benefit.

  Earlier, I accepted the `(Pet, Task)` pair approach only after checking that it solved a real problem: the Scheduler needs pet context to plan for multiple pets, for example to tell Biscuit's "Feeding" apart from Mochi's. I also kept each phase limited to its scope. In Phase 2, I did not add enums for priority, recurring-task logic, conflict handling, or extra architecture, because none of those were needed yet and they would have made the code harder to follow.

- How did you evaluate or verify what the AI suggested?

  I ran the code and checked the results instead of trusting the explanation. After Phase 2, I ran `python main.py` and checked that the schedule was correct: each task appeared with the right pet, tasks were ordered by priority, and a task that did not fit the available time was skipped with an explanation. Then I ran `python -m pytest`, and all 4 tests at that point passed. Two tests were required (marking a task complete, and adding a task to a pet). The other two check that `Owner.get_all_tasks()` keeps pet context across multiple pets and that the Scheduler pulls tasks from all pets, leaves out completed tasks, sorts by priority, and stays within the available time.

  After Phases 4 and 5, I re-ran `main.py` to check sorting, recurrence, filtering, and the conflict warning, and the suite grew to 17 passing tests. For the UI, I ran the Streamlit app and tested adding pets and tasks, generating a schedule, and seeing conflict warnings in the browser.

  Throughout the project, I acted as the lead architect. I made the design decisions, such as the four classes, `(Pet, Task)` pairs, and exact-time conflict detection. I reviewed each AI suggestion, decided what to accept or reject, verified behavior by running the app and the tests, and kept the implementation aligned with the assignment. The AI wrote most of the code from my direction; my job was to make sure it was the right code.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

  The suite in `tests/test_pawpal.py` has 17 tests:
  - **Core behavior:** marking a task complete, adding a task to a pet, and `get_all_tasks()` keeping pet context when two pets have tasks with the same name.
  - **Scheduling:** the plan uses tasks from all pets, skips completed tasks, orders by priority, and stays within the available minutes. A task that exactly fills the remaining time is still scheduled.
  - **Sorting:** tasks are ordered by time across pets, by date before time, and `"7:05"` is normalized to `"07:05"` so it sorts correctly.
  - **Filtering:** by pet name (case-insensitive), by completion status, and by both. Filtering returns the original Task objects, not copies.
  - **Recurrence:** daily tasks move forward 1 day and weekly tasks 7 days, including across a month end. Completing a task twice does not create a duplicate, one-time tasks do not repeat, and tomorrow's occurrence is left out of today's plan.
  - **Conflicts:** same date and time across pets is flagged, while completed tasks and tasks on other days are ignored.
  - **Edge cases and invalid input:** a pet with no tasks, invalid times, and unknown frequencies.

- Why were these tests important?

  The Phase 5 strategy was to test each feature's normal case and then the edge case most likely to break it. Several tests protect earlier design decisions. For example, the test with two pets that both have "Feeding" protects the `(Pet, Task)` design, and the "complete twice" test protects against duplicate recurring tasks when Streamlit reruns the script. Using fixed dates (`date(2026, 1, 15)`) instead of today's date makes the results the same on every run. Whenever I or the AI changed the code, running `python -m pytest` showed right away whether existing behavior broke.

**b. Confidence**

- How confident are you that your scheduler works correctly?

  About 4 out of 5. Every core feature has tests for its normal case and key edge cases, all 17 tests pass, and the CLI demo produces the expected output. I'm not at 5 because of known gaps: conflict detection only checks exact start times, an invalid priority is only rejected when a plan is generated, `generate_plan()` depends on the real current date, and the Streamlit UI is only tested by hand.

- What edge cases would you test next if you had more time?

  - Overlapping durations (for example, 07:00 for 30 minutes and 07:15), if overlap detection were added.
  - An invalid priority given when a task is created.
  - `generate_plan()` with a fixed "today" so overdue tasks can be tested reliably.
  - Three or more tasks in the same time slot producing exactly one warning.
  - Recurring tasks across a year end and leap day.
  - Removing a task that doesn't exist, and pets whose names differ only by case.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

  I'm most satisfied with the `(Pet, Task)` design decision. Making it early, before writing any scheduling logic, meant that sorting, filtering, conflict detection, and the UI could all show which pet a task belongs to without any extra work. I'm also happy that the backend stayed simple and readable while still supporting recurrence and conflict warnings, and that it is well covered by tests.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

  - Detect overlapping durations, not just identical start times.
  - Validate priority when a Task is created, the same way time and frequency are.
  - Let `generate_plan()` take a date, so it is easier to test and could plan future days.
  - Use the owner's preferences (for example, "morning walks") when ordering tasks.
  - Let users edit or delete tasks in the UI, and save data between sessions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  AI is very effective at producing code quickly, but the important decisions still have to come from me. The most valuable moments were not when the AI wrote code, but when I questioned a suggestion. Sometimes I accepted it after checking it solved a real problem, as with `(Pet, Task)`. Other times I rejected it because the existing solution was already good enough, as with `detect_conflicts()`. Acting as the lead architect meant keeping a clear design, giving the AI focused tasks in separate chats, and verifying everything by running the code and the tests. A small, clear design also made the AI's work better, because there was less room for it to guess.
