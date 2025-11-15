"""
Data loading utilities for provinces, countries, and game data
"""
import json
import csv
from pathlib import Path
from src.province import Province
from src.country import Country


def load_game_data(game_state):
    """Load all game data"""
    # Load provinces
    load_provinces(game_state.province_manager)

    # Load countries
    load_countries(game_state.country_manager)

    # Assign province ownership based on country definitions
    assign_province_ownership(game_state)


def load_provinces(province_manager):
    """Load provinces from CSV file"""
    csv_path = Path("data/provinces.csv")

    if not csv_path.exists():
        print(f"Warning: {csv_path} not found, creating sample data...")
        create_sample_provinces()

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            province = Province(
                province_id=int(row['id']),
                name=row['name'],
                color_rgb=(int(row['r']), int(row['g']), int(row['b'])),
                terrain_type=row.get('terrain', 'plains'),
                development=int(row.get('development', 1)),
                population=int(row.get('population', 1000)),
                is_coastal=row.get('coastal', '').lower() == 'true'
            )
            province_manager.add_province(province)


def load_countries(country_manager):
    """Load countries from JSON file"""
    json_path = Path("data/countries.json")

    if not json_path.exists():
        print(f"Warning: {json_path} not found, creating sample data...")
        create_sample_countries()

    with open(json_path, 'r') as f:
        data = json.load(f)
        for code, country_data in data.items():
            country = Country(
                code=code,
                name=country_data['name'],
                color=tuple(country_data['color']),
                capital_province_id=country_data['capital'],
                money=country_data.get('money', 1000.0),
                manpower=country_data.get('manpower', 10000),
                military_factories=country_data.get('military_factories', 10),
                civilian_factories=country_data.get('civilian_factories', 10)
            )
            country.provinces = country_data.get('provinces', [])
            country_manager.add_country(country)


def assign_province_ownership(game_state):
    """Assign provinces to countries based on country definitions"""
    for country in game_state.country_manager.get_all_countries():
        if hasattr(country, 'provinces'):
            for province_id in country.provinces:
                province = game_state.province_manager.get_province(province_id)
                if province:
                    province.owner = country.code
                    # Mark capital
                    if province_id == country.capital_province_id:
                        province.is_capital = True


def create_sample_provinces():
    """Create sample province data for testing"""
    Path("data").mkdir(exist_ok=True)

    # Sample provinces in a grid
    provinces = [
        {'id': 1, 'name': 'Berlin', 'r': 255, 'g': 0, 'b': 0, 'terrain': 'plains', 'development': 5, 'population': 5000, 'coastal': 'false'},
        {'id': 2, 'name': 'Munich', 'r': 254, 'g': 0, 'b': 0, 'terrain': 'hills', 'development': 4, 'population': 4000, 'coastal': 'false'},
        {'id': 3, 'name': 'Hamburg', 'r': 253, 'g': 0, 'b': 0, 'terrain': 'plains', 'development': 3, 'population': 3000, 'coastal': 'true'},
        {'id': 4, 'name': 'Paris', 'r': 0, 'g': 255, 'b': 0, 'terrain': 'plains', 'development': 5, 'population': 5000, 'coastal': 'false'},
        {'id': 5, 'name': 'Lyon', 'r': 0, 'g': 254, 'b': 0, 'terrain': 'hills', 'development': 3, 'population': 3000, 'coastal': 'false'},
        {'id': 6, 'name': 'Marseille', 'r': 0, 'g': 253, 'b': 0, 'terrain': 'plains', 'development': 3, 'population': 3000, 'coastal': 'true'},
        {'id': 7, 'name': 'London', 'r': 0, 'g': 0, 'b': 255, 'terrain': 'plains', 'development': 5, 'population': 5000, 'coastal': 'false'},
        {'id': 8, 'name': 'Manchester', 'r': 0, 'g': 0, 'b': 254, 'terrain': 'plains', 'development': 4, 'population': 4000, 'coastal': 'false'},
        {'id': 9, 'name': 'Liverpool', 'r': 0, 'g': 0, 'b': 253, 'terrain': 'plains', 'development': 3, 'population': 3000, 'coastal': 'true'},
    ]

    with open('data/provinces.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'r', 'g', 'b', 'terrain', 'development', 'population', 'coastal'])
        writer.writeheader()
        writer.writerows(provinces)

    print("Created sample provinces at data/provinces.csv")


def create_sample_countries():
    """Create sample country data for testing"""
    Path("data").mkdir(exist_ok=True)

    countries = {
        "GER": {
            "name": "Germany",
            "color": [128, 128, 128],
            "capital": 1,
            "provinces": [1, 2, 3],
            "money": 2000.0,
            "manpower": 20000,
            "military_factories": 15,
            "civilian_factories": 20
        },
        "FRA": {
            "name": "France",
            "color": [0, 0, 200],
            "capital": 4,
            "provinces": [4, 5, 6],
            "money": 1800.0,
            "manpower": 18000,
            "military_factories": 12,
            "civilian_factories": 18
        },
        "GBR": {
            "name": "United Kingdom",
            "color": [200, 0, 0],
            "capital": 7,
            "provinces": [7, 8, 9],
            "money": 2500.0,
            "manpower": 15000,
            "military_factories": 18,
            "civilian_factories": 25
        }
    }

    with open('data/countries.json', 'w') as f:
        json.dump(countries, f, indent=2)

    print("Created sample countries at data/countries.json")
