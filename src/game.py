"""
Main game state and logic
"""
import arcade
from typing import Optional
from src.province import ProvinceManager
from src.country import CountryManager
from src.unit import UnitTemplateManager
from src.systems.economy import EconomySystem
from src.systems.military import MilitarySystem
from src.systems.combat import CombatSystem
from src.systems.diplomacy import DiplomacySystem
from src.systems.ai import AIController
from src.constants import *


class GameState:
    """Manages the overall game state"""

    def __init__(self):
        self.province_manager = ProvinceManager()
        self.country_manager = CountryManager()
        self.unit_template_manager = UnitTemplateManager()

        # Game systems (initialized after data is loaded)
        self.economy_system = None
        self.military_system = None
        self.combat_system = None
        self.diplomacy_system = None
        self.ai_controller = None

        # Game time
        self.game_time = 0.0  # Time in game hours
        self.game_speed = GAME_SPEED_NORMAL
        self.is_paused = False

        # Player control
        self.player_country = None  # Country code player is controlling

        # Selected province
        self.selected_province_id: Optional[int] = None

        # Selected unit
        self.selected_unit_id: Optional[int] = None

        # Date tracking (starting January 1, 1936)
        self.start_year = 1936
        self.start_month = 1
        self.start_day = 1

    def initialize_systems(self):
        """Initialize game systems after data is loaded"""
        self.economy_system = EconomySystem(self)
        self.military_system = MilitarySystem(self)
        self.combat_system = CombatSystem(self)
        self.diplomacy_system = DiplomacySystem(self)
        self.ai_controller = AIController(self)

    def update(self, delta_time: float):
        """Update game state"""
        if not self.is_paused:
            # Update game time
            self.game_time += delta_time * self.game_speed

            # Update game systems
            scaled_delta = delta_time * self.game_speed

            if self.economy_system:
                self.economy_system.update(scaled_delta)

            if self.military_system:
                self.military_system.update(scaled_delta)

            if self.combat_system:
                self.combat_system.update(scaled_delta)

            if self.ai_controller:
                self.ai_controller.update(scaled_delta)

            # Check for auto-peace at 100% war score
            if self.diplomacy_system:
                self.diplomacy_system.auto_peace_at_100()

    def toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = not self.is_paused

    def set_speed(self, speed: float):
        """Set game speed"""
        self.game_speed = speed

    def set_player_country(self, country_code: str):
        """Set which country the player controls"""
        if self.country_manager.get_country(country_code):
            self.player_country = country_code

    def get_current_date(self) -> str:
        """Get current game date as string"""
        # Calculate date based on game time (1 hour per update)
        total_hours = int(self.game_time)
        total_days = total_hours // 24

        # Simple date calculation
        year = self.start_year
        month = self.start_month
        day = self.start_day + total_days

        # Handle month/year rollover (simplified)
        days_in_month = 30  # Simplified for now
        while day > days_in_month:
            day -= days_in_month
            month += 1
            if month > 12:
                month = 1
                year += 1

        month_names = ["", "January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]

        return f"{month_names[month]} {day}, {year}"

    def select_province(self, province_id: Optional[int]):
        """Select a province"""
        self.selected_province_id = province_id

    def get_selected_province(self):
        """Get the currently selected province"""
        if self.selected_province_id is not None:
            return self.province_manager.get_province(self.selected_province_id)
        return None
