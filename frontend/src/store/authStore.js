import { create } from 'zustand';
import api from '../api/client';

const useAuthStore = create((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('accessToken') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  isAuthenticated: !!localStorage.getItem('accessToken'),

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    set({ accessToken: access_token, refreshToken: refresh_token, isAuthenticated: true });
    // Fetch user
    const userResponse = await api.get('/auth/me');
    set({ user: userResponse.data });
  },

  logout: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
  },

  setUser: (user) => set({ user }),

  getCurrentRole: () => get().user?.role,
}));

export { useAuthStore };