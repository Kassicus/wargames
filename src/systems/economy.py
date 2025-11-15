"""
Economy system for automatic resource generation and management
"""


class EconomySystem:
    """Manages economic updates for all countries"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.update_interval = 24.0  # Update every 24 game hours (1 day)
        self.time_accumulator = 0.0

    def update(self, delta_time):
        """Update economy - collect income, etc."""
        self.time_accumulator += delta_time

        if self.time_accumulator >= self.update_interval:
            self.time_accumulator -= self.update_interval
            self.collect_daily_income()
            self.collect_manpower()

    def collect_daily_income(self):
        """Collect daily income from all provinces"""
        for country in self.game_state.country_manager.get_all_countries():
            provinces = self.game_state.province_manager.get_provinces_by_owner(country.code)
            daily_income = sum(p.get_income() for p in provinces)
            country.add_money(daily_income)

    def collect_manpower(self):
        """Collect manpower from provinces"""
        for country in self.game_state.country_manager.get_all_countries():
            provinces = self.game_state.province_manager.get_provinces_by_owner(country.code)
            manpower_gain = sum(p.population // 100 for p in provinces)  # 1% of population per day
            country.add_manpower(manpower_gain)

    def can_afford_unit(self, country_code, unit_cost, manpower_cost):
        """Check if country can afford to build a unit"""
        country = self.game_state.country_manager.get_country(country_code)
        if not country:
            return False
        return country.money >= unit_cost and country.manpower >= manpower_cost

    def purchase_unit(self, country_code, unit_cost, manpower_cost):
        """Purchase a unit (deduct resources)"""
        country = self.game_state.country_manager.get_country(country_code)
        if not country:
            return False

        if country.spend_money(unit_cost) and country.recruit_manpower(manpower_cost):
            return True

        return False
