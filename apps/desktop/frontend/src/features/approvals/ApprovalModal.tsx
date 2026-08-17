import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle, Lock, AlertTriangle } from 'lucide-react';
import { approveTaskStep, rejectTaskStep } from '../../services/agentApi';
import { useApprovalStore } from '../../stores/useApprovalStore';
import { useTaskStore } from '../../stores/useTaskStore';

export const ApprovalModal: React.FC = () => {
  const { activeApprovalModal, removePendingApproval, closeApprovalModal } = useApprovalStore();
  const setLatestResult = useTaskStore((s) => s.setLatestResult);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!activeApprovalModal) return null;

  const { taskId, step, reason } = activeApprovalModal;

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      const res = await approveTaskStep(taskId, step.step_id);
      setLatestResult(res);
      removePendingApproval(taskId, step.step_id);
    } catch (e: any) {
      alert(`Approval error: ${e.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      const res = await rejectTaskStep(taskId, step.step_id);
      setLatestResult(res);
      removePendingApproval(taskId, step.step_id);
    } catch (e: any) {
      alert(`Rejection error: ${e.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '520px',
        width: '100%',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        border: '1px solid rgba(245, 158, 11, 0.4)',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.6)',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            padding: '10px',
            background: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: 'var(--radius-md)'
          }}>
            <ShieldAlert size={24} color="#f59e0b" />
          </div>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f59e0b' }}>
              Action Approval Required
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Security Policy Gate • Human-in-the-Loop Gate
            </p>
          </div>
        </div>

        {/* Action Details */}
        <div style={{ background: 'rgba(0, 0, 0, 0.4)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Target Tool:</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '13px', color: 'var(--accent-cyan)' }}>
              {step.tool_id}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Risk Level:</span>
            <span className="badge badge-medium" style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase' }}>
              {step.risk_level} Risk
            </span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-primary)', marginBottom: '12px', lineHeight: '1.4' }}>
            {reason || step.description}
          </p>

          {step.tool_input && (
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>Arguments:</span>
              <pre style={{
                background: 'rgba(0, 0, 0, 0.5)',
                padding: '10px',
                borderRadius: '6px',
                marginTop: '4px',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: '#e2e8f0',
                overflowX: 'auto'
              }}>
                {JSON.stringify(step.tool_input, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Notice */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
          <Lock size={14} color="var(--accent-cyan)" />
          <span>Approving generates a cryptographically signed HMAC token for execution.</span>
        </div>

        {/* Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={handleReject}
            disabled={isSubmitting}
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '10px 20px',
              borderRadius: 'var(--radius-md)',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              fontWeight: 600,
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <XCircle size={16} />
            <span>Deny & Halt</span>
          </button>

          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            style={{
              background: 'linear-gradient(135deg, #10b981, #059669)',
              border: 'none',
              color: '#fff',
              padding: '10px 20px',
              borderRadius: 'var(--radius-md)',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              fontWeight: 600,
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <CheckCircle size={16} />
            <span>Approve & Execute</span>
          </button>
        </div>
      </div>
    </div>
  );
};
