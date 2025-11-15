"""
Test script to validate game structure without requiring a display
"""
import sys
from pathlib import Path

# Test imports
try:
    from src.constants import *
    from src.province import Province, ProvinceManager
    from src.country import Country, CountryManager
    from src.game import GameState
    from src.data_loader import load_game_data, create_sample_provinces, create_sample_countries
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test data creation
try:
    create_sample_provinces()
    create_sample_countries()
    print("✓ Sample data files created")
except Exception as e:
    print(f"✗ Data creation error: {e}")
    sys.exit(1)

# Test game state
try:
    game_state = GameState()
    load_game_data(game_state)
    print(f"✓ Game state created")
    print(f"  - Loaded {len(game_state.province_manager.provinces)} provinces")
    print(f"  - Loaded {len(game_state.country_manager.countries)} countries")
except Exception as e:
    print(f"✗ Game state error: {e}")
    sys.exit(1)

# Test province operations
try:
    province = game_state.province_manager.get_province(1)
    if province:
        print(f"✓ Province operations work")
        print(f"  - Province 1: {province.name}")
        print(f"  - Owner: {province.owner}")
        print(f"  - Income: {province.get_income()}")
        print(f"  - Color: {province.color_rgb}")
except Exception as e:
    print(f"✗ Province error: {e}")
    sys.exit(1)

# Test country operations
try:
    countries = game_state.country_manager.get_all_countries()
    print(f"✓ Country operations work")
    for country in countries:
        provinces_owned = game_state.province_manager.get_provinces_by_owner(country.code)
        print(f"  - {country.name} ({country.code}): {len(provinces_owned)} provinces")
        print(f"    Money: ${country.money:.2f}, Manpower: {country.manpower}")
except Exception as e:
    print(f"✗ Country error: {e}")
    sys.exit(1)

# Test game mechanics
try:
    # Test pause/unpause
    game_state.toggle_pause()
    assert game_state.is_paused == True
    game_state.toggle_pause()
    assert game_state.is_paused == False

    # Test speed control
    game_state.set_speed(GAME_SPEED_FAST)
    assert game_state.game_speed == GAME_SPEED_FAST

    # Test update
    game_state.update(1.0)

    # Test province selection
    game_state.select_province(1)
    assert game_state.selected_province_id == 1

    # Test date
    date = game_state.get_current_date()
    assert "1936" in date

    print(f"✓ Game mechanics work")
    print(f"  - Current date: {date}")
    print(f"  - Game time: {game_state.game_time:.2f} hours")
except Exception as e:
    print(f"✗ Game mechanics error: {e}")
    sys.exit(1)

# Test diplomacy
try:
    ger = game_state.country_manager.get_country("GER")
    fra = game_state.country_manager.get_country("FRA")

    # Test war declaration
    ger.declare_war("FRA")
    assert ger.is_at_war_with("FRA")

    # Test peace
    ger.make_peace("FRA")
    assert not ger.is_at_war_with("FRA")

    print(f"✓ Diplomacy system works")
except Exception as e:
    print(f"✗ Diplomacy error: {e}")
    sys.exit(1)

# Test economy
try:
    total_income = 0
    for province in game_state.province_manager.provinces.values():
        if province.owner:
            total_income += province.get_income()

    print(f"✓ Economy system works")
    print(f"  - Total world income: ${total_income:.2f}/hour")
except Exception as e:
    print(f"✗ Economy error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("ALL TESTS PASSED!")
print("="*50)
print("\nThe game structure is working correctly.")
print("To run the actual game on a system with a display, use:")
print("  python main.py")
print("\nControls:")
print("  - SPACE: Pause/Unpause")
print("  - 1/2/3: Set game speed")
print("  - Arrow keys: Pan camera")
print("  - Mouse scroll: Zoom")
print("  - Right click + drag: Pan camera")
print("  - Left click: Select province")
