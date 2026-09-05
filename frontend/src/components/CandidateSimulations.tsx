import React from 'react';
import { Bot, UserCheck, Code, AlertTriangle, FileCode } from 'lucide-react';
import { SimulationProfileResult } from '../types/schemas';

interface CandidateSimulationsProps {
  simulations: SimulationProfileResult[];
}

export const CandidateSimulations: React.FC<CandidateSimulationsProps> = ({ simulations }) => {
  const getProfileIcon = (profile: string) => {
    if (profile.includes('AI-Dependent')) return <Bot size={22} color="var(--accent-coral)" />;
    if (profile.includes('Naive')) return <UserCheck size={22} color="var(--accent-amber)" />;
    return <Code size={22} color="var(--accent-emerald)" />;
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Bot size={20} color="var(--accent-primary)" />
        Simulated AI-Assisted Candidate Profiles
      </h3>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
        Redline evaluates task vulnerability by comparing 3 simulated candidate solving strategies:
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {simulations.map((sim, idx) => (
          <div
            key={idx}
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-card)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              {/* Profile Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.85rem' }}>
                {getProfileIcon(sim.profile)}
                <div>
                  <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{sim.profile}</h4>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    AI Delegation Level: <strong style={{ color: 'var(--accent-cyan)' }}>{sim.estimated_delegation}</strong>
                  </span>
                </div>
              </div>

              {/* Reasoning Summary */}
              <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: '1.4' }}>
                {sim.reasoning_summary}
              </p>

              {/* Inspected Files */}
              {sim.inspected_files.length > 0 && (
                <div style={{ marginBottom: '0.85rem' }}>
                  <div style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <FileCode size={12} />
                    Inspected Files:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {sim.inspected_files.map((f, i) => (
                      <span key={i} className="font-mono" style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', color: 'var(--text-secondary)' }}>
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {/* Reused Abstractions */}
              {sim.abstractions_reused && sim.abstractions_reused.length > 0 && (
                <div style={{ marginBottom: '0.85rem' }}>
                  <div style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--accent-emerald)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                    Reused Code Conventions:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {sim.abstractions_reused.map((abs, aIdx) => (
                      <span key={aIdx} style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '3px', color: 'var(--accent-emerald)' }}>
                        {abs}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Edge Cases Tested */}
              {sim.edge_cases_tested && sim.edge_cases_tested.length > 0 && (
                <div style={{ marginBottom: '0.85rem' }}>
                  <div style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--accent-cyan)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                    Edge-Case Verification:
                  </div>
                  <ul style={{ paddingLeft: '1rem', fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0 }}>
                    {sim.edge_cases_tested.map((test, tIdx) => (
                      <li key={tIdx}>{test}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Missed Risks & Likelihood */}
            <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '0.75rem', marginTop: '0.5rem' }}>
              <div style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--accent-coral)', textTransform: 'uppercase', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <AlertTriangle size={12} />
                Missed Risks / Vulnerabilities:
              </div>
              {sim.missed_risks.length === 0 ? (
                <span style={{ fontSize: '0.78rem', color: 'var(--accent-emerald)', fontWeight: 500 }}>
                  ✓ High-level trade-offs evaluated
                </span>
              ) : (
                <ul style={{ paddingLeft: '1rem', fontSize: '0.78rem', color: 'var(--text-secondary)', margin: 0 }}>
                  {sim.missed_risks.map((risk, rIdx) => (
                    <li key={rIdx}>{risk}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
