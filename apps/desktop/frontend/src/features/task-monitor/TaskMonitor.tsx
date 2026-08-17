import React, { useState } from 'react';
import { Activity, CheckCircle2, XCircle, Clock, AlertTriangle, ChevronDown, ChevronRight, Shield } from 'lucide-react';
import { useTaskStore } from '../../stores/useTaskStore';
import { RiskLevel, TaskStep } from '../../types';

export const TaskMonitor: React.FC = () => {
  const { tasks, activeTask } = useTaskStore();
  const [expandedStepId, setExpandedStepId] = useState<string | null>(null);

  const getRiskBadgeClass = (risk: RiskLevel) => {
    switch (risk) {
      case 'low': return 'badge-low';
      case 'medium': return 'badge-medium';
      case 'high': return 'badge-high';
      case 'critical': return 'badge-critical';
      default: return 'badge-low';
    }
  };

  const getStatusIcon = (status: TaskStep['status']) => {
    switch (status) {
      case 'success': return <CheckCircle2 size={16} color="#34d399" />;
      case 'failed': return <XCircle size={16} color="#f87171" />;
      case 'blocked': return <XCircle size={16} color="#f87171" />;
      case 'awaiting_approval': return <AlertTriangle size={16} color="#fb923c" className="animate-pulse-glow" />;
      case 'running': return <Activity size={16} color="var(--accent-cyan)" className="animate-pulse-glow" />;
      default: return <Clock size={16} color="var(--text-muted)" />;
    }
  };

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px' }}>Task Execution DAG</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            Real-time step-by-step tool plan execution and security policy evaluation.
          </p>
        </div>
      </div>

      {!activeTask || activeTask.steps.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Activity size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
          <p>No active execution plan. Execute a command in the Command Center to populate steps.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Plan Header */}
          <div className="glass-card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent-cyan)', fontWeight: 700, letterSpacing: '1px' }}>
                Goal Summary
              </span>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginTop: '2px' }}>{activeTask.goal_summary}</h3>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Status: </span>
              <span style={{ fontWeight: 700, fontSize: '13px', textTransform: 'uppercase', color: activeTask.status === 'completed' ? '#34d399' : 'var(--accent-cyan)' }}>
                {activeTask.status}
              </span>
            </div>
          </div>

          {/* Steps Timeline */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {activeTask.steps.map((step, index) => {
              const isExpanded = expandedStepId === step.step_id;
              return (
                <div key={step.step_id} className="glass-card" style={{ padding: '16px' }}>
                  <div
                    onClick={() => setExpandedStepId(isExpanded ? null : step.step_id)}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '12px',
                        fontWeight: 700,
                        fontFamily: 'var(--font-mono)'
                      }}>
                        {index + 1}
                      </span>
                      {getStatusIcon(step.status)}
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontWeight: 600, fontSize: '14px', fontFamily: 'var(--font-mono)' }}>
                            {step.tool_id}
                          </span>
                          <span className={`badge ${getRiskBadgeClass(step.risk_level)}`} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 700, textTransform: 'uppercase' }}>
                            {step.risk_level} Risk
                          </span>
                        </div>
                        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                          {step.description}
                        </p>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                    </div>
                  </div>

                  {/* Expanded Step Details */}
                  {isExpanded && (
                    <div style={{ marginTop: '14px', paddingTop: '14px', borderTop: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ fontSize: '12px' }}>
                        <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Input Parameters: </span>
                        <pre style={{
                          background: 'rgba(0, 0, 0, 0.4)',
                          padding: '10px',
                          borderRadius: '6px',
                          marginTop: '4px',
                          fontFamily: 'var(--font-mono)',
                          fontSize: '12px',
                          color: '#38bdf8',
                          overflowX: 'auto'
                        }}>
                          {JSON.stringify(step.tool_input, null, 2)}
                        </pre>
                      </div>

                      {step.output_summary && (
                        <div style={{ fontSize: '12px' }}>
                          <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Output Summary: </span>
                          <p style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '10px', borderRadius: '6px', marginTop: '4px', color: 'var(--text-primary)' }}>
                            {step.output_summary}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
