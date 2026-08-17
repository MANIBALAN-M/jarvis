import React, { useEffect } from 'react';
import { FileText, Shield, Filter, RefreshCw } from 'lucide-react';
import { fetchAuditLogs } from '../../services/agentApi';
import { useAuditStore } from '../../stores/useAuditStore';
import { RiskLevel } from '../../types';

export const AuditLogView: React.FC = () => {
  const { auditLogs, filterRisk, setAuditLogs, setFilterRisk, isLoading, setIsLoading } = useAuditStore();

  const loadLogs = async () => {
    setIsLoading(true);
    const logs = await fetchAuditLogs(50);
    setAuditLogs(logs);
    setIsLoading(false);
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = auditLogs.filter((log) => {
    if (filterRisk === 'all') return true;
    return log.risk_level === filterRisk;
  });

  const getRiskBadgeClass = (risk: RiskLevel) => {
    switch (risk) {
      case 'low': return 'badge-low';
      case 'medium': return 'badge-medium';
      case 'high': return 'badge-high';
      case 'critical': return 'badge-critical';
      default: return 'badge-low';
    }
  };

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px' }}>Security Audit Trail</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            Immutable local audit log recording policy decisions and tool invocations.
          </p>
        </div>

        <button
          onClick={loadLogs}
          disabled={isLoading}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            padding: '8px 14px',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <RefreshCw size={14} className={isLoading ? 'animate-pulse-glow' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Filter size={15} color="var(--text-muted)" />
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Risk Filter:</span>
        {(['all', 'low', 'medium', 'high', 'critical'] as const).map((r) => (
          <button
            key={r}
            onClick={() => setFilterRisk(r)}
            style={{
              background: filterRisk === r ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              border: filterRisk === r ? '1px solid rgba(56, 189, 248, 0.5)' : '1px solid var(--border-color)',
              color: filterRisk === r ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: 600,
              textTransform: 'uppercase'
            }}
          >
            {r}
          </button>
        ))}
      </div>

      {/* Audit Log Table / Cards */}
      {filteredLogs.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <FileText size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
          <p>No audit events match the selected risk filter.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filteredLogs.map((log) => (
            <div key={log.event_id} className="glass-card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <Shield size={18} color="var(--accent-cyan)" />
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px', fontFamily: 'var(--font-mono)' }}>
                      {log.tool_id}
                    </span>
                    <span className={`badge ${getRiskBadgeClass(log.risk_level)}`} style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 700, textTransform: 'uppercase' }}>
                      {log.risk_level}
                    </span>
                    <span style={{
                      fontSize: '11px',
                      color: log.decision === 'allow' ? '#34d399' : log.decision === 'ask_user' ? '#fb923c' : '#f87171',
                      fontWeight: 700,
                      textTransform: 'uppercase'
                    }}>
                      [{log.decision}]
                    </span>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Event ID: {log.event_id}
                  </span>
                </div>
              </div>

              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {new Date(log.timestamp_ts * 1000).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
