import React, { useState } from 'react';
import { ArrowUpRight, Copy, Check, Sparkles, AlertCircle } from 'lucide-react';
import { TaskRecommendation } from '../types/schemas';

interface TaskUpgradeCardProps {
  recommendation: TaskRecommendation;
}

export const TaskUpgradeCard: React.FC<TaskUpgradeCardProps> = ({ recommendation }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(recommendation.upgraded_task);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={20} color="var(--accent-amber)" />
          Recommended Task Upgrade
        </h3>
        <button className="btn-primary" onClick={handleCopy} style={{ fontSize: '0.825rem', padding: '0.4rem 0.85rem' }}>
          {copied ? <Check size={16} /> : <Copy size={16} />}
          {copied ? 'Copied to Clipboard!' : 'Copy Upgraded Task'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
        {/* Original Task */}
        <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.3)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-card)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Original Candidate Task Prompt:
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: '1.5' }}>
            "{recommendation.original_task}"
          </p>
        </div>

        {/* Upgraded Task */}
        <div style={{ backgroundColor: 'rgba(99, 102, 241, 0.08)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-cyan)', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <ArrowUpRight size={14} />
            Upgraded High-Signal Prompt:
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500, lineHeight: '1.5' }}>
            "{recommendation.upgraded_task}"
          </p>
        </div>
      </div>

      {/* Rationale & Added Constraints */}
      <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.25)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-card)' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <AlertCircle size={14} color="var(--accent-amber)" />
          Upgrade Rationale & Mitigated Risks:
        </div>
        <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
          {recommendation.rationale}
        </p>

        {recommendation.added_constraints.length > 0 && (
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              Added Architectural Constraints:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {recommendation.added_constraints.map((c, i) => (
                <span key={i} style={{ fontSize: '0.775rem', padding: '0.2rem 0.6rem', backgroundColor: 'rgba(6, 182, 212, 0.12)', border: '1px solid rgba(6, 182, 212, 0.25)', borderRadius: '9999px', color: 'var(--accent-cyan)' }}>
                  + {c}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
