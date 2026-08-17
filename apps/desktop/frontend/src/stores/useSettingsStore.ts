import { create } from 'zustand';

interface SettingsState {
  agentUrl: string;
  autoApproveLowRisk: boolean;
  globalHotkey: string;
  selectedModel: string;
  theme: 'dark' | 'light';
  
  setAgentUrl: (url: string) => void;
  setAutoApproveLowRisk: (autoApprove: boolean) => void;
  setGlobalHotkey: (hotkey: string) => void;
  setSelectedModel: (model: string) => void;
  setTheme: (theme: 'dark' | 'light') => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  agentUrl: 'http://127.0.0.1:8765',
  autoApproveLowRisk: true,
  globalHotkey: 'Ctrl+Space',
  selectedModel: 'gpt-4o-mini (Cloud)',
  theme: 'dark',

  setAgentUrl: (agentUrl) => set({ agentUrl }),
  setAutoApproveLowRisk: (autoApproveLowRisk) => set({ autoApproveLowRisk }),
  setGlobalHotkey: (globalHotkey) => set({ globalHotkey }),
  setSelectedModel: (selectedModel) => set({ selectedModel }),
  setTheme: (theme) => set({ theme }),
}));
