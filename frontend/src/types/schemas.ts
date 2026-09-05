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

export interface RepositoryFactMatrix {
  observed_abstractions: string[];
  absent_abstractions: string[];
}

export interface RepoContextSummary {
  repo_name: string;
  total_files: number;
  file_tree: string[];
  detected_routes: string[];
  key_symbols: RepoSymbol[];
  fact_matrix?: RepositoryFactMatrix;
}

export interface EvidenceGroundingChain {
  repo_facts: string[];
  task_implications: string[];
  allowed_upgrades: string[];
  forbidden_upgrades: string[];
  confidence_rating: string;
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
  abstractions_reused?: string[];
  edge_cases_tested?: string[];
}

export interface TaskRecommendation {
  original_task: string;
  upgraded_task: string;
  rationale: string;
  added_constraints: string[];
  grounding_chain?: EvidenceGroundingChain;
}

export interface FullAssessmentResult {
  job_id: string;
  status: string;
  diagnostic_disclaimer: string;
  repo_summary?: RepoContextSummary;
  report: SignalHealthReport;
  simulations: SimulationProfileResult[];
  recommendations: TaskRecommendation;
  evidence_grounding?: EvidenceGroundingChain;
  artificial_complexity_flag?: boolean;
  complexity_rationale?: string;
  is_fallback?: boolean;
  fallback_reason?: string;
}
