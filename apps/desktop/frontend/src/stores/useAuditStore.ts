import { create } from 'zustand';
import { AuditEvent, RiskLevel } from '../types';

interface AuditState {
  auditLogs: AuditEvent[];
  filterRisk: RiskLevel | 'all';
  searchQuery: string;
  isLoading: boolean;
  
  setAuditLogs: (logs: AuditEvent[]) => void;
  setFilterRisk: (risk: RiskLevel | 'all') => void;
  setSearchQuery: (query: string) => void;
  setIsLoading: (loading: boolean) => void;
}

export const useAuditStore = create<AuditState>((set) => ({
  auditLogs: [],
  filterRisk: 'all',
  searchQuery: '',
  isLoading: false,

  setAuditLogs: (auditLogs) => set({ auditLogs }),
  setFilterRisk: (filterRisk) => set({ filterRisk }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setIsLoading: (isLoading) => set({ isLoading }),
}));
