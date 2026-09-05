import React, { useState } from 'react';
import { Play, Sparkles, FolderGit2, FileText } from 'lucide-react';
import { AnalysisRequest } from '../types/schemas';

interface AssessmentFormProps {
  onSubmit: (request: AnalysisRequest) => void;
  isLoading: boolean;
}

const PRESETS = [
  {
    name: 'Weak Signal: FastAPI CSV Export',
    repo: '.',
    task: 'Add a CSV export endpoint for user transaction history.'
  },
  {
    name: 'Strong Signal: Streaming RAM & Middleware',
    repo: '.',
    task: 'Add a CSV export endpoint for user transaction history. Ensure the implementation streams response data to stay under 50MB RAM usage and preserves existing custom API rate-limiting middleware contracts.'
  },
  {
    name: 'Sample Public GitHub Repo',
    repo: 'https://github.com/fastapi/fastapi',
    task: 'Add a custom OAuth2 token revocation endpoint supporting async Redis caching.'
  }
];

export const AssessmentForm: React.FC<AssessmentFormProps> = ({ onSubmit, isLoading }) => {
  const [repoUrl, setRepoUrl] = useState('.');
  const [branch, setBranch] = useState('main');
  const [taskDescription, setTaskDescription] = useState('Add a CSV export endpoint for user transaction history.');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl.trim() || !taskDescription.trim()) return;
    onSubmit({
      repo_url: repoUrl.trim(),
      branch: branch.trim() || 'main',
      task_description: taskDescription.trim()
    });
  };

  const handleSelectPreset = (preset: typeof PRESETS[0]) => {
    setRepoUrl(preset.repo);
    setTaskDescription(preset.task);
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FolderGit2 size={20} color="var(--accent-primary)" />
          Assessment Red-Teaming Input
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={16} color="var(--accent-amber)" />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Quick Presets:</span>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="btn-secondary"
              onClick={() => handleSelectPreset(p)}
              style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
            >
              {p.name.split(':')[0]}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              GitHub Repository URL or Local Directory Path
            </label>
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="e.g. https://github.com/org/repo or ."
              required
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-card)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.9rem'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Branch
            </label>
            <input
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-card)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.9rem'
              }}
            />
          </div>
        </div>

        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            <FileText size={14} style={{ display: 'inline', marginRight: '4px' }} />
            Proposed Candidate Coding Task Description
          </label>
          <textarea
            value={taskDescription}
            onChange={(e) => setTaskDescription(e.target.value)}
            rows={3}
            placeholder="Describe the proposed candidate task..."
            required
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--border-card)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-sans)',
              fontSize: '0.9rem',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="btn-primary" disabled={isLoading}>
            <Play size={18} />
            {isLoading ? 'Red-Teaming Assessment...' : 'Run Red-Team Analysis'}
          </button>
        </div>
      </form>
    </div>
  );
};
