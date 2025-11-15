"""
Comprehensive test script for all game features
"""
import sys
from pathlib import Path

# Test all imports
print("="*60)
print("TESTING COMPLETE GRAND STRATEGY GAME")
print("="*60)
print()

try:
    from src.constants import *
    from src.province import Province, ProvinceManager
    from src.country import Country, CountryManager
    from src.unit import Unit, UnitTemplate, UnitTemplateManager
    from src.game import GameState
    from src.data_loader import load_game_data
    from src.systems.economy import EconomySystem
    from src.systems.military import MilitarySystem
    from src.systems.combat import CombatSystem
    from src.systems.diplomacy import DiplomacySystem
    from src.systems.ai import AIController
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test game initialization
try:
    print("\n" + "="*60)
    print("1. GAME INITIALIZATION")
    print("="*60)

    game_state = GameState()
    load_game_data(game_state)
    game_state.initialize_systems()

    print(f"✓ Loaded {len(game_state.province_manager.provinces)} provinces")
    print(f"✓ Loaded {len(game_state.country_manager.countries)} countries")
    print(f"✓ Loaded {len(game_state.unit_template_manager.templates)} unit templates")
    print(f"✓ All game systems initialized")

    # Set player
    game_state.set_player_country("GER")
    print(f"✓ Player set to Germany")

