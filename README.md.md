# Number Guessing Game - Rich Terminal Edition

A reel-ready Python terminal game designed for the VS Code terminal.

## Features

- Vibrant Rich-powered terminal UI
- Difficulty cards for Easy, Medium, and Hard
- Animated intro text
- Remaining-attempts visual gauge
- Score, best score, win/loss count, and streak tracking
- Safe input validation for text, negative numbers, and out-of-range guesses
- Retro win/loss ASCII screens
- Cross-platform visual feedback with no audio dependency

## Setup

1. Open VS Code.
2. Open this folder:

   ```text
   C:\Users\Swarnadeep Yadav\OneDrive\Documents\Vibe_code\number_guessing_rich
   ```

3. Open the VS Code terminal.
4. Install the dependency:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Run the game:

   ```powershell
   python main.py
   ```

## Useful Commands

Run without intro delays:

```powershell
python main.py --fast
```

Inside the game:

- `q` quits the game
- `Enter` accepts the current prompt

## Audio Notes

This version intentionally has no sound dependency. It uses color changes and stable terminal screens for win, loss, high, low, and error feedback.

## Recording Tips

- Use VS Code's dark theme.
- Zoom the terminal in with `Ctrl + Plus`.
- Use PowerShell or the integrated VS Code terminal.
- Run `python main.py --fast` if you want a snappier recording.
