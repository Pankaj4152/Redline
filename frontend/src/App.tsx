import { useState } from 'react';
import { Header } from './components/Header';
import { AssessmentForm } from './components/AssessmentForm';
import { HealthScoreCard } from './components/HealthScoreCard';
import { CandidateSimulations } from './components/CandidateSimulations';
import { TaskUpgradeCard } from './components/TaskUpgradeCard';
import { AnalysisRequest, FullAssessmentResult } from './types/schemas';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FullAssessmentResult | null>(null);

  const handleAnalyze = async (request: AnalysisRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `API request failed with status ${response.status}`);
      }

      const data: FullAssessmentResult = await response.json();
      setResult(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during assessment red-teaming.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 1.5rem 3rem 1.5rem' }}>
      <Header />

      <main>
        {/* Assessment Red-Teaming Input Form */}
        <AssessmentForm onSubmit={handleAnalyze} isLoading={isLoading} />

        {/* Error Banner */}
        {error && (
          <div
            className="glass-card"
            style={{
              padding: '1rem 1.25rem',
              marginBottom: '2rem',
              borderColor: 'var(--accent-coral)',
              backgroundColor: 'rgba(244, 63, 94, 0.1)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}
          >
            <AlertCircle size={20} color="var(--accent-coral)" />
            <div style={{ fontSize: '0.875rem', color: 'var(--accent-coral)' }}>
              <strong>Analysis Error:</strong> {error}
            </div>
          </div>
        )}

        {/* Loading Spinner Indicator */}
        {isLoading && (
          <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', marginBottom: '2rem' }}>
            <RefreshCw size={36} color="var(--accent-primary)" className="spin" style={{ animation: 'spin 1.5s linear infinite', marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
              Red-Teaming Assessment Task...
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Parsing repository AST outlines → Simulating candidate profile strategies → Evaluating diagnostic signal evidence...
            </p>
            <style>{`
              @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        )}

        {/* Results Dashboard */}
        {result && !isLoading && (
          <div>
            {/* 1. Diagnostic Health Score Card */}
            <HealthScoreCard report={result.report} disclaimer={result.diagnostic_disclaimer} />

            {/* 2. Candidate Strategy Profile Simulations */}
            <CandidateSimulations simulations={result.simulations} />

            {/* 3. Recommended Task Upgrade */}
            <TaskUpgradeCard recommendation={result.recommendations} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
