/**
 * Video Generation Models Comparison Utilities
 * Survey Date: January 15, 2024
 */

export interface ModelSource {
  url: string;
  date: string;
  type: 'official' | 'news' | 'documentation' | 'repository' | 'paper' | 'model_hub' | 'official_blog';
}

export interface CameraMotionControl {
  supported: boolean;
  controls: string[];
  description: string;
}

export interface CharacterConsistency {
  supported: boolean;
  method: string;
  description: string;
}

export interface ReferenceFrames {
  supported: boolean;
  types: string[];
  description: string;
}

export interface TemporalControls {
  supported: boolean;
  features: string[];
  description: string;
}

export interface Controllability {
  camera_motion: CameraMotionControl;
  character_consistency: CharacterConsistency;
  reference_frames: ReferenceFrames;
  temporal_controls: TemporalControls;
}

export interface BenchmarkMetric {
  score: number;
  metric: string;
  description?: string;
}

export interface BenchmarkMetrics {
  instruction_following: BenchmarkMetric;
  temporal_consistency: BenchmarkMetric;
  [key: string]: BenchmarkMetric;
}

export interface CostLatency {
  pricing_model: string;
  cost_per_second: string;
  estimated_cost_range: string;
  generation_latency: string;
  notes?: string;
}

export interface SafetyProvenance {
  content_moderation: boolean;
  watermarking: boolean;
  provenance_tracking: boolean;
  c2pa_support: boolean;
  safety_features: string[];
}

export interface Capabilities {
  modes: string[];
  max_length_seconds: number;
  max_resolution: string;
  aspect_ratios: string[];
  api_availability: string;
  api_status: string;
  frame_rate: number;
}

export interface VideoGenerationModel {
  name: string;
  provider: string;
  category: 'commercial' | 'open-source';
  capabilities: Capabilities;
  controllability: Controllability;
  benchmark_metrics: BenchmarkMetrics;
  cost_latency: CostLatency;
  safety_provenance: SafetyProvenance;
  sources: ModelSource[];
  last_updated: string;
}

export interface ComparisonSummary {
  longest_video: {
    model: string;
    duration: number;
  };
  highest_resolution: {
    model: string;
    resolution: string;
  };
  fastest_generation: {
    model: string;
    latency: string;
  };
  most_affordable: {
    model: string;
    cost: string;
  };
  best_temporal_consistency: {
    model: string;
    score: number;
  };
  best_controllability: {
    model: string;
    features: string;
  };
  best_api_access: {
    models: string[];
    status: string;
  };
}

export interface SurveyMetadata {
  survey_date: string;
  total_models: number;
  categories: string[];
  verification_sources_minimum: number;
}

export interface VideoGenerationSurvey {
  survey_metadata: SurveyMetadata;
  models: VideoGenerationModel[];
  comparison_summary: ComparisonSummary;
}

/**
 * Comparison utilities
 */
export class ModelComparison {
  constructor(private survey: VideoGenerationSurvey) {}

  /**
   * Get models by category
   */
  getModelsByCategory(category: 'commercial' | 'open-source'): VideoGenerationModel[] {
    return this.survey.models.filter(m => m.category === category);
  }

  /**
   * Get models with production API
   */
  getProductionAPIModels(): VideoGenerationModel[] {
    return this.survey.models.filter(m => m.capabilities.api_status === 'production');
  }

  /**
   * Get models supporting specific mode
   */
  getModelsByMode(mode: string): VideoGenerationModel[] {
    return this.survey.models.filter(m => 
      m.capabilities.modes.some(availMode => 
        availMode.toLowerCase().includes(mode.toLowerCase())
      )
    );
  }

  /**
   * Get models with camera motion control
   */
  getModelsWithCameraControl(): VideoGenerationModel[] {
    return this.survey.models.filter(m => m.controllability.camera_motion.supported);
  }

  /**
   * Get models with character consistency
   */
  getModelsWithCharacterConsistency(): VideoGenerationModel[] {
    return this.survey.models.filter(m => m.controllability.character_consistency.supported);
  }

  /**
   * Get models with C2PA support
   */
  getModelsWithC2PA(): VideoGenerationModel[] {
    return this.survey.models.filter(m => m.safety_provenance.c2pa_support);
  }

  /**
   * Sort models by temporal consistency score
   */
  sortByTemporalConsistency(): VideoGenerationModel[] {
    return [...this.survey.models].sort(
      (a, b) => b.benchmark_metrics.temporal_consistency.score - a.benchmark_metrics.temporal_consistency.score
    );
  }

  /**
   * Sort models by instruction following score
   */
  sortByInstructionFollowing(): VideoGenerationModel[] {
    return [...this.survey.models].sort(
      (a, b) => b.benchmark_metrics.instruction_following.score - a.benchmark_metrics.instruction_following.score
    );
  }

  /**
   * Sort models by max video length
   */
  sortByMaxLength(): VideoGenerationModel[] {
    return [...this.survey.models].sort(
      (a, b) => b.capabilities.max_length_seconds - a.capabilities.max_length_seconds
    );
  }

  /**
   * Get models by minimum video length
   */
  getModelsByMinLength(minSeconds: number): VideoGenerationModel[] {
    return this.survey.models.filter(m => m.capabilities.max_length_seconds >= minSeconds);
  }

