export type CommandSource = 'text_ui' | 'voice_stt' | 'global_hotkey' | 'scheduled' | 'cloud_sync';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type PolicyDecision = 'allow' | 'ask_user' | 'block';

export interface TaskStep {
  step_id: string;
  tool_id: string;
  description: string;
  tool_input: Record<string, any>;
  risk_level: RiskLevel;
  requires_approval: boolean;
  approval_token?: string | null;
  status: 'pending' | 'running' | 'success' | 'failed' | 'blocked' | 'awaiting_approval';
  output_summary?: string | null;
  error_message?: string | null;
}

export interface TaskPlan {
  task_id: string;
  command_id: string;
  goal_summary: string;
  steps: TaskStep[];
  created_at_ts: number;
  status: 'created' | 'in_progress' | 'awaiting_approval' | 'completed' | 'failed';
}

export interface CommandResult {
  command_id: string;
  task_id: string;
  status: 'success' | 'failed' | 'awaiting_approval';
  summary: string;
  steps_executed: number;
  error_message?: string | null;
  output_data?: Record<string, any> | null;
}

export interface AuditEvent {
  event_id: string;
  event_type: string;
  timestamp_ts: number;
  tool_id: string;
  risk_level: RiskLevel;
  decision: PolicyDecision;
  args?: Record<string, any> | null;
}

export interface AgentHealth {
  status: 'healthy' | 'unhealthy' | 'offline';
  agent: string;
  version: string;
  host: string;
  port: number;
}

export interface SystemStats {
  cpu: number;
  memory: number;
  is_placeholder: boolean;
  label: string;
}
