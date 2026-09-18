# 🎯 Number Guessing Game

A polished, non-flickering terminal number guessing game built with [Rich](https://github.com/Textualize/rich). Features a live-updating dashboard, difficulty levels, scoring with streak bonuses, and persistent best-score tracking — all in the terminal.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Rich](https://img.shields.io/badge/built%20with-Rich-magenta)

✨ Features

- **Live dashboard UI** — score, streak, wins/losses, and a progress bar update in place with no flicker
- **Three difficulty levels** — Easy, Medium, and Hard, all with 5 preset attempts
- **Custom attempts mode** — choose your own tries between 15 to 20, or skip to play with default 5 attempts
- **Scoring system** — points based on difficulty, speed, and current win streak
- **Persistent best score** — automatically saved to `scores.json` and reloaded on launch
- **Visual feedback only** — no audio, just color-coded hints (too high / too low / locked / lost)
- **Fast mode** — skip intro animations and pauses for quicker rounds

📦 Requirements

- Python 3.8+
- [rich](https://pypi.org/project/rich/)

🚀 Installation & Run

```bash
git clone https://github.com/SwarnadeepYadav/number_guessing_game.git
cd number_guessing_game
pip install -r requirements.txt
python game.py
python game.py --fast
If you don't have a `requirements.txt` yet, create one with:
rich

▶️ Usage

Run the game:
python game.py
Run in fast mode (skips intro typing animation and shortens result-screen pauses):
python game.py --fast
Controls

- Enter a number within the shown range to make a guess
- Type `q` at any prompt to quit
- After a round ends, choose `Y` to play again or `N` to exit

🎮 How to Play

1. Pick a difficulty:
   - *Easy* — range 1–50
   - *Medium* — range 50–100
   - *Hard* — range 100–200
   All difficulties start with 5 preset attempts.
2. You will be asked `Want custom attempts (15-20)?`
3. Press `y` and enter a number between 15-20 for custom tries, or press `n` / `Enter` to skip and play with 5 attempts.
4. Guess the secret number — the dashboard tells you if you're too high or too low.

🧮 Scoring

Points per win are calculated as:
points = difficulty bonus + speed bonus + streak bonus
speed bonus  = (max_attempts - attempts_used + 1) * 100
streak bonus = current_streak * 25
Your best score is saved automatically whenever a new high score is reached.

📁 Project Structure
.
├── game.py           # Main game code
├── scores.json       # Auto-generated best-score save file
└── README.md
🛠️ Built With

- https://github.com/Textualize/rich — terminal formatting, layouts, and live UI updates

📄 License

This project is available under the [MIT License](LICENSE).

---
Made with ❤️ by Swarnadeep Yadav
