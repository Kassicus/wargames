"""
Country data structures and management
"""
from typing import Tuple, List
from dataclasses import dataclass, field


@dataclass
class Country:
    """Represents a playable country"""

    code: str  # 3-letter code (e.g., "USA", "GER")
    name: str
    color: Tuple[int, int, int]  # RGB color for map display
    capital_province_id: int

    # Resources
    money: float = 1000.0
    manpower: int = 10000
    military_factories: int = 10
    civilian_factories: int = 10

    # Diplomatic
    at_war_with: List[str] = field(default_factory=list)
    allied_with: List[str] = field(default_factory=list)

    # War score (tracks score in each war)
    war_scores: dict = field(default_factory=dict)  # enemy_code -> score

    def add_money(self, amount: float):
        """Add money to treasury"""
        self.money += amount

    def spend_money(self, amount: float) -> bool:
        """Try to spend money, returns True if successful"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def add_manpower(self, amount: int):
        """Add manpower"""
        self.manpower += amount

    def recruit_manpower(self, amount: int) -> bool:
        """Try to recruit manpower, returns True if successful"""
        if self.manpower >= amount:
            self.manpower -= amount
            return True
        return False

    def is_at_war_with(self, country_code: str) -> bool:
        """Check if at war with another country"""
        return country_code in self.at_war_with

    def declare_war(self, country_code: str):
        """Declare war on another country"""
        if country_code not in self.at_war_with:
            self.at_war_with.append(country_code)
            self.war_scores[country_code] = 0

    def make_peace(self, country_code: str):
        """Make peace with another country"""
        if country_code in self.at_war_with:
            self.at_war_with.remove(country_code)
            if country_code in self.war_scores:
                del self.war_scores[country_code]


class CountryManager:
    """Manages all countries in the game"""

    def __init__(self):
        self.countries = {}  # country_code -> Country

    def add_country(self, country: Country):
        """Add a country to the manager"""
        self.countries[country.code] = country

    def get_country(self, code: str) -> Country:
        """Get country by code"""
        return self.countries.get(code)

    def get_all_countries(self) -> List[Country]:
        """Get all countries"""
        return list(self.countries.values())
