"""
Combat resolution system
"""
import random
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Battle:
    """Represents an ongoing battle"""
    province_id: int
    attackers: List[str]  # Country codes
    defenders: List[str]  # Country codes
    duration: float = 0.0  # Hours of combat


class CombatSystem:
    """Manages combat resolution"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.active_battles = []  # List of Battle objects
        self.combat_update_interval = 1.0  # Update combat every game hour
        self.time_accumulator = 0.0

    def update(self, delta_time):
        """Update all active battles"""
        self.time_accumulator += delta_time

        if self.time_accumulator >= self.combat_update_interval:
            self.time_accumulator -= self.combat_update_interval

            # Check for new battles
            self.detect_battles()

            # Resolve active battles
            for battle in self.active_battles[:]:
                self.resolve_battle_tick(battle)
                battle.duration += self.combat_update_interval

    def detect_battles(self):
        """Detect provinces with hostile units (battles)"""
        # Check each province for units from different countries at war
        for province in self.game_state.province_manager.provinces.values():
            units = self.game_state.military_system.get_units_in_province(province.province_id)

            if len(units) < 2:
                continue

            # Group units by owner
            by_owner = {}
            for unit in units:
                if unit.owner not in by_owner:
                    by_owner[unit.owner] = []
                by_owner[unit.owner].append(unit)

            # Check if any are at war
            owners = list(by_owner.keys())
            for i, owner1 in enumerate(owners):
                for owner2 in owners[i+1:]:
                    country1 = self.game_state.country_manager.get_country(owner1)
                    country2 = self.game_state.country_manager.get_country(owner2)

                    if country1 and country2 and country1.is_at_war_with(owner2):
                        # Battle exists!
                        if not self._has_battle_in_province(province.province_id):
                            self.start_battle(province.province_id, owner1, owner2)

    def _has_battle_in_province(self, province_id: int) -> bool:
        """Check if battle already exists in province"""
        return any(b.province_id == province_id for b in self.active_battles)

    def start_battle(self, province_id: int, attacker: str, defender: str):
        """Start a new battle"""
        battle = Battle(
            province_id=province_id,
            attackers=[attacker],
            defenders=[defender]
        )
        self.active_battles.append(battle)

    def resolve_battle_tick(self, battle: Battle):
        """Resolve one tick of combat"""
        province = self.game_state.province_manager.get_province(battle.province_id)
        if not province:
            self.active_battles.remove(battle)
            return

        # Get all units in battle
        attacker_units = []
        defender_units = []

        for attacker in battle.attackers:
            attacker_units.extend(
                self.game_state.military_system.get_units_in_province_by_owner(
                    battle.province_id, attacker
                )
            )

        for defender in battle.defenders:
            defender_units.extend(
                self.game_state.military_system.get_units_in_province_by_owner(
                    battle.province_id, defender
                )
            )

        # Check if battle is over
        if not attacker_units or not defender_units:
            self.end_battle(battle, attacker_units, defender_units)
            return

        # Calculate combat values
        attack_power = self._calculate_combat_power(attacker_units, is_attacking=True)
        defense_power = self._calculate_combat_power(defender_units, is_attacking=False)

        # Apply terrain modifier
        terrain_modifier = self._get_terrain_modifier(province.terrain_type)
        defense_power *= terrain_modifier

        # Dice rolls for randomness
        attack_roll = attack_power * random.uniform(0.7, 1.3)
        defense_roll = defense_power * random.uniform(0.7, 1.3)

        # Apply damage
        if attack_roll > defense_roll:
            # Attackers winning
            damage_to_defender = (attack_roll - defense_roll) * 0.5
            self._apply_damage_to_units(defender_units, damage_to_defender)

            # Light damage to attacker
            damage_to_attacker = defense_roll * 0.2
            self._apply_damage_to_units(attacker_units, damage_to_attacker)
        else:
            # Defenders winning
            damage_to_attacker = (defense_roll - attack_roll) * 0.5
            self._apply_damage_to_units(attacker_units, damage_to_attacker)

            # Light damage to defender
            damage_to_defender = attack_roll * 0.2
            self._apply_damage_to_units(defender_units, damage_to_defender)

        # Check for retreats
        self._check_retreats(attacker_units, defender_units)

    def _calculate_combat_power(self, units: List, is_attacking: bool) -> float:
        """Calculate total combat power of units"""
        total = 0.0
        for unit in units:
            template = self.game_state.unit_template_manager.get_template(unit.template_id)
            if template:
                if is_attacking:
                    total += unit.get_effective_attack(template)
                else:
                    total += unit.get_effective_defense(template)
        return total

    def _get_terrain_modifier(self, terrain_type: str) -> float:
        """Get terrain combat modifier"""
        modifiers = {
            "plains": 1.0,
            "hills": 1.2,
            "mountains": 1.5,
            "forest": 1.3,
            "urban": 1.4,
            "marsh": 1.1
        }
        return modifiers.get(terrain_type, 1.0)

    def _apply_damage_to_units(self, units: List, total_damage: float):
        """Distribute damage among units"""
        if not units:
            return

        damage_per_unit = total_damage / len(units)

        for unit in units:
            template = self.game_state.unit_template_manager.get_template(unit.template_id)
            if template:
                unit.take_damage(damage_per_unit, template)

    def _check_retreats(self, attacker_units: List, defender_units: List):
        """Check if any units should retreat"""
        # Simple retreat: if organization too low, move to adjacent province
        # For now, just mark them for removal
        pass

    def end_battle(self, battle: Battle, remaining_attackers: List, remaining_defenders: List):
        """End a battle and determine winner"""
        province = self.game_state.province_manager.get_province(battle.province_id)
        if not province:
            self.active_battles.remove(battle)
            return

        # Determine winner
        if remaining_attackers and not remaining_defenders:
            # Attackers won
            winner = battle.attackers[0] if battle.attackers else None
            if winner and province.owner != winner:
                # Province captured!
                old_owner = province.owner
                province.owner = winner

                # Award war score
                if old_owner:
                    self._award_war_score(winner, old_owner, 5)  # 5 points for province capture

        elif remaining_defenders and not remaining_attackers:
            # Defenders won
            winner = battle.defenders[0] if battle.defenders else None
            if winner and old_owner := battle.attackers[0]:
                self._award_war_score(winner, old_owner, 2)  # 2 points for defense

        # Remove battle
        if battle in self.active_battles:
            self.active_battles.remove(battle)

    def _award_war_score(self, winner: str, loser: str, points: int):
        """Award war score to winner"""
        winner_country = self.game_state.country_manager.get_country(winner)
        if winner_country and loser in winner_country.war_scores:
            winner_country.war_scores[loser] += points

            # Cap at 100
            winner_country.war_scores[loser] = min(100, winner_country.war_scores[loser])

    def get_battle_in_province(self, province_id: int) -> Optional[Battle]:
        """Get battle happening in a province"""
        for battle in self.active_battles:
            if battle.province_id == province_id:
                return battle
        return None
