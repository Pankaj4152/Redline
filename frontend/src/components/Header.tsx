import React from 'react';
import { Target, ShieldCheck } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '1.5rem 0',
      marginBottom: '2rem',
      borderBottom: '1px solid var(--border-card)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          background: 'linear-gradient(135deg, var(--accent-coral), var(--accent-primary))',
          padding: '0.6rem',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Target size={28} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h1 style={{ fontSize: '1.5rem', color: 'var(--text-primary)' }}>Redline</h1>
            <span className="badge badge-disclaimer">Pre-Flight Assessment Red-Teamer</span>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Stress-test AI coding assessments before assigning them to candidates.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <ShieldCheck size={16} color="var(--accent-emerald)" />
        <span>Static AST & LLM Strategy Engine</span>
      </div>
    </header>
  );
};
