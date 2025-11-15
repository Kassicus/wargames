"""
Grand Strategy Game - Main Entry Point
"""
import arcade
from src.constants import *
from src.game import GameState
from src.data_loader import load_game_data
from src.map_renderer import MapRenderer
from src.ui.panels import (draw_top_bar, draw_economy_panel, draw_military_panel,
                           draw_province_info)


class GrandStrategyGame(arcade.Window):
    """Main game window"""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(COLOR_OCEAN)

        # Game state
        self.game_state = GameState()

        # Camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Camera position and zoom
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 1.0

        # Map renderer
        self.map_renderer = None

        # Mouse state
        self.mouse_x = 0
        self.mouse_y = 0
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

    def setup(self):
        """Set up the game"""
        # Load game data (provinces, countries, etc.)
        load_game_data(self.game_state)

        # Initialize game systems
        self.game_state.initialize_systems()

        # Initialize map renderer
        self.map_renderer = MapRenderer(self.game_state.province_manager)

        # Set player country (for now, first country in list)
        countries = self.game_state.country_manager.get_all_countries()
        if countries:
            self.game_state.set_player_country(countries[0].code)

        # Give each country some starting units
        for country in countries:
            capital = self.game_state.province_manager.get_province(country.capital_province_id)
            if capital:
                # Create 2 infantry units at capital
                self.game_state.military_system.create_unit("infantry", country.code, capital.province_id)
                self.game_state.military_system.create_unit("infantry", country.code, capital.province_id)

        print("Game setup complete!")
        print(f"Loaded {len(self.game_state.province_manager.provinces)} provinces")
        print(f"Loaded {len(self.game_state.country_manager.countries)} countries")
        print(f"Created {len(self.game_state.military_system.units)} starting units")

    def on_update(self, delta_time):
        """Update game state"""
        self.game_state.update(delta_time)

    def on_draw(self):
        """Render the game"""
        self.clear()

        # Use game camera for world rendering
        self.camera.use()

        # Draw the map
        if self.map_renderer:
            self.map_renderer.draw(
                self.camera_x,
                self.camera_y,
                self.zoom_level,
                self.game_state.selected_province_id,
                self.game_state.country_manager
            )

        # Draw units on map
        self.draw_units()

        # Use GUI camera for UI
        self.gui_camera.use()

        # Draw UI elements
        self.draw_ui()

    def draw_ui(self):
        """Draw UI elements (top bar, side panels, etc.)"""
        # Draw all UI panels using the panel functions
        draw_top_bar(self.game_state, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_economy_panel(self.game_state, SCREEN_HEIGHT)
        draw_military_panel(self.game_state, SCREEN_HEIGHT)

        # Selected province info
        selected_province = self.game_state.get_selected_province()
        if selected_province:
            draw_province_info(self.game_state, selected_province, SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw_units(self):
        """Draw military units on the map"""
        if not self.game_state.military_system:
            return

        # Get province positions from map
        provinces_list = list(self.game_state.province_manager.provinces.values())
        grid_cols = 3
        grid_rows = 3
        cell_width = 800 // grid_cols
        cell_height = 600 // grid_rows

        for unit in self.game_state.military_system.units:
            # Find province position
            try:
                province_index = [p.province_id for p in provinces_list].index(unit.location)
            except ValueError:
                continue

            col = province_index % grid_cols
            row = province_index // grid_cols

            x = (col * cell_width + cell_width // 2) * self.zoom_level
            y = (row * cell_height + cell_height // 2) * self.zoom_level

            # Get unit owner color
            country = self.game_state.country_manager.get_country(unit.owner)
            if country:
                color = tuple(country.color)
            else:
                color = (255, 255, 255)

            # Draw unit as a small square
            size = 10 * self.zoom_level
            arcade.draw_rectangle_filled(x, y, size, size, color)

            # Draw health bar
            if self.zoom_level > 0.8:
                bar_width = size
                bar_height = 2 * self.zoom_level
                health_pct = unit.strength
                arcade.draw_rectangle_filled(
                    x, y - size // 2 - 3,
                    bar_width * health_pct, bar_height,
                    (0, 255, 0)
                )
                arcade.draw_rectangle_outline(
                    x, y - size // 2 - 3,
                    bar_width, bar_height,
                    (255, 255, 255), 1
                )

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check if clicking on map (not UI)
            if y < SCREEN_HEIGHT - 40:
                # Convert screen coordinates to world coordinates
                world_x = (x + self.camera_x) / self.zoom_level
                world_y = (y + self.camera_y) / self.zoom_level

                # Check which province was clicked
                if self.map_renderer:
                    province = self.map_renderer.get_province_at_point(world_x, world_y)
                    if province:
                        self.game_state.select_province(province.province_id)
                        print(f"Selected province: {province.name} (ID: {province.province_id})")

        elif button == arcade.MOUSE_BUTTON_RIGHT:
            # Start dragging
            self.is_dragging = True
            self.drag_start_x = x
            self.drag_start_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release"""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.is_dragging = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion"""
        self.mouse_x = x
        self.mouse_y = y

        if self.is_dragging:
            # Pan camera
            self.camera_x -= dx
            self.camera_y -= dy

            # Clamp camera position
            self.camera_x = max(0, min(self.camera_x, MAP_WIDTH * self.zoom_level - SCREEN_WIDTH))
            self.camera_y = max(0, min(self.camera_y, MAP_HEIGHT * self.zoom_level - SCREEN_HEIGHT))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Handle mouse scroll (zoom)"""
        # Get mouse position in world coordinates before zoom
        world_x_before = (x + self.camera_x) / self.zoom_level
        world_y_before = (y + self.camera_y) / self.zoom_level

        # Update zoom
        old_zoom = self.zoom_level
        self.zoom_level += scroll_y * ZOOM_SPEED
        self.zoom_level = max(ZOOM_MIN, min(ZOOM_MAX, self.zoom_level))

        # Adjust camera to keep mouse position constant
        world_x_after = (x + self.camera_x) / self.zoom_level
        world_y_after = (y + self.camera_y) / self.zoom_level

        self.camera_x += (world_x_after - world_x_before) * self.zoom_level
        self.camera_y += (world_y_after - world_y_before) * self.zoom_level

    def on_key_press(self, key, modifiers):
        """Handle key press"""
        # Pause/unpause
        if key == arcade.key.SPACE:
            self.game_state.toggle_pause()

        # Speed controls
        elif key == arcade.key.KEY_1:
            self.game_state.set_speed(GAME_SPEED_NORMAL)
        elif key == arcade.key.KEY_2:
            self.game_state.set_speed(GAME_SPEED_FAST)
        elif key == arcade.key.KEY_3:
            self.game_state.set_speed(GAME_SPEED_VERY_FAST)

        # Recruit units (I for Infantry)
        elif key == arcade.key.I:
            self.recruit_unit_in_selected_province("infantry")
        elif key == arcade.key.T:
            self.recruit_unit_in_selected_province("armor")
        elif key == arcade.key.A:
            self.recruit_unit_in_selected_province("artillery")

        # Declare war (W key on selected province)
        elif key == arcade.key.W:
            self.declare_war_on_selected_province()

        # Make peace (P key)
        elif key == arcade.key.P:
            self.make_peace_with_enemies()

        # Camera movement with arrow keys
        elif key == arcade.key.LEFT:
            self.camera_x -= CAMERA_SPEED / self.zoom_level
        elif key == arcade.key.RIGHT:
            self.camera_x += CAMERA_SPEED / self.zoom_level
        elif key == arcade.key.UP:
            self.camera_y += CAMERA_SPEED / self.zoom_level
        elif key == arcade.key.DOWN:
            self.camera_y -= CAMERA_SPEED / self.zoom_level

    def recruit_unit_in_selected_province(self, unit_type):
        """Recruit a unit in the selected province"""
        if not self.game_state.selected_province_id:
            print("No province selected")
            return

        province = self.game_state.province_manager.get_province(
            self.game_state.selected_province_id
        )

        if not province:
            return

        if province.owner != self.game_state.player_country:
            print("Can only recruit in your own provinces")
            return

        # Try to recruit
        success = self.game_state.military_system.recruit_unit(
            self.game_state.player_country,
            unit_type,
            province.province_id
        )

        if success:
            template = self.game_state.unit_template_manager.get_template(unit_type)
            print(f"Recruited {template.name} in {province.name}!")
        else:
            print(f"Cannot afford {unit_type} (check money and manpower)")

    def declare_war_on_selected_province(self):
        """Declare war on the owner of the selected province"""
        if not self.game_state.selected_province_id:
            print("No province selected")
            return

        province = self.game_state.province_manager.get_province(
            self.game_state.selected_province_id
        )

        if not province or not province.owner:
            print("Province has no owner")
            return

        if province.owner == self.game_state.player_country:
            print("Cannot declare war on yourself")
            return

        # Declare war
        self.game_state.diplomacy_system.declare_war(
            self.game_state.player_country,
            province.owner
        )

        enemy = self.game_state.country_manager.get_country(province.owner)
        print(f"Declared war on {enemy.name}!")

    def make_peace_with_enemies(self):
        """Make peace with all enemies (white peace)"""
        if not self.game_state.player_country:
            return

        country = self.game_state.country_manager.get_country(
            self.game_state.player_country
        )

        if not country or not country.at_war_with:
            print("Not at war")
            return

        # Make peace with all
        for enemy_code in list(country.at_war_with):
            self.game_state.diplomacy_system.make_peace(
                self.game_state.player_country,
                enemy_code
            )
            enemy = self.game_state.country_manager.get_country(enemy_code)
            print(f"Made peace with {enemy.name}")


def main():
    """Main entry point"""
    game = GrandStrategyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
