"""
Diplomacy and peace treaty system
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PeaceDemand:
    """A demand in a peace treaty"""
    demand_type: str  # "annex_province", "war_reparations", "release_nation", etc.
    target_data: any  # Province ID, amount, etc.
    war_score_cost: int


@dataclass
class PeaceTreaty:
    """A proposed peace treaty"""
    from_country: str
    to_country: str
    demands: List[PeaceDemand]
    total_war_score_cost: int


class DiplomacySystem:
    """Manages diplomacy, wars, and peace treaties"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.pending_peace_treaties = []  # List of PeaceTreaty objects

    def declare_war(self, attacker: str, defender: str) -> bool:
        """Declare war between two countries"""
        attacker_country = self.game_state.country_manager.get_country(attacker)
        defender_country = self.game_state.country_manager.get_country(defender)

        if not attacker_country or not defender_country:
            return False

        # Declare war both ways
        attacker_country.declare_war(defender)
        defender_country.declare_war(attacker)

        return True

    def make_peace(self, country1: str, country2: str):
        """Make peace between two countries"""
        country1_obj = self.game_state.country_manager.get_country(country1)
        country2_obj = self.game_state.country_manager.get_country(country2)

        if country1_obj and country2_obj:
            country1_obj.make_peace(country2)
            country2_obj.make_peace(country1)

    def create_peace_demand(self, demand_type: str, target_data: any) -> PeaceDemand:
        """Create a peace demand with appropriate war score cost"""
        war_score_cost = self._calculate_demand_cost(demand_type, target_data)

        return PeaceDemand(
            demand_type=demand_type,
            target_data=target_data,
            war_score_cost=war_score_cost
        )

    def _calculate_demand_cost(self, demand_type: str, target_data: any) -> int:
        """Calculate war score cost for a demand"""
        if demand_type == "annex_province":
            # Cost based on province value
            province = self.game_state.province_manager.get_province(target_data)
            if province:
                return 5 + province.development * 2  # 5-15 points typically
            return 10

        elif demand_type == "war_reparations":
            # Cost based on amount (target_data is money amount)
            return max(5, int(target_data / 500))  # 5 points per 500 money

        elif demand_type == "release_nation":
            return 30  # High cost

        elif demand_type == "military_access":
            return 5

        return 10  # Default

    def propose_peace_treaty(self, from_country: str, to_country: str,
                           demands: List[PeaceDemand]) -> Optional[PeaceTreaty]:
        """Propose a peace treaty"""
        total_cost = sum(d.war_score_cost for d in demands)

        treaty = PeaceTreaty(
            from_country=from_country,
            to_country=to_country,
            demands=demands,
            total_war_score_cost=total_cost
        )

        # Check if proposer has enough war score
        proposer = self.game_state.country_manager.get_country(from_country)
        if proposer and to_country in proposer.war_scores:
            if proposer.war_scores[to_country] >= total_cost:
                self.pending_peace_treaties.append(treaty)
                return treaty

        return None

    def accept_peace_treaty(self, treaty: PeaceTreaty) -> bool:
        """Accept and execute a peace treaty"""
        if treaty not in self.pending_peace_treaties:
            return False

        # Execute demands
        for demand in treaty.demands:
            self._execute_demand(treaty.from_country, treaty.to_country, demand)

        # Make peace
        self.make_peace(treaty.from_country, treaty.to_country)

        # Remove treaty
        self.pending_peace_treaties.remove(treaty)

        return True

    def _execute_demand(self, winner: str, loser: str, demand: PeaceDemand):
        """Execute a peace demand"""
        if demand.demand_type == "annex_province":
            province = self.game_state.province_manager.get_province(demand.target_data)
            if province and province.owner == loser:
                province.owner = winner

        elif demand.demand_type == "war_reparations":
            loser_country = self.game_state.country_manager.get_country(loser)
            winner_country = self.game_state.country_manager.get_country(winner)

            if loser_country and winner_country:
                amount = min(demand.target_data, loser_country.money)
                loser_country.spend_money(amount)
                winner_country.add_money(amount)

    def ai_should_accept_peace(self, country_code: str, treaty: PeaceTreaty) -> bool:
        """AI decision: should country accept this peace treaty?"""
        if treaty.to_country != country_code:
            return False

        country = self.game_state.country_manager.get_country(country_code)
        if not country:
            return False

        # Check war score - if losing badly, accept
        if treaty.from_country in country.war_scores:
            their_score = country.war_scores[treaty.from_country]
            if their_score < -50:  # We're losing badly
                return True

        # Check demands severity
        provinces_lost = sum(1 for d in treaty.demands if d.demand_type == "annex_province")
        total_provinces = len(self.game_state.province_manager.get_provinces_by_owner(country_code))

        # Don't accept if losing more than 50% of provinces
        if total_provinces > 0 and provinces_lost / total_provinces > 0.5:
            return False

        # Check money
        reparations = sum(d.target_data for d in treaty.demands
                         if d.demand_type == "war_reparations")
        if reparations > country.money * 0.8:
            return False

        # If war score is very negative, probably accept
        enemy_country = self.game_state.country_manager.get_country(treaty.from_country)
        if enemy_country and country_code in enemy_country.war_scores:
            if enemy_country.war_scores[country_code] > 75:
                return True

        return False

    def auto_peace_at_100(self):
        """Automatically create peace treaties when war score reaches 100"""
        for country in self.game_state.country_manager.get_all_countries():
            for enemy_code, war_score in list(country.war_scores.items()):
                if war_score >= 100:
                    # Force peace - take all provinces
                    enemy = self.game_state.country_manager.get_country(enemy_code)
                    if enemy:
                        enemy_provinces = self.game_state.province_manager.get_provinces_by_owner(enemy_code)

                        demands = []
                        for province in enemy_provinces[:]:  # Take up to all provinces
                            demands.append(self.create_peace_demand(
                                "annex_province", province.province_id
                            ))

                        # Create and auto-accept treaty
                        treaty = PeaceTreaty(
                            from_country=country.code,
                            to_country=enemy_code,
                            demands=demands,
                            total_war_score_cost=100
                        )

                        self._execute_demands_list(country.code, enemy_code, demands)
                        self.make_peace(country.code, enemy_code)

    def _execute_demands_list(self, winner: str, loser: str, demands: List[PeaceDemand]):
        """Execute a list of demands"""
        for demand in demands:
            self._execute_demand(winner, loser, demand)
