# Dungeon Crawler

A 2D top-down dungeon crawler game built with Python and Pygame.

## Features

- Custom pixel art character and enemies
- 4 levels including an epic boss fight
- WASD/Arrow key movement
- Shooting mechanics with ricochet
- Health system with health pack pickups
- Enemy AI with pathfinding
- Boss with teleportation abilities
- Background music and sound effects

## Requirements

- Python 3.8+
- Pygame 2.5.0+

## Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## How to Play

```bash
python game.py
```

### Controls

- **WASD / Arrow Keys** - Move
- **SPACE** - Shoot
- **ESC** - Quit game
- **R** - Restart (after game over/win)

### Objective

Navigate through dungeon levels, defeat enemies, and reach the yellow exit. In the final level, defeat the boss to win!

## Building Executables

### Local Build

```bash
python build.py
```

The executable will be created in the `dist/` folder.

### GitHub Actions (Windows & macOS)

1. Push your code to GitHub
2. Go to Actions tab
3. Run the "Build Game" workflow
4. Download the artifacts (Windows .exe and macOS app)

## Distribution

After building, share the executable with friends:
- **Windows**: `dist/DungeonCrawler.exe`
- **macOS**: `dist/DungeonCrawler`

No Python installation required for your friends!
