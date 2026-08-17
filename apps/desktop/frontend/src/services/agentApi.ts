import { AgentHealth, AuditEvent, CommandResult, TaskPlan } from '../types';
import { getApiAuthToken as getTauriToken } from './tauriIpc';

let BASE_URL = 'http://127.0.0.1:8765/api/v1';
let API_AUTH_TOKEN = '';

export function setApiBaseUrl(url: string) {
  BASE_URL = url.replace(/\/$/, '') + '/api/v1';
}

export function setApiAuthToken(token: string) {
  API_AUTH_TOKEN = token;
}

export async function resolveApiAuthToken(): Promise<string> {
  if (API_AUTH_TOKEN) return API_AUTH_TOKEN;
  const tauriToken = await getTauriToken();
  if (tauriToken) {
    API_AUTH_TOKEN = tauriToken;
    return tauriToken;
  }
  return '';
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const token = await resolveApiAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    headers['X-JARVIS-API-KEY'] = token;
  }
  return headers;
}

export async function checkAgentHealth(): Promise<AgentHealth> {
  try {
    const res = await fetch(`http://127.0.0.1:8765/api/v1/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      return { status: 'unhealthy', agent: 'jarvis-local', version: '0.2.0', host: '127.0.0.1', port: 8765 };
    }
    const data = await res.json();
    if (data.api_auth_token) {
      setApiAuthToken(data.api_auth_token);
    }
    return data;
  } catch (_e) {
    return { status: 'offline', agent: 'jarvis-local', version: '0.2.0', host: '127.0.0.1', port: 8765 };
  }
}

export async function sendCommand(rawText: string): Promise<CommandResult> {
  const res = await fetch(`${BASE_URL}/command`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ raw_text: rawText, source: 'text_ui' }),
  });
  if (!res.ok) {
    throw new Error(`Command failed with status ${res.status}`);
  }
  return res.json();
}

export async function fetchTask(taskId: string): Promise<TaskPlan> {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}`, {
    method: 'GET',
    headers: await getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch task ${taskId}`);
  }
  return res.json();
}

export async function approveTaskStep(taskId: string, stepId: string): Promise<CommandResult> {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}/approve`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ step_id: stepId }),
  });
  if (!res.ok) {
    throw new Error(`Approval failed with status ${res.status}`);
  }
  return res.json();
}

export async function rejectTaskStep(taskId: string, stepId: string): Promise<CommandResult> {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}/reject`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ step_id: stepId }),
  });
  if (!res.ok) {
    throw new Error(`Rejection failed with status ${res.status}`);
  }
  return res.json();
}

export async function fetchAuditLogs(limit: number = 50): Promise<AuditEvent[]> {
  try {
    const res = await fetch(`${BASE_URL}/audit?limit=${limit}`, {
      method: 'GET',
      headers: await getAuthHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  } catch (_e) {
    return [];
  }
}
