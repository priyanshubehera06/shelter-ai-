/**
 * MaterialLibrary.ts — Physically based rendering parameters and color palettes for shelter materials.
 */

export interface MaterialProperties {
  color: string;
  roughness: number;
  metalness: number;
  opacity?: number;
  transparent?: boolean;
}

export const MATERIAL_PBR_MAP: Record<string, MaterialProperties> = {
  cseb_interlocking: { color: '#b58d6b', roughness: 0.90, metalness: 0.02 },
  ceb_standard: { color: '#a07855', roughness: 0.92, metalness: 0.02 },
  brick_standard: { color: '#a34839', roughness: 0.85, metalness: 0.04 },
  aac_block: { color: '#dcdde1', roughness: 0.95, metalness: 0.01 },
  stone_masonry: { color: '#7f8c8d', roughness: 0.88, metalness: 0.05 },
  eps_sandwich: { color: '#ecf0f1', roughness: 0.40, metalness: 0.35 },
  bamboo_composite: { color: '#c8b075', roughness: 0.70, metalness: 0.02 },
  roof_cgi_sheet: { color: '#7f8c8d', roughness: 0.30, metalness: 0.85 },
  roof_cgi_insulated: { color: '#34495e', roughness: 0.40, metalness: 0.70 },
  roof_concrete_slab: { color: '#95a5a6', roughness: 0.90, metalness: 0.05 },
  roof_bamboo_thatch: { color: '#8d704b', roughness: 0.95, metalness: 0.01 },
  roof_bipv_solar: { color: '#1b1464', roughness: 0.15, metalness: 0.95 },
  glazing_single: { color: '#81ecec', roughness: 0.10, metalness: 0.90, opacity: 0.65, transparent: true },
  glazing_double: { color: '#74b9ff', roughness: 0.10, metalness: 0.90, opacity: 0.60, transparent: true },
  glazing_low_e: { color: '#0984e3', roughness: 0.10, metalness: 0.90, opacity: 0.55, transparent: true },
  glazing_polycarb: { color: '#a29bfe', roughness: 0.20, metalness: 0.50, opacity: 0.70, transparent: true },
  door_timber_composite: { color: '#6d4c41', roughness: 0.65, metalness: 0.05 },
  floor_concrete_screed: { color: '#57606f', roughness: 0.92, metalness: 0.08 },
};

export const getMaterialProps = (matId: string): MaterialProperties => {
  return MATERIAL_PBR_MAP[matId] || { color: '#95a5a6', roughness: 0.85, metalness: 0.05 };
};
