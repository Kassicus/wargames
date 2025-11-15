# Grand Strategy Game

A 2D province-based real-time grand strategy game built with Python and Arcade, inspired by Hearts of Iron 4 and Age of History 2.

## Features

- Real-time gameplay with pause
- Province-based map system
- Separate land, sea, and air units
- Economy and production management
- War score and peace treaty system
- AI-controlled nations
- Multiple zoom levels

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Project Structure

- `data/` - Game data (JSON/CSV files)
- `assets/` - Images and sprites
- `src/` - Source code
  - `systems/` - Game systems (economy, combat, AI)
  - `ui/` - UI components
- `tests/` - Unit tests