  /**
   * Get free/open-source models
   */
  getFreeModels(): VideoGenerationModel[] {
    return this.survey.models.filter(m => 
      m.cost_latency.pricing_model === 'free_open_source'
    );
  }

  /**
   * Filter models by aspect ratio support
   */
  getModelsByAspectRatio(aspectRatio: string): VideoGenerationModel[] {
    return this.survey.models.filter(m => 
      m.capabilities.aspect_ratios.includes(aspectRatio)
    );
  }

  /**
   * Get model statistics
   */
  getStatistics() {
    const models = this.survey.models;
    return {
      total_models: models.length,
      commercial_count: this.getModelsByCategory('commercial').length,
      open_source_count: this.getModelsByCategory('open-source').length,
      production_api_count: this.getProductionAPIModels().length,
      camera_control_count: this.getModelsWithCameraControl().length,
      c2pa_support_count: this.getModelsWithC2PA().length,
      avg_temporal_consistency: models.reduce(
        (sum, m) => sum + m.benchmark_metrics.temporal_consistency.score, 0
      ) / models.length,
      avg_instruction_following: models.reduce(
        (sum, m) => sum + m.benchmark_metrics.instruction_following.score, 0
      ) / models.length,
      max_video_length: Math.max(...models.map(m => m.capabilities.max_length_seconds)),
      min_video_length: Math.min(...models.map(m => m.capabilities.max_length_seconds))
    };
  }

  /**
   * Get detailed comparison for specific models
   */
  compareModels(modelNames: string[]): VideoGenerationModel[] {
    return this.survey.models.filter(m => 
      modelNames.some(name => m.name.toLowerCase().includes(name.toLowerCase()))
    );
  }

  /**
   * Get recommendation by use case
   */
  getRecommendationByUseCase(useCase: string): VideoGenerationModel[] {
    const lowerUseCase = useCase.toLowerCase();
    
    if (lowerUseCase.includes('professional') || lowerUseCase.includes('film')) {
      return this.compareModels(['Runway Gen-3', 'Veo 3', 'Sora']);
    }
    
    if (lowerUseCase.includes('social') || lowerUseCase.includes('content creation')) {
      return this.compareModels(['Luma Dream Machine', 'Pika']);
    }
    
    if (lowerUseCase.includes('long') || lowerUseCase.includes('narrative')) {
      return this.getModelsByMinLength(60);
    }
    
    if (lowerUseCase.includes('research') || lowerUseCase.includes('development')) {
      return this.getFreeModels();
    }
    
    if (lowerUseCase.includes('budget')) {
      return [...this.getFreeModels(), ...this.compareModels(['Kling', 'Stability AI'])];
    }
    
    return [];
  }

  /**
   * Export comparison table data
   */
  exportComparisonTable(): Array<{
    name: string;
    provider: string;
    category: string;
    max_length: number;
    resolution: string;
    api_status: string;
    temporal_consistency: number;
    instruction_following: number;
  }> {
    return this.survey.models.map(m => ({
      name: m.name,
      provider: m.provider,
      category: m.category,
      max_length: m.capabilities.max_length_seconds,
      resolution: m.capabilities.max_resolution,
      api_status: m.capabilities.api_status,
      temporal_consistency: m.benchmark_metrics.temporal_consistency.score,
      instruction_following: m.benchmark_metrics.instruction_following.score
    }));
  }
}

/**
 * Parse resolution string to width and height
 */
export function parseResolution(resolution: string): { width: number; height: number } | null {
  const match = resolution.match(/(\d+)x(\d+)/);
  if (!match) return null;
  return {
    width: parseInt(match[1]),
    height: parseInt(match[2])
  };
}

/**
 * Calculate total pixels from resolution string
 */
export function getTotalPixels(resolution: string): number {
  const parsed = parseResolution(resolution);
  if (!parsed) return 0;
  return parsed.width * parsed.height;
}

/**
 * Compare resolutions
 */
export function compareResolutions(res1: string, res2: string): number {
  return getTotalPixels(res1) - getTotalPixels(res2);
}

/**
 * Format cost range for display
 */
export function formatCostRange(costLatency: CostLatency): string {
  if (costLatency.pricing_model === 'free_open_source') {
    return 'Free (hardware costs only)';
  }
  return costLatency.estimated_cost_range;
}

/**
 * Check if model is production ready
 */
export function isProductionReady(model: VideoGenerationModel): boolean {
  const productionStatuses = ['production', 'public_api', 'api_available'];
  return productionStatuses.includes(model.capabilities.api_status);
}

/**
 * Get controllability score (0-4 based on supported features)
 */
export function getControllabilityScore(model: VideoGenerationModel): number {
  let score = 0;
  if (model.controllability.camera_motion.supported) score++;
  if (model.controllability.character_consistency.supported) score++;
  if (model.controllability.reference_frames.supported) score++;
  if (model.controllability.temporal_controls.supported) score++;
  return score;
}

/**
 * Get safety score (0-4 based on safety features)
 */
export function getSafetyScore(model: VideoGenerationModel): number {
  let score = 0;
  if (model.safety_provenance.content_moderation) score++;
  if (model.safety_provenance.watermarking) score++;
  if (model.safety_provenance.provenance_tracking) score++;
  if (model.safety_provenance.c2pa_support) score++;
  return score;
}
