import React, { useState } from 'react';
import { Send, Mic, MicOff, Sparkles, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { sendCommand } from '../../services/agentApi';
import { useTaskStore } from '../../stores/useTaskStore';
import { useApprovalStore } from '../../stores/useApprovalStore';

export const CommandCenter: React.FC = () => {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const { isExecuting, setIsExecuting, updateTaskPlan, setLatestResult, latestResult } = useTaskStore();
  const addPendingApproval = useApprovalStore((s) => s.addPendingApproval);

  const quickPrompts = [
    'Check system info',
    'Open VS Code workspace',
    'Read package.json file',
    'Run git status',
  ];

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input.trim();
    if (!text || isExecuting) return;

    setInput('');
    setIsExecuting(true);

    try {
      const result = await sendCommand(text);
      setLatestResult(result);

      if (result.status === 'awaiting_approval' && result.output_data) {
        addPendingApproval({
          taskId: result.task_id,
          step: {
            step_id: result.output_data.step_id || 's1',
            tool_id: result.output_data.tool_id || 'tool',
            description: `Tool '${result.output_data.tool_id}' requires explicit user confirmation.`,
            tool_input: result.output_data,
            risk_level: 'high',
            requires_approval: true,
            status: 'awaiting_approval',
          },
          reason: result.output_data.reason || result.summary,
        });
      }
    } catch (e: any) {
      setLatestResult({
        command_id: 'cmd-err',
        task_id: 'task-err',
        status: 'failed',
        summary: e.message || 'Failed to process command',
        steps_executed: 0,
        error_message: e.message,
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const toggleMic = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setTimeout(() => {
        setIsRecording(false);
        setInput('Show system status');
      }, 3000);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      padding: '24px',
      gap: '20px',
      maxWidth: '900px',
      margin: '0 auto',
      width: '100%'
    }}>
      {/* Banner / Header */}
      <div style={{ textAlign: 'center', marginBottom: '8px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '6px', background: 'linear-gradient(135deg, #f3f4f6, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          What can JARVIS execute for you?
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Secure, local-first computer automation agent. Execute natural language desktop commands.
        </p>
      </div>

      {/* Natural Language Prompt Input Bar */}
      <div className="glass-panel glow-cyan" style={{
        borderRadius: 'var(--radius-lg)',
        padding: '10px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        border: '1px solid rgba(56, 189, 248, 0.4)'
      }}>
        <Sparkles size={20} color="var(--accent-cyan)" />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="e.g. 'Read package.json', 'Run git status', or 'Open VS Code'..."
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-primary)',
            fontSize: '15px',
            fontFamily: 'var(--font-sans)'
          }}
        />
        
        {/* Push-to-talk Mic Button */}
        <button
          onClick={toggleMic}
          title={isRecording ? 'Listening...' : 'Push to talk'}
          style={{
            background: isRecording ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.05)',
            border: isRecording ? '1px solid rgba(239, 68, 68, 0.5)' : '1px solid var(--border-color)',
            color: isRecording ? '#ef4444' : 'var(--text-secondary)',
            padding: '8px',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          {isRecording ? <MicOff size={18} className="animate-pulse-glow" /> : <Mic size={18} />}
        </button>

        {/* Send Button */}
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || isExecuting}
          style={{
            background: input.trim() && !isExecuting ? 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))' : 'rgba(255, 255, 255, 0.08)',
            border: 'none',
            color: '#fff',
            padding: '10px 18px',
            borderRadius: 'var(--radius-md)',
            cursor: input.trim() && !isExecuting ? 'pointer' : 'not-allowed',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}
        >
          <span>Execute</span>
          <Send size={15} />
        </button>
      </div>

      {/* Quick Suggestion Chips */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
        {quickPrompts.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              padding: '6px 14px',
              borderRadius: '20px',
              cursor: 'pointer',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
          >
            <span>{chip}</span>
            <ArrowRight size={12} />
          </button>
        ))}
      </div>

      {/* Execution Result Card */}
      {latestResult && (
        <div className="glass-card" style={{ padding: '20px', marginTop: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {latestResult.status === 'success' && <CheckCircle2 size={20} color="#34d399" />}
              {latestResult.status === 'failed' && <AlertCircle size={20} color="#f87171" />}
              {latestResult.status === 'awaiting_approval' && <AlertCircle size={20} color="#fb923c" />}
              <span style={{ fontWeight: 600, fontSize: '15px' }}>
                Execution Outcome ({latestResult.status.toUpperCase()})
              </span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Task ID: {latestResult.task_id}
            </span>
          </div>

          <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
            <p style={{ fontSize: '14px', lineHeight: '1.5', color: 'var(--text-primary)' }}>
              {latestResult.summary}
            </p>

            {latestResult.error_message && (
              <p style={{ color: '#f87171', fontSize: '13px', marginTop: '8px', fontFamily: 'var(--font-mono)' }}>
                Error: {latestResult.error_message}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
