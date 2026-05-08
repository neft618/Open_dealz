import { useAuthStore } from '../store/authStore';

export const useCurrentRole = () => {
  return useAuthStore((state) => state.getCurrentRole());
};