// API base URL (should be in .env in production)
export const API_BASE_URL = 'http://localhost:8000/api'; // Base URL includes /api prefix

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/token',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  GPUS: {
    LIST: '/gpus',
    DETAIL: (id: string | number) => `/gpus/${id}`,
    MY_GPUS: '/gpus/my-gpus',
  },
  TASKS: {
    LIST: '/tasks',
    DETAIL: (id: string | number) => `/tasks/${id}`,
    CANCEL: (id: string | number) => `/tasks/${id}/cancel`,
  },
  PAYMENTS: {
    LIST: '/payments',
    SENT: '/payments/sent',
    RECEIVED: '/payments/received',
    DETAIL: (id: string | number) => `/payments/${id}`,
    CREATE: (taskId: string | number) => `/tasks/${taskId}/payments`,
  },
};

export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'application/json',
};
