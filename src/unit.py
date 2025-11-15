"""
Military unit data structures and templates
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class UnitTemplate:
    """Template defining a type of unit"""
    template_id: str
    name: str
    category: str  # "land", "sea", "air"
    attack: int
    defense: int
    max_hp: int
    max_organization: int
    speed: float
    cost: float
    manpower_cost: int
    combat_width: int = 2  # How much space in battle

    def __hash__(self):
        return hash(self.template_id)


@dataclass
class Unit:
    """Instance of a military unit"""
    unit_id: int
    template_id: str
    owner: str  # Country code
    location: int  # Province ID
    current_hp: int
    organization: int
    experience: int = 0
    strength: float = 1.0  # 0.0 to 1.0
    is_moving: bool = False
    move_target: Optional[int] = None

    def get_effective_attack(self, template: UnitTemplate) -> float:
        """Get effective attack value based on HP and org"""
        return template.attack * self.strength * (self.organization / 100.0)

    def get_effective_defense(self, template: UnitTemplate) -> float:
        """Get effective defense value"""
        return template.defense * self.strength * (self.organization / 100.0)

    def take_damage(self, damage: float, template: UnitTemplate):
        """Apply damage to unit"""
        # Damage reduces both HP and organization
        hp_damage = damage * 0.5
        org_damage = damage * 0.5

        self.current_hp -= int(hp_damage)
        self.organization -= int(org_damage)

        self.current_hp = max(0, self.current_hp)
        self.organization = max(0, self.organization)

        # Update strength based on HP
        self.strength = self.current_hp / template.max_hp

    def is_destroyed(self) -> bool:
        """Check if unit is destroyed"""
        return self.current_hp <= 0

    def should_retreat(self) -> bool:
        """Check if unit should retreat"""
        return self.organization <= 20  # Retreat at 20% org


class UnitTemplateManager:
    """Manages unit templates"""

    def __init__(self):
        self.templates = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self):
        """Create default unit templates"""
        # Land units
        self.add_template(UnitTemplate(
            template_id="infantry",
            name="Infantry Division",
            category="land",
            attack=30,
            defense=50,
            max_hp=100,
            max_organization=100,
            speed=4.0,
            cost=100.0,
            manpower_cost=1000,
            combat_width=2
        ))

        self.add_template(UnitTemplate(
            template_id="armor",
            name="Armored Division",
            category="land",
            attack=70,
            defense=40,
            max_hp=150,
            max_organization=80,
            speed=8.0,
            cost=500.0,
            manpower_cost=500,
            combat_width=3
        ))

        self.add_template(UnitTemplate(
            template_id="artillery",
            name="Artillery Division",
            category="land",
            attack=60,
            defense=20,
            max_hp=80,
            max_organization=70,
            speed=3.0,
            cost=300.0,
            manpower_cost=800,
            combat_width=2
        ))

        # Naval units
        self.add_template(UnitTemplate(
            template_id="destroyer",
            name="Destroyer",
            category="sea",
            attack=20,
            defense=30,
            max_hp=100,
            max_organization=100,
            speed=30.0,
            cost=800.0,
            manpower_cost=200,
            combat_width=1
        ))

        self.add_template(UnitTemplate(
            template_id="battleship",
            name="Battleship",
            category="sea",
            attack=100,
            defense=80,
            max_hp=300,
            max_organization=100,
            speed=20.0,
            cost=3000.0,
            manpower_cost=500,
            combat_width=3
        ))

        # Air units
        self.add_template(UnitTemplate(
            template_id="fighter",
            name="Fighter Squadron",
            category="air",
            attack=40,
            defense=30,
            max_hp=100,
            max_organization=100,
            speed=500.0,
            cost=400.0,
            manpower_cost=100,
            combat_width=1
        ))

        self.add_template(UnitTemplate(
            template_id="bomber",
            name="Bomber Squadron",
            category="air",
            attack=80,
            defense=15,
            max_hp=80,
            max_organization=80,
            speed=400.0,
            cost=600.0,
            manpower_cost=150,
            combat_width=2
        ))

    def add_template(self, template: UnitTemplate):
        """Add a unit template"""
        self.templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[UnitTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> List[UnitTemplate]:
        """Get all templates"""
        return list(self.templates.values())

    def get_templates_by_category(self, category: str) -> List[UnitTemplate]:
        """Get all templates of a category"""
        return [t for t in self.templates.values() if t.category == category]
