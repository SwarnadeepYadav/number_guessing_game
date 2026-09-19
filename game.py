import argparse
import json
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

try:
    from rich.align import Align
    from rich.bar import Bar
    from rich.console import Console, Group
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.text import Text
except ModuleNotFoundError:
    print("Missing dependency: rich")
    print("Install it with: python -m pip install -r requirements.txt")
    sys.exit(1)


APP_DIR = Path(__file__).resolve().parent
SCORE_FILE = APP_DIR / "scores.json"


@dataclass(frozen=True)
class Difficulty:
    name: str
    low: int
    high: int
    bonus: int
    color: str


DIFFICULTIES = {
    "1": Difficulty("Easy", 1, 50, 50, "spring_green1"),
    "2": Difficulty("Medium", 50, 100, 100, "cyan1"),
    "3": Difficulty("Hard", 100, 200, 180, "magenta1"),
}


class ScoreKeeper:
    """Tracks both this session's numbers and permanent lifetime stats.

    Lifetime stats (best_score, total_games, total_wins, total_losses,
    best_streak) are written to scores.json after every single round, so
    they survive closing the terminal, restarting the laptop, etc. They
    only ever go up - closing/reopening never resets them.
    """

    def __init__(self):
        # Session-only (resets each time you run the script)
        self.session_score = 0
        self.wins = 0
        self.losses = 0
        self.streak = 0

        # Lifetime (persisted to disk, never resets on its own)
        self.best_score = 0
        self.total_games = 0
        self.total_wins = 0
        self.total_losses = 0
        self.best_streak = 0

        self.load_stats()

    def load_stats(self):
        if not SCORE_FILE.exists():
            return
        try:
            data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return

        self.best_score = int(data.get("best_score", 0))
        self.total_games = int(data.get("total_games", 0))
        self.total_wins = int(data.get("total_wins", 0))
        self.total_losses = int(data.get("total_losses", 0))
        self.best_streak = int(data.get("best_streak", 0))

    def save_stats(self):
        data = {
            "best_score": self.best_score,
            "total_games": self.total_games,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "best_streak": self.best_streak,
        }
        SCORE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def record_win(self, points):
        self.wins += 1
        self.streak += 1
        self.session_score += points

        self.total_games += 1
        self.total_wins += 1
        if self.session_score > self.best_score:
            self.best_score = self.session_score
        if self.streak > self.best_streak:
            self.best_streak = self.streak

        self.save_stats()

    def record_loss(self):
        self.losses += 1
        self.streak = 0

        self.total_games += 1
        self.total_losses += 1

        self.save_stats()


