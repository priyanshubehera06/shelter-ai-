"""
geometry.py — Physical structure and parametric envelope engine for Shelter-AI.
Defines building geometry, spatial dimensions, openings, envelope areas,
volume, compactness ratio (S/V), and generative design variants for optimization.
"""

import math
from typing import Dict, List, Optional, Any


class ShelterGeometry:
    """
    Parametric building geometry engine defining physical structure,
    envelopes, openings, solar exposure, and compactness ratios.
    """

    def __init__(
        self,
        length_m: float = 6.0,
        width_m: float = 4.0,
        height_m: float = 2.8,
        shelter_type: str = "transitional",
        roof_type: str = "pitched",
        roof_pitch_deg: float = 15.0,
        wall_thickness_m: float = 0.20,
        wall_thickness_cm: Optional[float] = None,
        wwr_pct: float = 15.0,
        window_width_m: Optional[float] = None,
        window_height_m: Optional[float] = None,
        window_count: Optional[int] = None,
        door_width_m: float = 0.9,
        door_height_m: float = 2.1,
        door_count: int = 0,
        overhang_m: float = 0.5,
        ventilation_area_m2: Optional[float] = None,
        orientation_deg: float = 0.0,
    ):
        # 1. Primary Physical Dimensions
        self.length = max(1.5, float(length_m))
        self.width = max(1.5, float(width_m))
        self.height = max(1.8, float(height_m))
        self.shelter_type = str(shelter_type)
        self.orientation = float(orientation_deg) % 360.0

        # 2. Roof Configuration
        self.roof_type = str(roof_type).lower()
        self.roof_pitch = max(0.0, min(60.0, float(roof_pitch_deg))) if self.roof_type != "flat" else 0.0
        self.overhang = max(0.0, float(overhang_m))

        # 3. Wall Thickness (supports both m and cm inputs)
        if wall_thickness_cm is not None:
            self.wall_thickness = float(wall_thickness_cm) / 100.0
        else:
            self.wall_thickness = float(wall_thickness_m)

        # 4. Window & Glazing Parameters
        self.wwr = max(0.0, min(60.0, float(wwr_pct))) / 100.0
        self.window_width = float(window_width_m) if window_width_m is not None else None
        self.window_height = float(window_height_m) if window_height_m is not None else None
        self.window_count = int(window_count) if window_count is not None else None

        # 5. Door Openings
        self.door_width = max(0.0, float(door_width_m))
        self.door_height = max(0.0, float(door_height_m))
        self.door_count = max(0, int(door_count))

        # 6. Ventilation Openings
        self._custom_vent_area = float(ventilation_area_m2) if ventilation_area_m2 is not None else None

    # ----------------------------------------------------------------------
    # Core Spatial & Envelope Calculations
    # ----------------------------------------------------------------------

    def floor_area(self) -> float:
        """Usable internal footprint floor area (m²)."""
        return round(self.length * self.width, 2)

    def footprint_perimeter(self) -> float:
        """Building envelope base perimeter (m)."""
        return round(2.0 * (self.length + self.width), 2)

    def gross_wall_area(self) -> float:
        """
        Total vertical gross wall perimeter area (m²).
        Formula: 2 × (Length + Width) × Height
        """
        return round(2.0 * (self.length + self.width) * self.height, 2)

    def wall_area(self) -> float:
        """Alias for gross_wall_area (m²)."""
        return self.gross_wall_area()

    def window_area(self) -> float:
        """
        Total window / glazing area (m²).
        Computed from explicit dimensions or Window-to-Wall Ratio (WWR).
        """
        if self.window_width is not None and self.window_height is not None and self.window_count is not None:
            return round(self.window_width * self.window_height * self.window_count, 2)
        return round(self.gross_wall_area() * self.wwr, 2)

    def glazing_area(self) -> float:
        """Alias for window_area for thermal engine compatibility (m²)."""
        return self.window_area()

    def door_area(self) -> float:
        """Total door openings area (m²)."""
        return round(self.door_width * self.door_height * self.door_count, 2)

    def ventilation_area(self) -> float:
        """
        Passive ventilation opening area (louvers, clerestory, jali) (m²).
        Defaults to 5% of floor area if not explicitly specified.
        """
        if self._custom_vent_area is not None:
            return round(self._custom_vent_area, 2)
        return round(self.floor_area() * 0.05, 2)

    def total_openings_area(self) -> float:
        """Combined area of all building envelope openings (m²)."""
        return round(self.window_area() + self.door_area() + (self._custom_vent_area or 0.0), 2)

    def net_wall_area(self) -> float:
        """
        Opaque net wall surface area excluding window/door openings (m²).
        """
        net = self.gross_wall_area() - self.window_area() - self.door_area()
        return round(max(0.0, net), 2)

    def opening_to_wall_ratio(self) -> float:
        """Ratio of total envelope openings to gross wall area (fraction)."""
        gross = self.gross_wall_area()
        if gross <= 0:
            return 0.0
        return round(min(1.0, self.total_openings_area() / gross), 3)

    # ----------------------------------------------------------------------
    # Roof & Volumetric Calculations
    # ----------------------------------------------------------------------

    def roof_height_delta(self) -> float:
        """Vertical rise of roof apex / ridge above the wall plate line (m)."""
        if self.roof_type == "pitched":
            return (self.width / 2.0) * math.tan(math.radians(self.roof_pitch))
        elif self.roof_type == "monoslope":
            return self.width * math.tan(math.radians(self.roof_pitch))
        elif self.roof_type == "hipped":
            return (min(self.width, self.length) / 2.0) * math.tan(math.radians(self.roof_pitch))
        return 0.15  # flat slab default thickness

    def roof_area(self) -> float:
        """
        Total sloped or flat roof surface area including overhang eaves (m²).
        """
        eave_l = self.length + 2.0 * self.overhang
        eave_w = self.width + 2.0 * self.overhang
        flat_footprint = eave_l * eave_w

        if self.roof_type in ["pitched", "monoslope", "hipped"] and self.roof_pitch > 0:
            rad = math.radians(self.roof_pitch)
            return round(flat_footprint / math.cos(rad), 2)
        return round(flat_footprint, 2)

    def volume(self) -> float:
        """
        Total internal air volume (m³), combining the base room volume
        and overhead attic/roof volume.
        """
        base_vol = self.length * self.width * self.height
        roof_vol = 0.0
        if self.roof_type == "pitched":
            roof_h = self.roof_height_delta()
            roof_vol = 0.5 * self.width * roof_h * self.length
        elif self.roof_type == "monoslope":
            roof_h = self.roof_height_delta()
            roof_vol = 0.5 * self.width * roof_h * self.length
        elif self.roof_type == "hipped":
            roof_h = self.roof_height_delta()
            roof_vol = (1.0 / 3.0) * self.width * self.length * roof_h
        return round(base_vol + roof_vol, 2)

    def exposed_surface_area(self, include_ground: bool = False) -> float:
        """
        Total external building envelope surface area exposed to ambient climate (m²).
        Sums gross wall area + roof area (+ floor if elevated).
        """
        exposed = self.gross_wall_area() + self.roof_area()
        if include_ground:
            exposed += self.floor_area()
        return round(exposed, 2)

    def surface_to_volume_ratio(self, include_ground: bool = False) -> float:
        """
        Surface-to-Volume ratio (S/V ratio in m⁻¹), measuring thermal compactness.
        Lower S/V values indicate higher thermal efficiency and less heat exchange.
        """
        vol = self.volume()
        if vol <= 0:
            return 0.0
        return round(self.exposed_surface_area(include_ground=include_ground) / vol, 3)

    def shading_factor(self, solar_elevation_deg: float = 60.0) -> float:
        """
        Fraction of window surface shaded by roof overhang at a given solar elevation.
        """
        if self.overhang <= 0.0 or solar_elevation_deg <= 0.0:
            return 0.0
        tan_sol = math.tan(math.radians(solar_elevation_deg))
        shaded_height = self.overhang * tan_sol
        window_height = self.height * 0.4
        shade_ratio = shaded_height / max(0.1, window_height)
        return round(min(1.0, max(0.0, shade_ratio)), 3)

    # ----------------------------------------------------------------------
    # Summaries & Formatting
    # ----------------------------------------------------------------------

    def dimensions_str(self) -> str:
        """Formatted dimensions string (e.g. '6.0 × 4.0 × 2.8 m')."""
        return f"{self.length:.1f} × {self.width:.1f} × {self.height:.1f} m"

    def envelope_summary(self) -> Dict[str, Any]:
        """
        Comprehensive data dictionary of physical and thermal envelope parameters.
        """
        return {
            "shelter_type": self.shelter_type,
            "length_m": self.length,
            "width_m": self.width,
            "height_m": self.height,
            "dimensions": self.dimensions_str(),
            "orientation_deg": self.orientation,
            "floor_area_m2": self.floor_area(),
            "perimeter_m": self.footprint_perimeter(),
            "gross_wall_area_m2": self.gross_wall_area(),
            "net_wall_area_m2": self.net_wall_area(),
            "roof_area_m2": self.roof_area(),
            "roof_type": self.roof_type,
            "roof_pitch_deg": self.roof_pitch,
            "roof_height_delta_m": round(self.roof_height_delta(), 2),
            "window_area_m2": self.window_area(),
            "glazing_area_m2": self.glazing_area(),
            "door_area_m2": self.door_area(),
            "ventilation_area_m2": self.ventilation_area(),
            "total_openings_area_m2": self.total_openings_area(),
            "volume_m3": self.volume(),
            "exposed_surface_area_m2": self.exposed_surface_area(),
            "surface_to_volume_ratio": self.surface_to_volume_ratio(),
            "opening_to_wall_ratio": self.opening_to_wall_ratio(),
            "wwr_pct": round(self.wwr * 100.0, 1),
            "wall_thickness_m": self.wall_thickness,
            "wall_thickness_cm": round(self.wall_thickness * 100.0, 1),
            "overhang_m": self.overhang,
            "shading_factor": self.shading_factor(),
        }

    # ----------------------------------------------------------------------
    # Factory & Generative Design Methods
    # ----------------------------------------------------------------------

    @classmethod
    def from_occupants(
        cls,
        occupants: int = 4,
        standard_m2_per_person: float = 3.5,
        ceiling_height: float = 2.8,
        roof_type: str = "pitched",
        roof_pitch_deg: float = 15.0,
        wwr_pct: float = 15.0,
        overhang_m: float = 0.6,
        orientation_deg: float = 0.0,
    ) -> "ShelterGeometry":
        """
        Dynamically auto-dimensions shelter footprint based on Sphere Humanitarian
        Standards (default 3.5 m²/person).
        """
        min_floor_area = max(1.0, float(occupants)) * float(standard_m2_per_person)
        aspect_ratio = 1.5  # standard 3:2 architectural ratio

        w = math.sqrt(min_floor_area / aspect_ratio)
        l = w * aspect_ratio

        return cls(
            length_m=round(l, 1),
            width_m=round(w, 1),
            height_m=ceiling_height,
            roof_type=roof_type,
            roof_pitch_deg=roof_pitch_deg,
            wwr_pct=wwr_pct,
            overhang_m=overhang_m,
            orientation_deg=orientation_deg,
        )

    @staticmethod
    def generate_design_variants(
        target_floor_area_m2: float = 24.0,
        roof_type: str = "pitched",
        roof_pitch_deg: float = 15.0,
        wwr_pct: float = 20.0,
        overhang_m: float = 0.5,
        orientation_deg: float = 0.0,
    ) -> List["ShelterGeometry"]:
        """
        Generates distinct structural design alternatives for optimizer evaluation:
        - Design 1: 6.0 × 4.0 × 3.0 m (Standard 3:2 aspect)
        - Design 2: 8.0 × 3.0 × 3.5 m (Elongated high-ceiling)
        - Design 3: 6.0 × 5.0 × 2.8 m (Compact high-volume)
        """
        configs = [
            (6.0, 4.0, 3.0, "Design 1 (6×4×3m)"),
            (8.0, 3.0, 3.5, "Design 2 (8×3×3.5m)"),
            (6.0, 5.0, 2.8, "Design 3 (6×5×2.8m)"),
        ]

        designs = []
        for l, w, h, name in configs:
            designs.append(
                ShelterGeometry(
                    length_m=l,
                    width_m=w,
                    height_m=h,
                    shelter_type=name,
                    roof_type=roof_type,
                    roof_pitch_deg=roof_pitch_deg,
                    wwr_pct=wwr_pct,
                    overhang_m=overhang_m,
                    orientation_deg=orientation_deg,
                )
            )

        return designs
