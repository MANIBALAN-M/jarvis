import { create } from 'zustand';
import { CommandResult, TaskPlan, TaskStep } from '../types';

interface TaskState {
  tasks: TaskPlan[];
  activeTask: TaskPlan | null;
  latestResult: CommandResult | null;
  isExecuting: boolean;
  
  setTasks: (tasks: TaskPlan[]) => void;
  setActiveTask: (task: TaskPlan | null) => void;
  updateTaskPlan: (plan: TaskPlan) => void;
  setLatestResult: (result: CommandResult | null) => void;
  setIsExecuting: (executing: boolean) => void;
  updateStepStatus: (taskId: string, stepId: string, status: TaskStep['status'], summary?: string, error?: string) => void;
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  activeTask: null,
  latestResult: null,
  isExecuting: false,

  setTasks: (tasks) => set({ tasks }),
  
  setActiveTask: (activeTask) => set({ activeTask }),

  updateTaskPlan: (plan) =>
    set((state) => {
      const exists = state.tasks.some((t) => t.task_id === plan.task_id);
      const updatedTasks = exists
        ? state.tasks.map((t) => (t.task_id === plan.task_id ? plan : t))
        : [plan, ...state.tasks];
      return {
        tasks: updatedTasks,
        activeTask: state.activeTask?.task_id === plan.task_id ? plan : state.activeTask || plan,
      };
    }),

  setLatestResult: (latestResult) => set({ latestResult }),
  
  setIsExecuting: (isExecuting) => set({ isExecuting }),

  updateStepStatus: (taskId, stepId, status, summary, error) =>
    set((state) => {
      const updatePlan = (plan: TaskPlan): TaskPlan => {
        if (plan.task_id !== taskId) return plan;
        const updatedSteps = plan.steps.map((step) => {
          if (step.step_id !== stepId) return step;
          return {
            ...step,
            status,
            output_summary: summary !== undefined ? summary : step.output_summary,
            error_message: error !== undefined ? error : step.error_message,
          };
        });
        return { ...plan, steps: updatedSteps };
      };

      const updatedTasks = state.tasks.map(updatePlan);
      const updatedActive = state.activeTask ? updatePlan(state.activeTask) : null;

      return { tasks: updatedTasks, activeTask: updatedActive };
    }),
}));
