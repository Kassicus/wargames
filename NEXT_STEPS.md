# Next Steps - Development Guide

## Getting Started

Your grand strategy game foundation is complete! Here's how to continue development.

## Immediate Next Steps (Recommended Order)

### Step 1: Test the Game Visually
On a system with a display:
```bash
cd /home/kason/localdev/wargames
source venv/bin/activate
python main.py
```

You should see:
- A 3x3 grid of provinces (Germany, France, UK)
- Top bar with date, pause status, speed
- Clickable provinces showing info panel
- Working zoom, pan, and camera controls

### Step 2: Expand the Economy System

**File to edit**: `src/systems/economy.py` (create this)

```python
"""Economy system for automatic resource generation"""

class EconomySystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.update_interval = 24.0  # Update every 24 game hours (1 day)
        self.time_accumulator = 0.0

    def update(self, delta_time):
        """Update economy - collect income, etc."""
        self.time_accumulator += delta_time

        if self.time_accumulator >= self.update_interval:
            self.time_accumulator -= self.update_interval
            self.collect_income()

    def collect_income(self):
        """Collect income from all provinces"""
        for country in self.game_state.country_manager.get_all_countries():
            provinces = self.game_state.province_manager.get_provinces_by_owner(country.code)
            income = sum(p.get_income() for p in provinces)
            country.add_money(income)
            print(f"{country.name} collected ${income:.2f}")
```

Then integrate in `src/game.py`:
```python
from src.systems.economy import EconomySystem

class GameState:
    def __init__(self):
        # ... existing code ...
        self.economy_system = EconomySystem(self)

    def update(self, delta_time):
        if not self.is_paused:
            self.game_time += delta_time * self.game_speed
            self.economy_system.update(delta_time * self.game_speed)
```

### Step 3: Add Military Units

**File to create**: `src/unit.py`

```python
"""Military unit data structures"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class UnitTemplate:
    """Template defining a type of unit"""
    unit_type: str  # "infantry", "tank", "fighter", etc.
    category: str  # "land", "sea", "air"
    attack: int
    defense: int
    hp: int
    cost: float
    manpower_cost: int
    production_time: int  # In hours

@dataclass
class Unit:
    """Instance of a military unit"""
    template_id: str
    owner: str  # Country code
    location: int  # Province ID
    current_hp: int
    organization: int
    experience: int = 0
```

**File to create**: `src/systems/military.py`

```python
"""Military system for unit management"""

class MilitarySystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.units = []  # List of all units

    def create_unit(self, template_id, owner, location):
        """Create a new unit"""
        template = self.get_template(template_id)
        unit = Unit(
            template_id=template_id,
            owner=owner,
            location=location,
            current_hp=template.hp,
            organization=100
        )
        self.units.append(unit)
        return unit

    def get_units_in_province(self, province_id):
        """Get all units in a province"""
        return [u for u in self.units if u.location == province_id]

    def move_unit(self, unit, destination_province_id):
        """Move unit to new province"""
        # TODO: Add pathfinding
        unit.location = destination_province_id
```

### Step 4: Implement Combat

**File to create**: `src/systems/combat.py`

```python
"""Combat resolution system"""
import random

class CombatSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.active_battles = []

    def resolve_battle(self, province_id):
        """Resolve combat in a province"""
        units = self.game_state.military_system.get_units_in_province(province_id)

        # Group by owner
        by_owner = {}
        for unit in units:
            if unit.owner not in by_owner:
                by_owner[unit.owner] = []
            by_owner[unit.owner].append(unit)

        if len(by_owner) < 2:
            return  # No battle if only one side

        # Simple 2-sided battle
        owners = list(by_owner.keys())
        attacker_units = by_owner[owners[0]]
        defender_units = by_owner[owners[1]]

        # Calculate combat values
        attack_value = sum(self.get_unit_attack(u) for u in attacker_units)
        defense_value = sum(self.get_unit_defense(u) for u in defender_units)

        # Dice rolls
        attack_roll = attack_value * random.uniform(0.5, 1.5)
        defense_roll = defense_value * random.uniform(0.5, 1.5)

        # Apply damage
        if attack_roll > defense_roll:
            damage = (attack_roll - defense_roll) * 0.1
            # Damage defender
            for unit in defender_units:
                unit.current_hp -= damage
        else:
            damage = (defense_roll - attack_roll) * 0.05
            # Damage attacker
            for unit in attacker_units:
                unit.current_hp -= damage
```

### Step 5: Create a Larger Map

**To create a custom map:**

1. **Create province ID map** in an image editor (GIMP, Photoshop):
   - Create a new image (e.g., 1920x1080)
   - Draw each province with a unique RGB color
   - Save as PNG: `assets/maps/provinces_id.png`

