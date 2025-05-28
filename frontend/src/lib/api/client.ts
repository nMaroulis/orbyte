import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { API_BASE_URL, DEFAULT_HEADERS } from './config';
import { get } from 'svelte/store';
import { user } from '$lib/stores/auth';

// Add response data interface for better type safety
interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
  headers: any;
  config: any;
  request?: any;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 
        ...DEFAULT_HEADERS,
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      },
      withCredentials: true,
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      const currentUser = get(user);
      if (currentUser?.access_token) {
        const token = currentUser.access_token.replace(/^Bearer\s+/i, '');
        config.headers.Authorization = `Bearer ${token}`;
      }
      console.log('Request config:', {
        url: config.url,
        method: config.method,
        headers: config.headers,
        data: config.data,
      });
      return config;
    }, (error) => {
      console.error('Request error:', error);
      return Promise.reject(error);
    });

    // Add response interceptor for better error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log('Response:', {
          url: response.config.url,
          status: response.status,
          data: response.data,
          headers: response.headers,
        });
        return response;
      },
      (error) => {
        const errorInfo = {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          statusText: error.response?.statusText,
          headers: error.config?.headers,
          request: {
            headers: error.config?.headers,
            data: error.config?.data,
          },
          response: {
            data: error.response?.data,
            headers: error.response?.headers,
          },
          message: error.message,
          stack: error.stack,
        };
        
        console.error('=== API Error ===');
        console.error('URL:', errorInfo.url);
        console.error('Method:', errorInfo.method);
        console.error('Status:', errorInfo.status, errorInfo.statusText);
        console.error('Error Message:', errorInfo.message);
        
        if (errorInfo.response?.data) {
          console.error('Error Details:', JSON.stringify(errorInfo.response.data, null, 2));
        }
        
        if (errorInfo.request?.headers?.Authorization) {
          const token = errorInfo.request.headers.Authorization.replace('Bearer ', '');
          console.error('Token (first 10 chars):', token.substring(0, 10) + '...');
          console.error('Token length:', token.length);
        }
        
        console.error('=== End API Error ===');
        
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    console.log(`GET ${url}`, { config });
    try {
      const response = await this.client.get<T>(url, {
        ...config,
        headers: {
          ...config?.headers,
          'Cache-Control': 'no-cache',
          Pragma: 'no-cache',
        },
      });
      console.log(`GET ${url} response:`, response);
      return response.data;
    } catch (error) {
      console.error(`GET ${url} error:`, error);
      throw error;
    }
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const api = new ApiClient();