class NumberGuessingGame:
    def __init__(self, fast=False):
        self.console = Console()
        self.score = ScoreKeeper()
        self.fast = fast

    def run(self):
        self.intro()

        while True:
            difficulty = self.choose_difficulty()
            max_attempts = self.choose_attempts(default=5)
            self.play_round(difficulty, max_attempts)

            self.print_score_table()
            if not self.ask_play_again():
                self.goodbye()
                break

    def intro(self):
        title = Text("NUMBER GUESSING GAME", justify="center")
        title.stylize("bold white on dark_green")

        subtitle = Text("A non-flickering Rich terminal game for VS Code", justify="center")
        subtitle.stylize("spring_green1")

        art = r"""
 _   _                 _                  ____                       
| \ | |_   _ _ __ ___ | |__   ___ _ __   / ___| _   _  ___  ___ ___  
|  \| | | | | '_ ` _ \| '_ \ / _ \ '__| | |  _ | | | |/ _ \/ __/ __| 
| |\  | |_| | | | | | | |_) |  __/ |    | |_| || |_| |  __/\__ \__ \ 
|_| \_|\__,_|_| |_| |_|_.__/ \___|_|     \____| \__,_|\___||___/___/
        """

        panel = Panel(
            Group(
                Align.center(Text(art, style="bright_magenta")),
                Align.center(title),
                Align.center(subtitle),
                Align.center(Text("Command: q = quit", style="yellow")),
            ),
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print(self.lifetime_stats_table())

        if not self.fast:
            self.type_line("Booting stable dashboard interface...", "bold cyan")
            time.sleep(0.35)
            self.type_line(
                "No flicker. No audio crashes. Visual cues do the work.",
                "bold spring_green1",
            )

    def choose_difficulty(self):
        table = Table.grid(expand=True)
        table.add_column(justify="center")
        table.add_column(justify="center")
        table.add_column(justify="center")

        cards = []
        for key, difficulty in DIFFICULTIES.items():
            card = Panel(
                f"[bold]{key}. {difficulty.name}[/bold]\n"
                f"[white]{difficulty.low} - {difficulty.high}[/white]\n"
                f"[yellow]+{difficulty.bonus} bonus[/yellow]",
                border_style=difficulty.color,
                padding=(1, 2),
            )
            cards.append(card)

        table.add_row(*cards)
        self.console.print("\n")
        self.console.print(table)

        while True:
            choice = Prompt.ask(
                "\n[bold spring_green1]>[/bold spring_green1] Select difficulty coordinates",
                choices=["1", "2", "3", "q"],
                default="2",
                console=self.console,
            )
            self.quit_if_requested(choice)
            if choice in DIFFICULTIES:
                return DIFFICULTIES[choice]

    def ask_play_again(self):
        replay_panel = Panel(
            Align.center(
                Text(
                    "Y = Play another round     N = Exit game",
                    style="bold spring_green1",
                )
            ),
            title="[bold white]NEXT MOVE[/bold white]",
            border_style="spring_green1",
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(replay_panel)

        while True:
            answer = self.console.input(
                "[bold spring_green1]>[/bold spring_green1] Choose Y or N: "
            ).strip().lower()

            if answer == "":
                return True
            if answer == "q":
                return False
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False

            self.console.print("[bold red1]Invalid choice.[/bold red1] Type Y or N.")

    def choose_attempts(self, default):
        while True:
            answer = Prompt.ask(
                f"[bold spring_green1]>[/bold spring_green1] Enter attempt limit "
                f"[dim](1-20, Enter for {default})[/dim]",
                default=str(default),
                console=self.console,
            ).strip()
            self.quit_if_requested(answer.lower())

            try:
                attempts = int(answer)
            except ValueError:
                self.console.print("[bold red1]Invalid input.[/bold red1] Use a whole number.")
                continue

            if 1 <= attempts <= 20:
                return attempts

            self.console.print("[bold red1]Attempt limit must be between 1 and 20.[/bold red1]")

    def play_round(self, difficulty, max_attempts):
        secret_number = random.randint(difficulty.low, difficulty.high)
        attempt = 0
        previous_guesses = []
        hint = "Enter your first coordinate scan."
        tone = "cyan1"
        result_screen = None

        layout = self.build_dashboard(
            attempt=attempt,
            max_attempts=max_attempts,
            hint=hint,
            tone=tone,
            previous_guesses=previous_guesses,
        )

        with Live(
            layout,
            console=self.console,
            refresh_per_second=10,
            auto_refresh=False,
            transient=False,
            screen=False,
        ) as live:
            while attempt < max_attempts and result_screen is None:
                live.update(
                    self.build_dashboard(
                        attempt=attempt,
                        max_attempts=max_attempts,
                        hint=hint,
                        tone=tone,
                        previous_guesses=previous_guesses,
                    ),
                    refresh=True,
                )

                # Pause the live renderer while we block on input.
                # This is the fix for the terminal filling up with
                # duplicate boxes: Live can't safely redraw in-place
                # while console.input() is also writing to the screen,
                # so we stop it first and restart it right after.
                live.stop()
                guess = self.ask_for_guess(difficulty, self.console)
                live.start(refresh=False)

                if guess is None:
                    hint = "Invalid coordinate. Enter a valid number in range."
                    tone = "red1"
                    continue

                attempt += 1
                previous_guesses.append(guess)

                if guess == secret_number:
                    points = self.calculate_points(difficulty, attempt, max_attempts)
                    self.score.record_win(points)
                    hint = "TARGET LOCKED. Correct coordinate found."
                    tone = "spring_green1"
                    live.update(
                        self.build_dashboard(
                            attempt=attempt,
                            max_attempts=max_attempts,
                            hint=hint,
                            tone=tone,
                            previous_guesses=previous_guesses,
                        ),
                        refresh=True,
                    )
                    time.sleep(0.4)
                    result_screen = self.win_screen(secret_number, attempt, points)
                    continue

                if guess > secret_number:
                    hint = "Signal too high. Drop to a smaller number."
                    tone = "orange1"
                else:
                    hint = "Signal too low. Push to a bigger number."
                    tone = "deep_sky_blue1"

            if result_screen is None:
                self.score.record_loss()
                result_screen = self.loss_screen(secret_number)

            live.update(result_screen, refresh=True)
            time.sleep(0.35 if not self.fast else 0.1)

    def ask_for_guess(self, difficulty, console):
        prompt = (
            f"[bold spring_green1]>[/bold spring_green1] Enter coordinates "
            f"[dim]({difficulty.low}-{difficulty.high})[/dim]: "
        )
        answer = console.input(prompt).strip().lower()
        self.quit_if_requested(answer)

        try:
            guess = int(answer)
        except ValueError:
            self.console.print("[bold red1]Rejected.[/bold red1] Coordinates must be numeric.")
            return None

        if guess < 0:
            self.console.print("[bold red1]Rejected.[/bold red1] Negative coordinates are blocked.")
            return None

        if guess < difficulty.low or guess > difficulty.high:
            self.console.print(
                f"[bold red1]Out of bounds.[/bold red1] Stay inside "
                f"{difficulty.low} to {difficulty.high}."
            )
            return None

        return guess

    def lifetime_stats_table(self):
        table = Table(title="All-Time Record", border_style="magenta1")
        table.add_column("Metric", style="bold white")
        table.add_column("Value", justify="right", style="spring_green1")
        table.add_row("Best Score", str(self.score.best_score))
        table.add_row("Total Games", str(self.score.total_games))
        table.add_row("Total Wins", str(self.score.total_wins))
        table.add_row("Total Losses", str(self.score.total_losses))
        table.add_row("Best Streak", str(self.score.best_streak))
        return table

    def print_score_table(self):
        score_table = Table(title="This Session", border_style="cyan1")
        score_table.add_column("Metric", style="bold white")
        score_table.add_column("Value", justify="right", style="spring_green1")
        score_table.add_row("Score", str(self.score.session_score))
        score_table.add_row("Wins", str(self.score.wins))
        score_table.add_row("Losses", str(self.score.losses))
        score_table.add_row("Streak", str(self.score.streak))
        self.console.print()
        self.console.print(score_table)
        self.console.print(self.lifetime_stats_table())

    def build_dashboard(self, attempt, max_attempts, hint, tone, previous_guesses):
        attempts_left = max_attempts - attempt
        guess_list = ", ".join(str(guess) for guess in previous_guesses) or "None yet"

        layout = Layout(name="root")
        layout.split_column(
            Layout(name="body", size=12),
            Layout(name="footer", size=4),
        )

        layout["body"].update(
            self.body_panel(
                attempts_left=attempts_left,
                max_attempts=max_attempts,
                hint=hint,
                tone=tone,
                previous_guesses=guess_list,
            )
        )
        layout["footer"].update(self.footer_panel())
        return layout

    def body_panel(self, attempts_left, max_attempts, hint, tone, previous_guesses):
        ratio = attempts_left / max_attempts
        bar_color = "spring_green1" if ratio >= 0.33 else "red1"

        progress = Bar(
            size=attempts_left,
            begin=0,
            end=max_attempts,
            width=36,
            color=bar_color,
            bgcolor="grey23",
        )

        attempts_text = Text(
            f"Attempts remaining: {attempts_left}/{max_attempts}",
            style=f"bold {bar_color}",
            justify="center",
        )

        body = Group(
            Align.center(Text(hint, style=f"bold {tone}")),
            Text(""),
            Align.center(progress),
            Align.center(attempts_text),
            Text(""),
            Align.center(Text(f"Previous scans: {previous_guesses}", style="dim")),
        )

        return Panel(
            body,
            title="[bold white]TARGET SCANNER[/bold white]",
            border_style=tone,
            padding=(1, 2),
        )

    def footer_panel(self):
        help_text = Text()
        help_text.append("q", style="bold red1")
        help_text.append(" quit   ", style="white")
        help_text.append("Numbers only", style="bold spring_green1")
        help_text.append("   No audio: visual cues show high/low/win/loss", style="dim")

        return Panel(
            Align.center(help_text),
            border_style="grey50",
            padding=(1, 2),
        )

    def calculate_points(self, difficulty, attempt, max_attempts):
        speed_bonus = (max_attempts - attempt + 1) * 100
        streak_bonus = self.score.streak * 25
        return difficulty.bonus + speed_bonus + streak_bonus

    def win_screen(self, secret_number, attempt, points):
        art = r"""
 __        ___ _   _ _   _ _____ ____
 \ \      / (_) \ | | \ | | ____|  _ \
  \ \ /\ / /| |  \| |  \| |  _| | |_) |
   \ V  V / | | |\  | |\  | |___|  _ <
    \_/\_/  |_|_| \_|_| \_|_____|_| \_\
        """

        return Panel(
            Group(
                Align.center(Text(art, style="bold spring_green1")),
                Align.center(Text(f"Secret coordinate: {secret_number}", style="bold white")),
                Align.center(Text(f"Solved in {attempt} attempt(s)", style="cyan1")),
                Align.center(Text(f"+{points} points", style="bold yellow")),
            ),
            title="[bold spring_green1]TARGET LOCKED[/bold spring_green1]",
            border_style="spring_green1",
            padding=(1, 2),
        )

    def loss_screen(self, secret_number):
        art = r"""
   ____    _    __  __ _____    _____     _______ ____
  / ___|  / \  |  \/  | ____|  / _ \ \   / / ____|  _ \
 | |  _  / _ \ | |\/| |  _|   | | | \ \ / /|  _| | |_) |
 | |_| |/ ___ \| |  | | |___  | |_| |\ V / | |___|  _ <
  \____/_/   \_\_|  |_|_____|  \___/  \_/  |_____|_| \_\
        """

        return Panel(
            Group(
                Align.center(Text(art, style="bold red1")),
                Align.center(Text(f"Correct coordinate: {secret_number}", style="bold white")),
                Align.center(Text("Scanner failed. Recalibrate and run it back.", style="yellow")),
            ),
            title="[bold red1]SIGNAL LOST[/bold red1]",
            border_style="red1",
            padding=(1, 2),
        )

    def goodbye(self):
        summary = Table(title="Session Summary", border_style="cyan1")
        summary.add_column("Metric", style="bold white")
        summary.add_column("Value", justify="right", style="spring_green1")
        summary.add_row("Score", str(self.score.session_score))
        summary.add_row("Wins", str(self.score.wins))
        summary.add_row("Losses", str(self.score.losses))
        summary.add_row("Final Streak", str(self.score.streak))
        self.console.print(summary)
        self.console.print(self.lifetime_stats_table())
        self.console.print("[bold cyan1]Session closed. Best of luck![/bold cyan1]")

    def type_line(self, message, style):
        if self.fast:
            self.console.print(message, style=style)
            return

        for character in message:
            self.console.print(character, style=style, end="")
            time.sleep(0.012)
        self.console.print()

    def quit_if_requested(self, command):
        if command == "q":
            self.goodbye()
            raise SystemExit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reel-ready Rich terminal number guessing game."
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip intro delays and shorten result-screen pauses.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    game = NumberGuessingGame(fast=args.fast)
    game.run()


if __name__ == "__main__":
    main()