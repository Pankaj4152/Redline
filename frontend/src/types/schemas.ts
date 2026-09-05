export type LevelEnum = 'HIGH' | 'MEDIUM' | 'LOW';

export type CandidateProfileEnum = 
  | 'AI-Dependent Engineer'
  | 'Naive AI-Assisted Engineer'
  | 'Strong AI-Native Engineer';

export interface AnalysisRequest {
  repo_url: string;
  branch?: string;
  task_description: string;
}

export interface RepoSymbol {
  name: string;
  symbol_type: string;
  file_path: string;
}

export interface RepoContextSummary {
  repo_name: string;
  total_files: number;
  file_tree: string[];
  detected_routes: string[];
  key_symbols: RepoSymbol[];
}

export interface MetricScore {
  score: number;
  level: LevelEnum;
  contributing_evidence: string[];
}

export interface SignalHealthReport {
  overall_health_score: number;
  verdict: string;
  ai_solvability: MetricScore;
  reasoning_signal: MetricScore;
  repo_depth: MetricScore;
  architectural_judgment: MetricScore;
  verification_requirement: MetricScore;
}

export interface SimulationProfileResult {
  profile: CandidateProfileEnum;
  success_likelihood: LevelEnum;
  estimated_delegation: string;
  reasoning_summary: string;
  missed_risks: string[];
  inspected_files: string[];
}

export interface TaskRecommendation {
  original_task: string;
  upgraded_task: string;
  rationale: string;
  added_constraints: string[];
}

export interface FullAssessmentResult {
  job_id: string;
  status: string;
  diagnostic_disclaimer: string;
  repo_summary?: RepoContextSummary;
  report: SignalHealthReport;
  simulations: SimulationProfileResult[];
  recommendations: TaskRecommendation;
}
