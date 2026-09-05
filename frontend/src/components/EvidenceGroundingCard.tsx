import React from 'react';
import { Database, CheckCircle2, XCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { EvidenceGroundingChain, RepositoryFactMatrix } from '../types/schemas';

interface EvidenceGroundingCardProps {
  groundingChain?: EvidenceGroundingChain;
  factMatrix?: RepositoryFactMatrix;
  artificialComplexityFlag?: boolean;
  complexityRationale?: string;
}

export const EvidenceGroundingCard: React.FC<EvidenceGroundingCardProps> = ({
  groundingChain,
  factMatrix,
  artificialComplexityFlag,
  complexityRationale,
}) => {
  if (!groundingChain && !factMatrix && !artificialComplexityFlag) return null;

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem', border: artificialComplexityFlag ? '1px solid rgba(244, 63, 94, 0.4)' : undefined }}>
      {/* Artificial Complexity Banner */}
      {artificialComplexityFlag && (
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', padding: '0.85rem 1rem', backgroundColor: 'rgba(244, 63, 94, 0.12)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(244, 63, 94, 0.3)', marginBottom: '1.25rem' }}>
          <AlertTriangle size={22} color="var(--accent-coral)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-coral)', margin: 0 }}>
              Artificial Complexity Warning
            </h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0 0' }}>
              {complexityRationale || 'The task introduces ungrounded architectural constraints not supported by existing repository code structure.'}
            </p>
          </div>
        </div>
      )}

      {/* Card Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-card)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={20} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            Repository Evidence & Grounding Matrix
          </h3>
        </div>
        {groundingChain?.confidence_rating && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.25rem 0.6rem', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
            <ShieldCheck size={14} />
            Grounding Confidence: {groundingChain.confidence_rating}
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        {/* Column 1: Observed Repository Facts */}
        <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.25)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-card)' }}>
          <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--accent-emerald)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <CheckCircle2 size={16} /> Observed Code Abstractions
          </h4>
          <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {(factMatrix?.observed_abstractions || groundingChain?.repo_facts || ['FastAPI Route Handler', 'Pydantic Data Validation']).map((fact, idx) => (
              <li key={idx} style={{ lineHeight: '1.4' }}>{fact}</li>
            ))}
          </ul>
        </div>

        {/* Column 2: Forbidden / Absent Abstractions */}
        <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.25)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-card)' }}>
          <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--accent-coral)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <XCircle size={16} /> Forbidden / Absent Abstractions
          </h4>
          <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {(factMatrix?.absent_abstractions || groundingChain?.forbidden_upgrades || ['NO Response Data Streaming', 'NO API Rate-Limiting Middleware']).map((absent, idx) => (
              <li key={idx} style={{ lineHeight: '1.4', color: 'rgba(255, 255, 255, 0.65)' }}>{absent}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Allowed Grounded Upgrades Chain */}
      {groundingChain && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px dashed var(--border-card)' }}>
          <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--accent-cyan)', marginBottom: '0.5rem' }}>
            Grounding Rules & Task Implications
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Task Implications:</span>
              <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {groundingChain.task_implications.map((imp, i) => (
                  <li key={i}>{imp}</li>
                ))}
              </ul>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Allowed Task Upgrades:</span>
              <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>
                {groundingChain.allowed_upgrades.map((up, i) => (
                  <li key={i}>{up}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
