import { create } from 'zustand';
import { TaskStep } from '../types';

export interface PendingApproval {
  taskId: string;
  step: TaskStep;
  reason?: string;
}

interface ApprovalState {
  pendingApprovals: PendingApproval[];
  activeApprovalModal: PendingApproval | null;
  
  addPendingApproval: (approval: PendingApproval) => void;
  removePendingApproval: (taskId: string, stepId: string) => void;
  openApprovalModal: (approval: PendingApproval) => void;
  closeApprovalModal: () => void;
}

export const useApprovalStore = create<ApprovalState>((set) => ({
  pendingApprovals: [],
  activeApprovalModal: null,

  addPendingApproval: (approval) =>
    set((state) => {
      const exists = state.pendingApprovals.some(
        (a) => a.taskId === approval.taskId && a.step.step_id === approval.step.step_id
      );
      if (exists) return state;
      return {
        pendingApprovals: [...state.pendingApprovals, approval],
        activeApprovalModal: state.activeApprovalModal || approval,
      };
    }),

  removePendingApproval: (taskId, stepId) =>
    set((state) => {
      const remaining = state.pendingApprovals.filter(
        (a) => !(a.taskId === taskId && a.step.step_id === stepId)
      );
      const isCurrentModal =
        state.activeApprovalModal?.taskId === taskId &&
        state.activeApprovalModal?.step.step_id === stepId;
      return {
        pendingApprovals: remaining,
        activeApprovalModal: isCurrentModal ? remaining[0] || null : state.activeApprovalModal,
      };
    }),

  openApprovalModal: (approval) => set({ activeApprovalModal: approval }),

  closeApprovalModal: () =>
    set((state) => ({
      activeApprovalModal: state.pendingApprovals.find(a => a !== state.activeApprovalModal) || null,
    })),
}));
