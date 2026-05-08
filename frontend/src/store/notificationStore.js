import { create } from 'zustand';
import api from '../api/client';

const useNotificationStore = create((set, get) => ({
  unreadCount: 0,

  fetchUnreadCount: async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      set({ unreadCount: response.data.count });
    } catch (error) {
      console.error('Failed to fetch unread count', error);
    }
  },

  markAllRead: async () => {
    try {
      await api.patch('/notifications/read-all');
      set({ unreadCount: 0 });
    } catch (error) {
      console.error('Failed to mark all read', error);
    }
  },
}));

// Polling every 30s
setInterval(() => {
  useNotificationStore.getState().fetchUnreadCount();
}, 30000);

export default useNotificationStore;