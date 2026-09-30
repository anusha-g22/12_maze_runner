# Maze Runner

Navigate through a procedurally generated maze to reach the exit using **Pygame**.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / UP | Move up |
| S / DOWN | Move down |
| A / LEFT | Move left |
| D / RIGHT | Move right |
| R | Generate new maze |
| H | Toggle shortest-path hint |
| 1 / 2 / 3 | Choose Easy / Medium / Hard at the difficulty menu |

## Features

- **Shortest Path Hint:** Press H to toggle the shortest path from the player's current cell to the exit.
- **Fog of War:** Maze cells within 3 cells of the player are visible; the visible area follows the player.
- **Timer Leaderboard:** Successful completion times are saved in `leaderboard.json`; the best 5 are shown after a win.
- **Difficulty Tiers:** At launch, press 1 for Easy (10x8), 2 for Medium (15x13), or 3 for Hard (20x18). Press R to generate another maze at the selected difficulty.

## Folder Structure

```
maze-runner/
├── main.py
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   ├── maze.py
│   └── player.py
└── README.md
```

## Submission Checklist

- [x] All 4 tasks completed
- [x] Maze is generated fresh each session (R key)
- [x] Fog of war renders correctly
- [x] Timer leaderboard persists to JSON
- [x] Code reviewed with LLM
