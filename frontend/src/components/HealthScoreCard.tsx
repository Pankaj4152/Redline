import React, { useState } from 'react';
import { ShieldAlert, ChevronDown, ChevronUp, AlertCircle, Cpu, FileCode2, Layers, Wrench } from 'lucide-react';
import { SignalHealthReport, MetricScore } from '../types/schemas';

interface HealthScoreCardProps {
  report: SignalHealthReport;
  disclaimer: string;
}

export const HealthScoreCard: React.FC<HealthScoreCardProps> = ({ report, disclaimer }) => {
  const [expandedMetric, setExpandedMetric] = useState<string | null>('ai_solvability');

  const toggleMetric = (key: string) => {
    setExpandedMetric(expandedMetric === key ? null : key);
  };

  const getHealthColor = (score: number) => {
    if (score >= 65) return 'var(--accent-emerald)';
    if (score >= 45) return 'var(--accent-amber)';
    return 'var(--accent-coral)';
  };

  const metrics: Array<{ key: string; title: string; scoreObj: MetricScore; icon: React.ReactNode }> = [
    { key: 'ai_solvability', title: 'AI Solvability (Raw AI Prompt Vulnerability)', scoreObj: report.ai_solvability, icon: <Cpu size={18} color="var(--accent-coral)" /> },
    { key: 'reasoning_signal', title: 'Reasoning Signal Demanded', scoreObj: report.reasoning_signal, icon: <ShieldAlert size={18} color="var(--accent-primary)" /> },
    { key: 'repo_depth', title: 'Repository Context & Depth Required', scoreObj: report.repo_depth, icon: <FileCode2 size={18} color="var(--accent-cyan)" /> },
    { key: 'architectural_judgment', title: 'Architectural Judgment & Design Trade-offs', scoreObj: report.architectural_judgment, icon: <Layers size={18} color="var(--accent-amber)" /> },
    { key: 'verification_requirement', title: 'Edge-Case Verification Requirement', scoreObj: report.verification_requirement, icon: <Wrench size={18} color="var(--accent-emerald)" /> },
  ];

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      {/* Disclaimer Header Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', padding: '0.6rem 0.85rem', backgroundColor: 'rgba(6, 182, 212, 0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
        <AlertCircle size={18} color="var(--accent-cyan)" />
        <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          <strong>Heuristic Diagnostic Feedback:</strong> {disclaimer}
        </span>
      </div>

      {/* Main Score Gauge Header */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem', alignItems: 'center', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-card)', marginBottom: '1.5rem' }}>
        <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(0, 0, 0, 0.3)', borderRadius: 'var(--radius-md)', border: `1px solid ${getHealthColor(report.overall_health_score)}` }}>
          <div style={{ fontSize: '2.8rem', fontWeight: 800, color: getHealthColor(report.overall_health_score), lineHeight: 1 }}>
            {report.overall_health_score}
            <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>/100</span>
          </div>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
            Engineering Signal Health
          </div>
        </div>

        <div>
          <span className={`badge badge-${report.overall_health_score >= 65 ? 'low' : report.overall_health_score >= 45 ? 'medium' : 'high'}`} style={{ marginBottom: '0.5rem' }}>
            {report.verdict}
          </span>
          <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginTop: '0.25rem' }}>
            Diagnostic Assessment Health Summary
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {report.overall_health_score < 45
              ? 'This task presents HIGH AI delegation risk. A raw AI prompt can complete it without requiring candidate repository inspection.'
              : report.overall_health_score < 65
              ? 'This task presents MODERATE AI delegation risk. Consider adding explicit architectural constraints.'
              : 'This task presents STRONG engineering signal. It forces candidate architectural judgment and edge-case verification.'}
          </p>
        </div>
      </div>

      {/* 5-Dimension Metrics Accordion */}
      <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '1rem' }}>
        Evaluated Signal Dimensions & Evidence Attribution:
      </h4>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {metrics.map((m) => {
          const isExpanded = expandedMetric === m.key;
          return (
            <div key={m.key} style={{ backgroundColor: 'rgba(0, 0, 0, 0.25)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-card)', overflow: 'hidden' }}>
              <div
                onClick={() => toggleMetric(m.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.85rem 1rem',
                  cursor: 'pointer',
                  userSelect: 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                  {m.icon}
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{m.title}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ width: '80px', height: '6px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${m.scoreObj.score}%`, height: '100%', backgroundColor: getHealthColor(m.key === 'ai_solvability' ? 100 - m.scoreObj.score : m.scoreObj.score) }} />
                  </div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, minWidth: '32px', textAlign: 'right' }}>{m.scoreObj.score}</span>
                  {isExpanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
                </div>
              </div>

              {isExpanded && (
                <div style={{ padding: '0.85rem 1rem', backgroundColor: 'rgba(0, 0, 0, 0.4)', borderTop: '1px solid var(--border-card)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                    Repository Evidence & Evaluation Rationale:
                  </div>
                  <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                    {m.scoreObj.contributing_evidence.map((ev, i) => (
                      <li key={i} style={{ marginBottom: '0.25rem' }}>{ev}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
