"""
Military system for unit management, movement, and recruitment
"""
from typing import List, Optional
from src.unit import Unit, UnitTemplate


class MilitarySystem:
    """Manages all military units and operations"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.units = []  # List of all units
        self.next_unit_id = 1

    def update(self, delta_time):
        """Update military units"""
        # Move units
        for unit in self.units[:]:  # Copy list to allow removal
            if unit.is_moving and unit.move_target:
                self._move_unit(unit)

            # Remove destroyed units
            if unit.is_destroyed():
                self.units.remove(unit)

    def create_unit(self, template_id: str, owner: str, location: int) -> Optional[Unit]:
        """Create a new unit"""
        template = self.game_state.unit_template_manager.get_template(template_id)
        if not template:
            return None

        unit = Unit(
            unit_id=self.next_unit_id,
            template_id=template_id,
            owner=owner,
            location=location,
            current_hp=template.max_hp,
            organization=template.max_organization
        )

        self.units.append(unit)
        self.next_unit_id += 1
        return unit

    def recruit_unit(self, country_code: str, template_id: str, province_id: int) -> bool:
        """Recruit a new unit (costs money and manpower)"""
        template = self.game_state.unit_template_manager.get_template(template_id)
        if not template:
            return False

        # Check if can afford
        if not self.game_state.economy_system.can_afford_unit(
            country_code, template.cost, template.manpower_cost
        ):
            return False

        # Purchase unit
        if self.game_state.economy_system.purchase_unit(
            country_code, template.cost, template.manpower_cost
        ):
            # Create unit
            unit = self.create_unit(template_id, country_code, province_id)
            return unit is not None

        return False

    def get_units_in_province(self, province_id: int) -> List[Unit]:
        """Get all units in a province"""
        return [u for u in self.units if u.location == province_id]

    def get_units_by_owner(self, country_code: str) -> List[Unit]:
        """Get all units owned by a country"""
        return [u for u in self.units if u.owner == country_code]

    def get_units_in_province_by_owner(self, province_id: int, country_code: str) -> List[Unit]:
        """Get units in province owned by specific country"""
        return [u for u in self.units if u.location == province_id and u.owner == country_code]

    def order_move(self, unit: Unit, destination_province_id: int):
        """Order unit to move to destination"""
        # Simple movement - just set destination
        unit.is_moving = True
        unit.move_target = destination_province_id

    def _move_unit(self, unit: Unit):
        """Execute unit movement (simplified - instant for now)"""
        if unit.move_target:
            # TODO: Implement pathfinding and gradual movement
            # For now, instant movement
            unit.location = unit.move_target
            unit.is_moving = False
            unit.move_target = None

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        """Get unit by ID"""
        for unit in self.units:
            if unit.unit_id == unit_id:
                return unit
        return None

    def count_units_by_category(self, country_code: str, category: str) -> int:
        """Count units of a specific category for a country"""
        count = 0
        for unit in self.get_units_by_owner(country_code):
            template = self.game_state.unit_template_manager.get_template(unit.template_id)
            if template and template.category == category:
                count += 1
        return count
