import { SystemStats } from '../types';

export interface TauriWindow {
  __TAURI_METADATA__?: any;
}

export function isTauriEnvironment(): boolean {
  return typeof window !== 'undefined' && '__TAURI_METADATA__' in window;
}

export async function toggleWindowVisibility(): Promise<void> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('toggle_window');
    } catch (e) {
      console.warn('Tauri IPC toggle_window failed:', e);
    }
  } else {
    console.log('[Browser Fallback] toggleWindowVisibility called');
  }
}

export async function sendDesktopNotification(title: string, body: string): Promise<void> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('show_notification', { title, body });
    } catch (e) {
      console.warn('Tauri IPC show_notification failed:', e);
    }
  } else {
    console.log(`[Notification Fallback] ${title}: ${body}`);
  }
}

export async function getSystemStats(): Promise<SystemStats> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('get_system_stats');
    } catch (e) {
      return { cpu: 12, memory: 45, is_placeholder: true, label: 'Fallback Metrics' };
    }
  }
  return { cpu: 8, memory: 38, is_placeholder: true, label: 'Browser Preview Metrics' };
}

export async function getApiAuthToken(): Promise<string> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<string>('get_api_token');
    } catch (e) {
      console.warn('Tauri IPC get_api_token failed:', e);
    }
  }
  return '';
}
