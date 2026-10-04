# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- The hints were backwards
- The score at the end seemed unreasonable
- When I went over 100 or below 1, there was no out-of-bounds

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input |   Expected Behavior   | Actual Behavior | Console Output / Error |
|-------|-----------------------|-----------------|------------------------|
|  101  | Number out-of-bounds  |    Go Lower     | Line 36                |
|   1   |        Go Lower       |    Go Higher    | Line 45                |
|  100  |       Go Higher       |    Go Lower     | Line 45                |

---

## 2. How did you use AI as a teammate?

I used Claude Code as a teammate for this project. The suggestions that it gave were all valid and used to fix bugs. They were also used to fix bugs that were discovered after fixing the inital bugs in the Bug Reproduction Log.

---

## 3. Debugging and testing your fixes

I ran tests both manually and using pytest. All of the tests in test/test_game_logic.py were designed by Claude Code. By doing these, I was able to determine whether a feature was a bug or not. It also helped me determine whether the bugs were fixed to run as intended.

---

## 4. What did you learn about Streamlit and state?

I would explaim Streamlit as a way to view Python web applications. Similar to livestreams for HTML and npm for JSX. State gives us updates on the web app's status such as updates and errors.

---

## 5. Looking ahead: your developer habits

One habit from this project that I want to reuse for future labs or projects is by adding comments on sections with descriptions of bugs and how they were fixed. One thing I would do differently is to list all of the discovered bugs in one go so that Claude can explain them to me in one session and make connections between the bugs if appliciable. This project helped me see how useful AI generated code can be to save me time, but I should still stay cautious when accepting changes.
