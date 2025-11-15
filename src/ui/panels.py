"""
UI panel drawing functions
"""
import arcade
from src.constants import *


def draw_top_bar(game_state, screen_width, screen_height):
    """Draw the top status bar"""
    # Background
    arcade.draw_rectangle_filled(
        screen_width // 2, screen_height - 20,
        screen_width, 40,
        COLOR_UI_BACKGROUND
    )

    # Date
    date_text = game_state.get_current_date()
    arcade.draw_text(date_text, 10, screen_height - 30, COLOR_UI_TEXT, 14, font_name="Arial")

    # Pause indicator
    if game_state.is_paused:
        arcade.draw_text("PAUSED", screen_width // 2 - 50, screen_height - 30,
                        (255, 100, 100), 16, bold=True, font_name="Arial")

    # Speed
    speed_text = f"Speed: {game_state.game_speed}x"
    arcade.draw_text(speed_text, 200, screen_height - 30, COLOR_UI_TEXT, 14, font_name="Arial")

    # Player country and resources
    if game_state.player_country:
        country = game_state.country_manager.get_country(game_state.player_country)
        if country:
            info_x = screen_width - 600
            arcade.draw_text(f"{country.name}", info_x, screen_height - 30,
                           COLOR_UI_TEXT, 14, bold=True, font_name="Arial")

            info_x += 150
            arcade.draw_text(f"${country.money:.0f}", info_x, screen_height - 30,
                           (100, 255, 100), 14, font_name="Arial")

            info_x += 100
            arcade.draw_text(f"MP: {country.manpower}", info_x, screen_height - 30,
                           (255, 200, 100), 14, font_name="Arial")

            info_x += 120
            land_units = game_state.military_system.count_units_by_category(country.code, "land")
            arcade.draw_text(f"Units: {land_units}", info_x, screen_height - 30,
                           (200, 200, 255), 14, font_name="Arial")


def draw_economy_panel(game_state, screen_height):
    """Draw economy panel on the left side"""
    if not game_state.player_country:
        return

    country = game_state.country_manager.get_country(game_state.player_country)
    if not country:
        return

    panel_x = 10
    panel_y = screen_height - 100
    panel_width = 240
    panel_height = 250

    # Background
    arcade.draw_rectangle_filled(
        panel_x + panel_width // 2, panel_y - panel_height // 2,
        panel_width, panel_height, COLOR_UI_BACKGROUND
    )

    # Border
    arcade.draw_rectangle_outline(
        panel_x + panel_width // 2, panel_y - panel_height // 2,
        panel_width, panel_height, COLOR_UI_BORDER, 2
    )

    # Title
    arcade.draw_text("ECONOMY", panel_x + 10, panel_y - 20,
                    COLOR_UI_TEXT, 14, bold=True, font_name="Arial")

    # Economic info
    y = panel_y - 50
    line_height = 22

    # Calculate income
    provinces = game_state.province_manager.get_provinces_by_owner(country.code)
    daily_income = sum(p.get_income() for p in provinces)

    texts = [
        f"Provinces: {len(provinces)}",
        f"Daily Income: ${daily_income:.1f}",
        f"Treasury: ${country.money:.0f}",
        "",
        f"Manpower: {country.manpower:,}",
        f"Mil Factories: {country.military_factories}",
        f"Civ Factories: {country.civilian_factories}",
    ]

    for text in texts:
        arcade.draw_text(text, panel_x + 15, y, COLOR_UI_TEXT, 12, font_name="Arial")
        y -= line_height


def draw_military_panel(game_state, screen_height):
    """Draw military panel on the left side below economy"""
    if not game_state.player_country:
        return

    country = game_state.country_manager.get_country(game_state.player_country)
    if not country:
        return

    panel_x = 10
    panel_y = screen_height - 380
    panel_width = 240
    panel_height = 200

    # Background
    arcade.draw_rectangle_filled(
        panel_x + panel_width // 2, panel_y - panel_height // 2,
        panel_width, panel_height, COLOR_UI_BACKGROUND
    )

    # Border
    arcade.draw_rectangle_outline(
        panel_x + panel_width // 2, panel_y - panel_height // 2,
        panel_width, panel_height, COLOR_UI_BORDER, 2
    )

    # Title
    arcade.draw_text("MILITARY", panel_x + 10, panel_y - 20,
                    COLOR_UI_TEXT, 14, bold=True, font_name="Arial")

    # Military info
    y = panel_y - 50
    line_height = 22

    land_units = game_state.military_system.count_units_by_category(country.code, "land")
    sea_units = game_state.military_system.count_units_by_category(country.code, "sea")
    air_units = game_state.military_system.count_units_by_category(country.code, "air")

    texts = [
        f"Land Units: {land_units}",
        f"Naval Units: {sea_units}",
        f"Air Units: {air_units}",
        "",
        f"At War: {len(country.at_war_with)}",
    ]

    # Show wars
    if country.at_war_with:
        texts.append("")
        for enemy_code in country.at_war_with:
            enemy = game_state.country_manager.get_country(enemy_code)
            if enemy:
                war_score = country.war_scores.get(enemy_code, 0)
                texts.append(f"vs {enemy.name}: {war_score}%")

    for text in texts:
        arcade.draw_text(text, panel_x + 15, y, COLOR_UI_TEXT, 12, font_name="Arial")
        y -= line_height