2. **Create CSV with province definitions**:
   ```csv
   id,name,r,g,b,terrain,development,population,coastal
   1,NewYork,255,0,0,plains,5,10000,true
   2,Pennsylvania,254,0,0,hills,4,8000,false
   ...
   ```

3. **Update countries.json** with province ownership

4. **Optional**: Create a visual map overlay showing terrain/geography

### Step 6: Add AI System

**File to create**: `src/systems/ai.py`

```python
"""AI controller for computer-controlled countries"""

class AIController:
    def __init__(self, game_state):
        self.game_state = game_state
        self.update_interval = 168.0  # AI thinks once per week
        self.time_accumulator = 0.0

    def update(self, delta_time):
        self.time_accumulator += delta_time

        if self.time_accumulator >= self.update_interval:
            self.time_accumulator -= self.update_interval
            self.make_decisions()

    def make_decisions(self):
        """AI decision-making for all countries"""
        for country in self.game_state.country_manager.get_all_countries():
            if country.code != self.game_state.player_country:
                self.make_country_decisions(country)

    def make_country_decisions(self, country):
        """Make decisions for one country"""
        # Economic decisions
        if country.money > 1000:
            self.consider_recruiting(country)

        # Military decisions
        self.evaluate_threats(country)

    def consider_recruiting(self, country):
        """Consider recruiting new units"""
        if country.manpower > 5000:
            # Recruit infantry in capital
            capital = self.game_state.province_manager.get_province(country.capital_province_id)
            if capital:
                # TODO: Create unit
                print(f"{country.name} is recruiting troops")
```

## Recommended Development Path

**Week 1-2: Economy & Resources**
- [ ] Automatic income collection
- [ ] Resource display in UI
- [ ] Production queue system

**Week 2-3: Military Units**
- [ ] Unit templates and data
- [ ] Unit creation/recruitment
- [ ] Unit rendering on map
- [ ] Unit movement

**Week 3-4: Combat**
- [ ] Battle detection
- [ ] Combat resolution
- [ ] Province capture
- [ ] War score accumulation

**Week 4-5: Diplomacy & Peace**
- [ ] War declaration UI
- [ ] Peace treaty interface
- [ ] Territorial demands

**Week 5-6: AI**
- [ ] Basic AI decision-making
- [ ] AI recruitment
- [ ] AI combat
- [ ] AI diplomacy

**Week 6-8: Polish & Content**
- [ ] Larger map
- [ ] More countries
- [ ] Better graphics
- [ ] Sound effects
- [ ] Events and flavor text

## Tips for Success

### 1. Incremental Development
Don't try to build everything at once. Add one feature, test it, then move to the next.

### 2. Use the Test Script
Modify `test_game.py` to test new features without needing to run the full game.

### 3. Data-Driven Development
Put all balance values (unit stats, costs, combat modifiers) in JSON files. This makes tweaking much easier.

### 4. Version Control
Initialize git:
```bash
git init
git add .
git commit -m "Initial grand strategy game foundation"
```

### 5. Profile Performance
If things get slow:
```python
import cProfile
cProfile.run('game.update(1.0)')
```

### 6. Modding Support
Keep data separate from code. This makes your game moddable by default.

## Common Challenges & Solutions

### Challenge: Pathfinding is slow
**Solution**: Use A* with early termination, cache paths, update paths in background threads

### Challenge: Too many units lag the game
**Solution**:
- Only render units in viewport
- Use sprite batching
- Update distant units less frequently

### Challenge: AI is too predictable
**Solution**: Add randomness to utility scores, give AI different personalities

### Challenge: Combat feels random
**Solution**: Show combat modifiers, use more granular damage, add tactics

## Resources

### Python Arcade Documentation
- Docs: https://api.arcade.academy/
- Examples: https://api.arcade.academy/en/latest/examples/index.html
- Discord: https://discord.gg/ZjGDqMp

### Game Design References
- Hearts of Iron 4 modding wiki
- Age of History 2 community forums
- Paradox Interactive dev diaries

### Useful Libraries
- **pathfinding**: A* pathfinding for Python
- **noise**: Procedural map generation
- **networkx**: Graph algorithms for diplomacy/trade

## Questions?

If you encounter issues:
1. Check `test_game.py` - does it still pass?
2. Add debug print statements
3. Use Python debugger: `import pdb; pdb.set_trace()`
4. Profile performance bottlenecks

## Final Notes

You have a solid foundation. The architecture supports:
- ✓ Easy expansion with new systems
- ✓ Data-driven content creation
- ✓ Modding support
- ✓ Performance optimization
- ✓ Clean, maintainable code

**The hardest part is done - you have working infrastructure. Now comes the fun part: adding gameplay!**

Good luck with your grand strategy game! 🎮
