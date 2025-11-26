export interface Statistic {
  id: string;
  name: string;
  value: number;
  unit?: string;
  visualization_type: 'bar' | 'line' | 'pie' | 'gauge';
}

export interface DesignSpecification {
  background_color: string;
  foreground_color_1: string;
  foreground_color_2: string;
  theme_name?: string;
}

export interface DocumentGenerationRequest {
  description: string;
  length: number;
  document_type: 'formal' | 'infographic' | 'invoice';
  use_watermark: boolean;  // Only applicable for formal documents with logo
  statistics: Statistic[];
  design_spec: DesignSpecification;
  logo?: File;
}

export interface GenerationJobResponse {
  job_id: string;
  status: string;
  message: string;
  estimated_time_seconds: number;
}

export interface JobStatusResponse {
  job_id: string;
  document_id?: string;
  status: string;
  progress: number;
  current_step: string;
  error_message?: string;
}

export interface DocumentResponse {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  pdf_url?: string;
}

export interface ColorTheme {
  name: string;
  background: string;
  foreground1: string;
  foreground2: string;
}

export const COLOR_THEMES: ColorTheme[] = [
  {
    name: 'Ocean Blue',
    background: '#FFFFFF',
    foreground1: '#2563EB',
    foreground2: '#06B6D4',
  },
  {
    name: 'Corporate Red',
    background: '#FFFFFF',
    foreground1: '#DC2626',
    foreground2: '#F97316',
  },
  {
    name: 'Forest Green',
    background: '#FFFFFF',
    foreground1: '#059669',
    foreground2: '#14B8A6',
  },
  {
    name: 'Royal Purple',
    background: '#FFFFFF',
    foreground1: '#7C3AED',
    foreground2: '#EC4899',
  },
  {
    name: 'Sunset Orange',
    background: '#FFFFFF',
    foreground1: '#EA580C',
    foreground2: '#EAB308',
  },
];
