import React from 'react';
import { Settings, Server, Shield, Key, Cpu, HardDrive } from 'lucide-react';
import { useSettingsStore } from '../../stores/useSettingsStore';

export const SettingsView: React.FC = () => {
  const {
    agentUrl,
    autoApproveLowRisk,
    globalHotkey,
    selectedModel,
    setAgentUrl,
    setAutoApproveLowRisk,
    setGlobalHotkey,
    setSelectedModel,
  } = useSettingsStore();

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px', height: '100%', overflowY: 'auto', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px' }}>Application & Agent Settings</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
          Configure local agent runtime connection, security policies, and AI reasoning models.
        </p>
      </div>

      {/* Local Agent Connection */}
      <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Server size={20} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Local Runtime Connection</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Agent Endpoint URL (FastAPI)</label>
          <input
            type="text"
            value={agentUrl}
            onChange={(e) => setAgentUrl(e.target.value)}
            style={{
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px'
            }}
          />
        </div>
      </div>

      {/* Security & Risk Policy Settings */}
      <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Shield size={20} color="#f59e0b" />
          <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Policy & Permission Gates</h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '13px' }}>Auto-execute Low-Risk Actions</div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Automatically execute read-only system inspections and status checks without popup approval.
            </p>
          </div>
          <input
            type="checkbox"
            checked={autoApproveLowRisk}
            onChange={(e) => setAutoApproveLowRisk(e.target.checked)}
            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
          />
        </div>
      </div>

      {/* Model Selection */}
      <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Cpu size={20} color="var(--accent-purple)" />
          <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Reasoning & LLM Backend Provider</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Selected Model</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={{
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '13px'
            }}
          >
            <option value="gpt-4o-mini (Cloud)">gpt-4o-mini (Cloud API - High Capacity)</option>
            <option value="llama3:8b (Ollama Local)">llama3:8b (Ollama Local - Privacy / Offline)</option>
            <option value="mistral:7b (Ollama Local)">mistral:7b (Ollama Local - Offline)</option>
          </select>
        </div>
      </div>

      {/* Hotkey Shortcuts */}
      <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Key size={20} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Global Hotkey Shortcut</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Toggle Window Shortcut</label>
          <input
            type="text"
            value={globalHotkey}
            onChange={(e) => setGlobalHotkey(e.target.value)}
            style={{
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px'
            }}
          />
        </div>
      </div>
    </div>
  );
};