def draw_province_info(game_state, province, screen_width, screen_height):
    """Draw info panel for selected province"""
    panel_x = screen_width - 250
    panel_y = screen_height - 100
    panel_width = 240
    panel_height = 300

    # Background
    arcade.draw_rectangle_filled(
        panel_x + panel_width // 2, panel_y - panel_height // 2,
        panel_width, panel_height, COLOR_UI_BACKGROUND
    )

    # Border
    arcade.draw_rectangle_outline(
        panel_x + panel_width // 2, panel_y - panel_height // 2,
        panel_width, panel_height, COLOR_UI_BORDER, 2
    )

    # Title
    arcade.draw_text("PROVINCE", panel_x + 10, panel_y - 20,
                    COLOR_UI_TEXT, 14, bold=True, font_name="Arial")

    # Province info
    y = panel_y - 50
    line_height = 20

    texts = [
        f"{province.name}",
        f"ID: {province.province_id}",
        "",
        f"Owner: {province.owner or 'None'}",
        f"Terrain: {province.terrain_type}",
        f"Development: {province.development}",
        f"Population: {province.population:,}",
        f"Income: ${province.get_income():.1f}",
    ]

    # Units in province
    units = game_state.military_system.get_units_in_province(province.province_id)
    if units:
        texts.append("")
        texts.append(f"Units: {len(units)}")
        for unit in units[:5]:  # Show max 5
            template = game_state.unit_template_manager.get_template(unit.template_id)
            if template:
                texts.append(f"  {template.name} ({unit.owner})")

    # Battle info
    battle = game_state.combat_system.get_battle_in_province(province.province_id)
    if battle:
        texts.append("")
        texts.append("BATTLE IN PROGRESS!")
        texts.append(f"Duration: {battle.duration:.0f}h")

    for text in texts:
        arcade.draw_text(text, panel_x + 10, y, COLOR_UI_TEXT, 11, font_name="Arial")
        y -= line_height

    # Recruitment buttons area
    if province.owner == game_state.player_country:
        y -= 10
        arcade.draw_text("Recruit (Press R):", panel_x + 10, y,
                        COLOR_UI_TEXT, 11, bold=True, font_name="Arial")


def draw_unit_recruitment_ui(game_state, screen_width, screen_height):
    """Draw unit recruitment interface"""
    if not game_state.selected_province_id:
        return

    province = game_state.province_manager.get_province(game_state.selected_province_id)
    if not province or province.owner != game_state.player_country:
        return

    # Show available unit templates
    panel_x = screen_width // 2 - 200
    panel_y = screen_height // 2
    panel_width = 400
    panel_height = 300

    arcade.draw_rectangle_filled(
        panel_x + panel_width // 2, panel_y,
        panel_width, panel_height, COLOR_UI_BACKGROUND
    )

    arcade.draw_rectangle_outline(
        panel_x + panel_width // 2, panel_y,
        panel_width, panel_height, COLOR_UI_BORDER, 3
    )

    y = panel_y + panel_height // 2 - 30
    arcade.draw_text("RECRUIT UNITS (ESC to close)",
                    panel_x + 20, y, COLOR_UI_TEXT, 14, bold=True, font_name="Arial")

    y -= 40

    # Show templates
    templates = game_state.unit_template_manager.get_templates_by_category("land")
    for i, template in enumerate(templates[:5]):
        text = f"{i+1}. {template.name} - ${template.cost:.0f}, {template.manpower_cost} MP"
        arcade.draw_text(text, panel_x + 20, y, COLOR_UI_TEXT, 12, font_name="Arial")
        y -= 25


def draw_notification(message, screen_width, screen_height):
    """Draw a notification message"""
    arcade.draw_text(message, screen_width // 2, 100,
                    (255, 255, 100), 16, anchor_x="center",
                    bold=True, font_name="Arial")