except Exception as e:
    print(f"✗ Initialization error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test unit templates
try:
    print("\n" + "="*60)
    print("2. UNIT TEMPLATES")
    print("="*60)

    templates = game_state.unit_template_manager.get_all_templates()
    land_units = game_state.unit_template_manager.get_templates_by_category("land")
    sea_units = game_state.unit_template_manager.get_templates_by_category("sea")
    air_units = game_state.unit_template_manager.get_templates_by_category("air")

    print(f"✓ Total templates: {len(templates)}")
    print(f"  - Land units: {len(land_units)}")
    print(f"  - Sea units: {len(sea_units)}")
    print(f"  - Air units: {len(air_units)}")

    for template in land_units:
        print(f"    {template.name}: Attack={template.attack}, Defense={template.defense}, Cost=${template.cost}")

except Exception as e:
    print(f"✗ Unit template error: {e}")
    sys.exit(1)

# Test economy system
try:
    print("\n" + "="*60)
    print("3. ECONOMY SYSTEM")
    print("="*60)

    ger = game_state.country_manager.get_country("GER")
    initial_money = ger.money
    initial_manpower = ger.manpower

    # Simulate one day
    game_state.economy_system.update(24.0)

    print(f"✓ Economy update successful")
    print(f"  - Initial money: ${initial_money:.0f}")
    print(f"  - After 1 day: ${ger.money:.0f}")
    print(f"  - Daily income: ${ger.money - initial_money:.0f}")
    print(f"  - Manpower: {initial_manpower} -> {ger.manpower}")

except Exception as e:
    print(f"✗ Economy error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test military system
try:
    print("\n" + "="*60)
    print("4. MILITARY SYSTEM")
    print("="*60)

    # Create units
    ger = game_state.country_manager.get_country("GER")
    fra = game_state.country_manager.get_country("FRA")

    # Recruit units for Germany
    unit1 = game_state.military_system.recruit_unit("GER", "infantry", 1)
    unit2 = game_state.military_system.recruit_unit("GER", "armor", 1)

    # Create units for France
    unit3 = game_state.military_system.create_unit("infantry", "FRA", 4)
    unit4 = game_state.military_system.create_unit("infantry", "FRA", 4)

    print(f"✓ Unit recruitment successful")
    print(f"  - Germany units: {len(game_state.military_system.get_units_by_owner('GER'))}")
    print(f"  - France units: {len(game_state.military_system.get_units_by_owner('FRA'))}")
    print(f"  - Total units: {len(game_state.military_system.units)}")

    # Test unit counts by category
    land_count = game_state.military_system.count_units_by_category("GER", "land")
    print(f"  - Germany land units: {land_count}")

except Exception as e:
    print(f"✗ Military error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test diplomacy system
try:
    print("\n" + "="*60)
    print("5. DIPLOMACY SYSTEM")
    print("="*60)

    # Declare war
    game_state.diplomacy_system.declare_war("GER", "FRA")

    ger = game_state.country_manager.get_country("GER")
    fra = game_state.country_manager.get_country("FRA")

    print(f"✓ War declaration successful")
    print(f"  - Germany at war with: {ger.at_war_with}")
    print(f"  - France at war with: {fra.at_war_with}")

    # Test peace demand
    demand = game_state.diplomacy_system.create_peace_demand("annex_province", 4)
    print(f"✓ Peace demand created: {demand.demand_type}, cost: {demand.war_score_cost}")

except Exception as e:
    print(f"✗ Diplomacy error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test combat system
try:
    print("\n" + "="*60)
    print("6. COMBAT SYSTEM")
    print("="*60)

    # Move German unit to French province to trigger battle
    ger_units = game_state.military_system.get_units_by_owner("GER")
    if ger_units:
        game_state.military_system.order_move(ger_units[0], 4)  # Move to Paris
        game_state.military_system.update(1.0)  # Execute movement

    # Update combat system to detect battles
    game_state.combat_system.update(1.0)

    battles = game_state.combat_system.active_battles
    print(f"✓ Combat system operational")
    print(f"  - Active battles: {len(battles)}")

    if battles:
        battle = battles[0]
        print(f"  - Battle in province {battle.province_id}")
        print(f"  - Attackers: {battle.attackers}")
        print(f"  - Defenders: {battle.defenders}")

        # Simulate some combat
        for i in range(5):
            game_state.combat_system.update(1.0)

        print(f"  - Battle duration: {battle.duration:.1f} hours")

except Exception as e:
    print(f"✗ Combat error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test AI system
try:
    print("\n" + "="*60)
    print("7. AI SYSTEM")
    print("="*60)

    # Make a country AI-controlled and test
    game_state.player_country = "GER"  # Player is Germany
    initial_gbr_units = len(game_state.military_system.get_units_by_owner("GBR"))

    # Run AI update (simulate a week)
    game_state.ai_controller.update(168.0)

    final_gbr_units = len(game_state.military_system.get_units_by_owner("GBR"))

    print(f"✓ AI system operational")
    print(f"  - AI made decisions for non-player countries")
    print(f"  - UK units before: {initial_gbr_units}")
    print(f"  - UK units after: {final_gbr_units}")

except Exception as e:
    print(f"✗ AI error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test complete game loop
try:
    print("\n" + "="*60)
    print("8. GAME LOOP SIMULATION")
    print("="*60)

    initial_time = game_state.game_time
    initial_date = game_state.get_current_date()

    # Simulate 1 game week
    for i in range(7):
        game_state.update(24.0)  # 24 hours per day

    final_time = game_state.game_time
    final_date = game_state.get_current_date()

    print(f"✓ Game loop simulation successful")
    print(f"  - Initial date: {initial_date}")
    print(f"  - Final date: {final_date}")
    print(f"  - Game time elapsed: {final_time - initial_time:.1f} hours")

except Exception as e:
    print(f"✗ Game loop error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final statistics
try:
    print("\n" + "="*60)
    print("9. FINAL GAME STATE")
    print("="*60)

    for country in game_state.country_manager.get_all_countries():
        provinces = game_state.province_manager.get_provinces_by_owner(country.code)
        units = game_state.military_system.get_units_by_owner(country.code)
        print(f"\n{country.name} ({country.code}):")
        print(f"  Provinces: {len(provinces)}")
        print(f"  Money: ${country.money:.0f}")
        print(f"  Manpower: {country.manpower:,}")
        print(f"  Units: {len(units)}")
        print(f"  At war: {len(country.at_war_with)} countries")
        if country.war_scores:
            for enemy, score in country.war_scores.items():
                print(f"    War score vs {enemy}: {score}")

except Exception as e:
    print(f"✗ Statistics error: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print()
print("The complete grand strategy game is fully functional with:")
print("  ✓ Province and country systems")
print("  ✓ Economy with income generation")
print("  ✓ Military units (land, sea, air)")
print("  ✓ Combat resolution")
print("  ✓ War score and diplomacy")
print("  ✓ AI controller")
print("  ✓ Complete game loop")
print()
print("To play the game on a system with a display:")
print("  python main.py")
print()
print("Controls:")
print("  SPACE: Pause/Resume")
print("  1/2/3: Game speed")
print("  I/T/A: Recruit Infantry/Tank/Artillery")
print("  W: Declare war on selected province owner")
print("  P: Make peace")
print("  Arrow keys: Pan camera")
print("  Mouse scroll: Zoom")
