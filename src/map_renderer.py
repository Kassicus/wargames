"""
Map rendering system
"""
import arcade
from PIL import Image
from typing import Optional
from src.constants import *
from src.province import Province


class MapRenderer:
    """Handles rendering of the game map"""

    def __init__(self, province_manager):
        self.province_manager = province_manager

        # ID map for province detection
        self.id_map_image = None
        self.id_map_width = 0
        self.id_map_height = 0

        # Visual map texture
        self.visual_map_texture = None

        # Province shapes for rendering
        self.province_shapes = {}

        # Load or create map
        self.load_map()

    def load_map(self):
        """Load or create the province ID map"""
        try:
            # Try to load existing ID map
            self.id_map_image = Image.open("assets/maps/provinces_id.png")
            self.id_map_width, self.id_map_height = self.id_map_image.size
            print(f"Loaded province ID map: {self.id_map_width}x{self.id_map_height}")
        except FileNotFoundError:
            # Create a simple test map
            print("Province ID map not found, creating test map...")
            self.create_test_map()

        # Try to load visual map
        try:
            self.visual_map_texture = arcade.load_texture("assets/maps/visual_map.png")
        except:
            print("Visual map not found, will render provinces only")

    def create_test_map(self):
        """Create a simple test ID map"""
        from pathlib import Path
        Path("assets/maps").mkdir(parents=True, exist_ok=True)

        # Create a 800x600 test map with colored rectangles for provinces
        width, height = 800, 600
        self.id_map_image = Image.new('RGB', (width, height), COLOR_OCEAN)
        self.id_map_width = width
        self.id_map_height = height

        pixels = self.id_map_image.load()

        # Draw provinces as rectangles (3x3 grid)
        provinces_list = list(self.province_manager.provinces.values())
        grid_cols = 3
        grid_rows = 3
        cell_width = width // grid_cols
        cell_height = height // grid_rows

        for i, province in enumerate(provinces_list[:9]):  # Only first 9
            col = i % grid_cols
            row = i // grid_cols

            x_start = col * cell_width
            y_start = row * cell_height
            x_end = x_start + cell_width
            y_end = y_start + cell_height

            # Fill rectangle with province color
            for y in range(y_start, y_end):
                for x in range(x_start, x_end):
                    if x < width and y < height:
                        pixels[x, y] = province.color_rgb

        # Save the test map
        self.id_map_image.save("assets/maps/provinces_id.png")
        print(f"Created test ID map at assets/maps/provinces_id.png ({width}x{height})")

    def get_province_at_point(self, x: float, y: float) -> Optional[Province]:
        """Get the province at a given world coordinate"""
        if not self.id_map_image:
            return None

        # Convert to pixel coordinates
        px = int(x)
        py = int(y)

        # Check bounds
        if px < 0 or px >= self.id_map_width or py < 0 or py >= self.id_map_height:
            return None

        # Flip Y coordinate (image coordinates vs screen coordinates)
        py = self.id_map_height - py - 1

        try:
            # Get pixel color
            color = self.id_map_image.getpixel((px, py))
            # Look up province
            return self.province_manager.get_province_by_color(color)
        except:
            return None

    def draw(self, camera_x, camera_y, zoom, selected_province_id, country_manager):
        """Draw the map"""
        if not self.id_map_image:
            return

        # Draw provinces
        self.draw_provinces(camera_x, camera_y, zoom, country_manager)

        # Draw selected province highlight
        if selected_province_id is not None:
            self.draw_province_highlight(selected_province_id, camera_x, camera_y, zoom)

        # Draw borders
        self.draw_borders(camera_x, camera_y, zoom)

    def draw_provinces(self, camera_x, camera_y, zoom, country_manager):
        """Draw all provinces with country colors"""
        # For now, draw simple rectangles based on the test map grid
        provinces_list = list(self.province_manager.provinces.values())
        grid_cols = 3
        grid_rows = 3
        cell_width = self.id_map_width // grid_cols
        cell_height = self.id_map_height // grid_rows

        for i, province in enumerate(provinces_list[:9]):
            col = i % grid_cols
            row = i // grid_cols

            x = col * cell_width + cell_width // 2
            y = row * cell_height + cell_height // 2

            # Get country color if province is owned
            if province.owner:
                country = country_manager.get_country(province.owner)
                if country:
                    color = tuple(country.color) + (180,)  # Add alpha
                else:
                    color = (150, 150, 150, 180)  # Gray for unowned
            else:
                color = (150, 150, 150, 180)  # Gray for unowned

            # Draw province rectangle
            arcade.draw_rectangle_filled(
                x * zoom,
                y * zoom,
                cell_width * zoom,
                cell_height * zoom,
                color
            )

    def draw_province_highlight(self, province_id, camera_x, camera_y, zoom):
        """Draw highlight for selected province"""
        province = self.province_manager.get_province(province_id)
        if not province:
            return

        # Find province position in grid
        provinces_list = list(self.province_manager.provinces.values())
        try:
            i = provinces_list.index(province)
        except ValueError:
            return

        grid_cols = 3
        cell_width = self.id_map_width // grid_cols
        cell_height = self.id_map_height // grid_cols

        col = i % grid_cols
        row = i // grid_cols

        x = col * cell_width + cell_width // 2
        y = row * cell_height + cell_height // 2

        # Draw highlight outline
        arcade.draw_rectangle_outline(
            x * zoom,
            y * zoom,
            cell_width * zoom,
            cell_height * zoom,
            (255, 255, 0),
            4
        )

    def draw_borders(self, camera_x, camera_y, zoom):
        """Draw province and country borders"""
        # Draw simple grid borders for test map
        grid_cols = 3
        grid_rows = 3
        cell_width = self.id_map_width // grid_cols
        cell_height = self.id_map_height // grid_rows

        # Vertical lines
        for i in range(1, grid_cols):
            x = i * cell_width * zoom
            arcade.draw_line(
                x, 0,
                x, self.id_map_height * zoom,
                COLOR_BORDER, 2
            )

        # Horizontal lines
        for i in range(1, grid_rows):
            y = i * cell_height * zoom
            arcade.draw_line(
                0, y,
                self.id_map_width * zoom, y,
                COLOR_BORDER, 2
            )
