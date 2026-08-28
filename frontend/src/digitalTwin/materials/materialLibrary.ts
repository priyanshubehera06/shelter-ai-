/**
 * materialLibrary.ts — PBR parameters, roughness, metalness, and fallback shaders for Three.js.
 */

export interface MaterialPBRDefinition {
  id: string;
  name: string;
  category: 'Wall' | 'Roof' | 'Floor' | 'Glazing' | 'Door' | 'Insulation';
  color: string;
  roughness: number;
  metalness: number;
  opacity?: number;
  transparent?: boolean;
  wireframe?: boolean;
}

export const PBR_MATERIALS: Record<string, MaterialPBRDefinition> = {
  // Wall Materials
  cseb_interlocking: { id: 'cseb_interlocking', name: 'CSEB Interlocking Block', category: 'Wall', color: '#b58d6b', roughness: 0.90, metalness: 0.02 },
  ceb_standard: { id: 'ceb_standard', name: 'Compressed Earth Block', category: 'Wall', color: '#a07855', roughness: 0.92, metalness: 0.02 },
  brick_standard: { id: 'brick_standard', name: 'Burnt Clay Brick', category: 'Wall', color: '#a34839', roughness: 0.85, metalness: 0.04 },
  aac_block: { id: 'aac_block', name: 'AAC Lightweight Block', category: 'Wall', color: '#dcdde1', roughness: 0.95, metalness: 0.01 },
  stone_masonry: { id: 'stone_masonry', name: 'Random Rubble Stone', category: 'Wall', color: '#7f8c8d', roughness: 0.88, metalness: 0.05 },
  eps_sandwich: { id: 'eps_sandwich', name: 'EPS Insulated Sandwich Panel', category: 'Wall', color: '#ecf0f1', roughness: 0.40, metalness: 0.35 },
  bamboo_composite: { id: 'bamboo_composite', name: 'Bamboo Composite Mat', category: 'Wall', color: '#c8b075', roughness: 0.70, metalness: 0.02 },
  timber_panel: { id: 'timber_panel', name: 'Treated Timber Panel', category: 'Wall', color: '#8d6e63', roughness: 0.65, metalness: 0.03 },

  // Roof Materials
  roof_cgi_sheet: { id: 'roof_cgi_sheet', name: 'Corrugated Galvanized Iron (CGI)', category: 'Roof', color: '#7f8c8d', roughness: 0.30, metalness: 0.85 },
  roof_cgi_insulated: { id: 'roof_cgi_insulated', name: 'Insulated Sandwich CGI Panel', category: 'Roof', color: '#34495e', roughness: 0.40, metalness: 0.70 },
  roof_concrete_slab: { id: 'roof_concrete_slab', name: 'Reinforced Concrete Roof Slab', category: 'Roof', color: '#95a5a6', roughness: 0.90, metalness: 0.05 },
  roof_bamboo_thatch: { id: 'roof_bamboo_thatch', name: 'Treated Bamboo Thatch', category: 'Roof', color: '#8d704b', roughness: 0.95, metalness: 0.01 },
  roof_clay_tile: { id: 'roof_clay_tile', name: 'Mangalore Terracotta Clay Tile', category: 'Roof', color: '#d35400', roughness: 0.82, metalness: 0.02 },
  roof_bipv_solar: { id: 'roof_bipv_solar', name: 'Building-Integrated PV Glass', category: 'Roof', color: '#1b1464', roughness: 0.15, metalness: 0.95 },

  // Floor Materials
  floor_concrete_screed: { id: 'floor_concrete_screed', name: 'Smooth Concrete Screed', category: 'Floor', color: '#57606f', roughness: 0.90, metalness: 0.05 },
  floor_terracotta_tile: { id: 'floor_terracotta_tile', name: 'Terracotta Floor Tiles', category: 'Floor', color: '#c0392b', roughness: 0.75, metalness: 0.03 },
  floor_timber_finish: { id: 'floor_timber_finish', name: 'Engineered Wood Planks', category: 'Floor', color: '#795548', roughness: 0.60, metalness: 0.05 },

  // Glazing Materials
  glazing_single: { id: 'glazing_single', name: 'Clear Single Float Glass', category: 'Glazing', color: '#81ecec', roughness: 0.10, metalness: 0.90, opacity: 0.60, transparent: true },
  glazing_double: { id: 'glazing_double', name: 'Double Glazed Low-E Unit', category: 'Glazing', color: '#74b9ff', roughness: 0.10, metalness: 0.90, opacity: 0.55, transparent: true },
  glazing_low_e: { id: 'glazing_low_e', name: 'Solar Control Low-E Glass', category: 'Glazing', color: '#0984e3', roughness: 0.10, metalness: 0.90, opacity: 0.50, transparent: true },
  glazing_polycarb: { id: 'glazing_polycarb', name: 'Multiwall Polycarbonate Sheet', category: 'Glazing', color: '#a29bfe', roughness: 0.25, metalness: 0.40, opacity: 0.65, transparent: true },

  // Door & Wood Details
  door_timber_composite: { id: 'door_timber_composite', name: 'Solid Core Timber Door', category: 'Door', color: '#5d4037', roughness: 0.65, metalness: 0.05 },
  frame_aluminum: { id: 'frame_aluminum', name: 'Anodized Aluminum Frame', category: 'Wall', color: '#2d3436', roughness: 0.35, metalness: 0.85 },
};

export const getPBRMaterial = (materialId?: string): MaterialPBRDefinition => {
  if (!materialId || !PBR_MATERIALS[materialId]) {
    return {
      id: 'default',
      name: 'Default Structural Material',
      category: 'Wall',
      color: '#95a5a6',
      roughness: 0.85,
      metalness: 0.05,
    };
  }
  return PBR_MATERIALS[materialId];
};
