import React from 'react';
import { Terminal, Activity, ShieldAlert, FileText, Settings as SettingsIcon } from 'lucide-react';
import { useApprovalStore } from '../stores/useApprovalStore';

export type NavTab = 'command' | 'tasks' | 'approvals' | 'audit' | 'settings';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const pendingApprovals = useApprovalStore((s) => s.pendingApprovals);
  const pendingCount = pendingApprovals.length;

  const navItems: { id: NavTab; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: 'command', label: 'Command Center', icon: <Terminal size={18} /> },
    { id: 'tasks', label: 'Task Monitor', icon: <Activity size={18} /> },
    { id: 'approvals', label: 'Approvals Gate', icon: <ShieldAlert size={18} />, badge: pendingCount },
    { id: 'audit', label: 'Security Audit', icon: <FileText size={18} /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon size={18} /> },
  ];

  return (
    <aside className="glass-panel" style={{
      width: '210px',
      height: 'calc(100vh - 52px)',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px 10px',
      borderRight: '1px solid var(--border-color)'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: isActive
                  ? 'linear-gradient(90deg, rgba(56, 189, 248, 0.15), rgba(59, 130, 246, 0.1))'
                  : 'transparent',
                color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                border: isActive ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid transparent',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: isActive ? 600 : 400,
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {item.icon}
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span style={{
                  background: 'var(--status-high)',
                  color: '#fff',
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '10px'
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </aside>
  );
};
