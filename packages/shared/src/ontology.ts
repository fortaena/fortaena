export type Shape =
  | 'LIGHT'
  | 'SPHERE'
  | 'TRIANGLE'
  | 'DISC'
  | 'CIGAR'
  | 'OVAL'
  | 'CHEVRON'
  | 'DELTA'
  | 'OTHER'
  | 'UNKNOWN';

export type SourceType = 'NUFORC' | 'MUFON' | 'EOC' | 'GOV' | 'REDDIT' | 'YOUTUBE' | 'CITIZEN';

export const TIER = [1, 2, 3, 4] as const;
export type Tier = typeof TIER[number];

export const SHAPE_CERTAINTY = ['HIGH', 'MEDIUM', 'LOW'] as const;
export type ShapeCertainty = typeof SHAPE_CERTAINTY[number];
