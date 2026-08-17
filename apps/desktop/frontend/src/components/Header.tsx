import React, { useEffect, useState } from 'react';
import { Shield, Wifi, WifiOff, Command, Minus, Square, X } from 'lucide-react';
import { checkAgentHealth } from '../services/agentApi';
import { toggleWindowVisibility } from '../services/tauriIpc';
import { AgentHealth } from '../types';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = () => {
  const [health, setHealth] = useState<AgentHealth | null>(null);

  useEffect(() => {
    const check = async () => {
      const h = await checkAgentHealth();
      setHealth(h);
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const isOnline = health?.status === 'healthy';

  return (
    <header className="glass-panel" style={{
      height: '52px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 16px',
      borderBottom: '1px solid var(--border-color)',
      zIndex: 50
    }}>
      {/* Brand & Connection Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '4px 10px',
          background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(139, 92, 246, 0.15))',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          borderRadius: 'var(--radius-sm)'
        }}>
          <Shield size={18} color="var(--accent-cyan)" />
          <span style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '0.5px' }}>
            JARVIS <span style={{ color: 'var(--accent-cyan)', fontSize: '11px', fontWeight: 500 }}>v0.2.0</span>
          </span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: isOnline ? '#34d399' : '#f87171',
          background: isOnline ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          padding: '3px 8px',
          borderRadius: '12px',
          border: `1px solid ${isOnline ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
        }}>
          {isOnline ? <Wifi size={13} /> : <WifiOff size={13} />}
          <span>{isOnline ? 'Agent Connected (127.0.0.1:8765)' : 'Agent Disconnected'}</span>
        </div>
      </div>

      {/* Global Shortcut Badge & Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          color: 'var(--text-secondary)',
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '4px 10px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-color)',
          fontFamily: 'var(--font-mono)'
        }}>
          <Command size={12} />
          <span>Ctrl + Space</span>
        </div>

        {/* Window Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => toggleWindowVisibility()}
            title="Minimize to Tray"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Minus size={15} />
          </button>
          <button
            title="Maximize"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Square size={13} />
          </button>
          <button
            onClick={() => toggleWindowVisibility()}
            title="Hide Window"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <X size={15} />
          </button>
        </div>
      </div>
    </header>
  );
};
