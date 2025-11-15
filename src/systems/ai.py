"""
AI controller for computer-controlled countries
"""
import random


class AIController:
    """AI decision-making for computer-controlled countries"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.update_interval = 168.0  # AI thinks once per week (168 hours)
        self.time_accumulator = 0.0

    def update(self, delta_time):
        """Update AI for all countries"""
        self.time_accumulator += delta_time

        if self.time_accumulator >= self.update_interval:
            self.time_accumulator -= self.update_interval
            self.make_all_decisions()

    def make_all_decisions(self):
        """Make decisions for all AI-controlled countries"""
        for country in self.game_state.country_manager.get_all_countries():
            # Skip player country
            if country.code == self.game_state.player_country:
                continue

            self.make_country_decisions(country)

    def make_country_decisions(self, country):
        """Make decisions for one country"""
        # Economic decisions
        self.make_economic_decisions(country)

        # Military decisions
        self.make_military_decisions(country)

        # Diplomatic decisions
        self.make_diplomatic_decisions(country)

    def make_economic_decisions(self, country):
        """Make economic decisions (production, building)"""
        # Recruit units if we have money and manpower
        if country.money > 500 and country.manpower > 5000:
            self.consider_recruiting_units(country)

    def consider_recruiting_units(self, country):
        """Consider recruiting new military units"""
        # Count existing units
        land_units = self.game_state.military_system.count_units_by_category(
            country.code, "land"
        )

        # Recruit if we have few units
        if land_units < 5:
            # Recruit infantry in capital
            capital = self.game_state.province_manager.get_province(
                country.capital_province_id
            )
            if capital and capital.owner == country.code:
                # Try to recruit infantry
                self.game_state.military_system.recruit_unit(
                    country.code, "infantry", capital.province_id
                )

    def make_military_decisions(self, country):
        """Make military decisions (movement, attacks)"""
        # Check if at war
        if country.at_war_with:
            self.conduct_war(country)
        else:
            # Consider expansion
            self.consider_expansion(country)

    def conduct_war(self, country):
        """Conduct ongoing wars"""
        for enemy_code in country.at_war_with:
            # Get our units
            our_units = self.game_state.military_system.get_units_by_owner(country.code)

            # Find enemy provinces
            enemy_provinces = self.game_state.province_manager.get_provinces_by_owner(enemy_code)

            if our_units and enemy_provinces:
                # Move units to attack
                for unit in our_units:
                    if not unit.is_moving:
                        # Find nearest enemy province
                        target = random.choice(enemy_provinces)
                        self.game_state.military_system.order_move(
                            unit, target.province_id
                        )

    def consider_expansion(self, country):
        """Consider declaring war for expansion"""
        # Don't be too aggressive - only expand sometimes
        if random.random() > 0.1:  # 10% chance per AI update
            return

        # Find neighbors
        our_provinces = self.game_state.province_manager.get_provinces_by_owner(country.code)
        if not our_provinces:
            return

        # Find potential targets
        for other_country in self.game_state.country_manager.get_all_countries():
            if other_country.code == country.code:
                continue

            if other_country.code == self.game_state.player_country:
                # Less likely to attack player
                if random.random() > 0.05:
                    continue

            # Check relative strength
            our_strength = self._calculate_military_strength(country.code)
            their_strength = self._calculate_military_strength(other_country.code)

            # Only attack if stronger
            if our_strength > their_strength * 1.5:
                # Declare war
                self.game_state.diplomacy_system.declare_war(
                    country.code, other_country.code
                )
                break  # One war at a time

    def make_diplomatic_decisions(self, country):
        """Make diplomatic decisions (peace, alliances)"""
        # Check if should make peace
        for enemy_code in list(country.at_war_with):
            self.consider_peace(country, enemy_code)

        # Check pending peace treaties
        for treaty in list(self.game_state.diplomacy_system.pending_peace_treaties):
            if treaty.to_country == country.code:
                # AI decides whether to accept
                if self.game_state.diplomacy_system.ai_should_accept_peace(
                    country.code, treaty
                ):
                    self.game_state.diplomacy_system.accept_peace_treaty(treaty)

    def consider_peace(self, country, enemy_code):
        """Consider making peace with an enemy"""
        enemy = self.game_state.country_manager.get_country(enemy_code)
        if not enemy:
            return

        # Check war score
        if enemy_code not in country.war_scores:
            return

        war_score = country.war_scores[enemy_code]

        # If winning big, demand peace
        if war_score >= 50:
            # Create peace demands
            demands = []

            # Take some provinces
            enemy_provinces = self.game_state.province_manager.get_provinces_by_owner(enemy_code)
            provinces_to_take = min(3, len(enemy_provinces), int(war_score / 20))

            for province in enemy_provinces[:provinces_to_take]:
                demand = self.game_state.diplomacy_system.create_peace_demand(
                    "annex_province", province.province_id
                )
                demands.append(demand)

            # Propose peace
            if demands:
                treaty = self.game_state.diplomacy_system.propose_peace_treaty(
                    country.code, enemy_code, demands
                )

                # AI might auto-accept if war score high enough
                if treaty and war_score >= 75:
                    if self.game_state.diplomacy_system.ai_should_accept_peace(
                        enemy_code, treaty
                    ):
                        self.game_state.diplomacy_system.accept_peace_treaty(treaty)

        # If losing badly, try to make peace
        elif war_score <= -50:
            # Willing to give up provinces
            our_provinces = self.game_state.province_manager.get_provinces_by_owner(country.code)

            # Offer some provinces
            if len(our_provinces) > 1:  # Keep at least capital
                demands = []
                provinces_to_give = min(2, len(our_provinces) - 1)

                for province in our_provinces[:provinces_to_give]:
                    if not province.is_capital:
                        demand = self.game_state.diplomacy_system.create_peace_demand(
                            "annex_province", province.province_id
                        )
                        demands.append(demand)

                # This would need to be from enemy's perspective
                # For now, just sue for peace
                # TODO: Implement peace offers from losing side

    def _calculate_military_strength(self, country_code: str) -> float:
        """Calculate approximate military strength of a country"""
        units = self.game_state.military_system.get_units_by_owner(country_code)
        strength = 0.0

        for unit in units:
            template = self.game_state.unit_template_manager.get_template(unit.template_id)
            if template:
                strength += (template.attack + template.defense) * unit.strength

        return strength

    def _get_ai_personality(self, country_code: str) -> str:
        """Get AI personality for a country (for future expansion)"""
        # Could be loaded from country definitions
        # For now, random
        personalities = ["aggressive", "defensive", "balanced", "economic"]
        return random.choice(personalities)
