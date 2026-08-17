import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { NavTab, Sidebar } from '../components/Sidebar';
import { CommandCenter } from '../features/command-center/CommandCenter';
import { TaskMonitor } from '../features/task-monitor/TaskMonitor';
import { ApprovalModal } from '../features/approvals/ApprovalModal';
import { AuditLogView } from '../features/audit-log/AuditLogView';
import { SettingsView } from '../features/settings/SettingsView';
import { agentWs } from '../services/websocket';
import { useTaskStore } from '../stores/useTaskStore';
import { useApprovalStore } from '../stores/useApprovalStore';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('command');
  const updateTaskPlan = useTaskStore((s) => s.updateTaskPlan);
  const addPendingApproval = useApprovalStore((s) => s.addPendingApproval);

  useEffect(() => {
    agentWs.connect();

    const unsubscribe = agentWs.subscribe((data) => {
      if (data.event === 'plan_created' && data.plan) {
        updateTaskPlan(data.plan);
      }
      if (data.event === 'task_completed' && data.result) {
        if (data.result.status === 'awaiting_approval' && data.result.output_data) {
          addPendingApproval({
            taskId: data.result.task_id,
            step: {
              step_id: data.result.output_data.step_id || 's1',
              tool_id: data.result.output_data.tool_id || 'tool',
              description: `Tool '${data.result.output_data.tool_id}' requires explicit approval`,
              tool_input: data.result.output_data,
              risk_level: 'high',
              requires_approval: true,
              status: 'awaiting_approval',
            },
            reason: data.result.output_data.reason || data.result.summary,
          });
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Header />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        <main style={{ flex: 1, height: 'calc(100vh - 52px)', overflowY: 'auto', background: 'var(--bg-primary)' }}>
          {activeTab === 'command' && <CommandCenter />}
          {activeTab === 'tasks' && <TaskMonitor />}
          {activeTab === 'approvals' && <ApprovalModal />}
          {activeTab === 'audit' && <AuditLogView />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>

      {/* Global Human-in-the-Loop Gate Approval Popup */}
      <ApprovalModal />
    </div>
  );
};
