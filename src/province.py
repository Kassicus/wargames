"""
Province data structures and management
"""
from typing import Tuple, List, Optional
from dataclasses import dataclass, field


@dataclass
class Province:
    """Represents a single province on the map"""

    province_id: int
    name: str
    color_rgb: Tuple[int, int, int]  # RGB color for ID map
    terrain_type: str = "plains"
    development: int = 1
    population: int = 1000
    owner: Optional[str] = None  # Country code (e.g., "USA", "GER")
    adjacent_provinces: List[int] = field(default_factory=list)

    # Economic properties
    base_income: float = 10.0
    manpower_pool: int = 1000

    # Military properties
    fortification_level: int = 0
    is_capital: bool = False
    is_coastal: bool = False

    def get_income(self) -> float:
        """Calculate province income based on development"""
        return self.base_income * self.development

    def get_recruitable_manpower(self) -> int:
        """Calculate available manpower for recruitment"""
        return int(self.population * 0.1)  # 10% of population can be recruited

    def __hash__(self):
        return hash(self.province_id)

    def __eq__(self, other):
        if isinstance(other, Province):
            return self.province_id == other.province_id
        return False


class ProvinceManager:
    """Manages all provinces in the game"""

    def __init__(self):
        self.provinces = {}  # province_id -> Province
        self.color_to_province = {}  # (r, g, b) -> province_id

    def add_province(self, province: Province):
        """Add a province to the manager"""
        self.provinces[province.province_id] = province
        self.color_to_province[province.color_rgb] = province.province_id

    def get_province(self, province_id: int) -> Optional[Province]:
        """Get province by ID"""
        return self.provinces.get(province_id)

    def get_province_by_color(self, color: Tuple[int, int, int]) -> Optional[Province]:
        """Get province by RGB color from ID map"""
        province_id = self.color_to_province.get(color)
        if province_id is not None:
            return self.provinces.get(province_id)
        return None

    def get_provinces_by_owner(self, country_code: str) -> List[Province]:
        """Get all provinces owned by a country"""
        return [p for p in self.provinces.values() if p.owner == country_code]

    def calculate_adjacency(self, id_map_data):
        """Calculate adjacent provinces from ID map pixel data"""
        # This will be implemented when we load the map
        pass
