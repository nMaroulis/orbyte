import { get } from 'svelte/store';
import { API_ENDPOINTS } from '$lib/api/config';
import { api } from '$lib/api/client';
import { user, setUser } from '$lib/stores/auth';
import type { User, LoginFormData, RegisterFormData } from '$lib/types';

export class AuthService {
  static async login(credentials: LoginFormData): Promise<User> {
    console.log('\n🔐 Starting login process...');
    console.log('Login attempt for email:', credentials.email);
    
    try {
      const params = new URLSearchParams();
      params.append('username', credentials.email);
      params.append('password', credentials.password);
      
      console.log('📤 Sending login request to:', API_ENDPOINTS.AUTH.LOGIN);
      
      const response = await api.post<{ access_token: string; token_type: string }>(
        API_ENDPOINTS.AUTH.LOGIN,
        params.toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      console.log('✅ Login successful. Token received.');
      console.log('Token type:', response.token_type);
      console.log('Token (first 10 chars):', response.access_token.substring(0, 10) + '...');

      // Get user details
      console.log('\n🔍 Fetching user details...');
      const userResponse = await this.getCurrentUser(response.access_token);
      
      // Combine user data with token
      const userWithToken = {
        ...userResponse,
        access_token: response.access_token,
      };
      
      console.log('👤 User data received:', {
        id: userWithToken.id,
        email: userWithToken.email,
        is_admin: userWithToken.is_admin,
        token_length: userWithToken.access_token?.length || 0
      });
      
      // Update store
      console.log('🔄 Updating user store...');
      setUser(userWithToken);
      
      console.log('✅ Login process completed successfully');
      return userWithToken;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  static async register(userData: RegisterFormData): Promise<User> {
    try {
      const response = await api.post<User>(
        API_ENDPOINTS.AUTH.REGISTER,
        userData
      );
      
      // Auto-login after registration
      return this.login({
        email: userData.email,
        password: userData.password,
      });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  static async getCurrentUser(token?: string): Promise<User> {
    console.log('\n=== getCurrentUser called ===');
    console.log('Token provided:', token ? `[length: ${token.length}]` : 'none');
    
    try {
      // If no token is provided, try to get it from the current user
      if (!token) {
        console.log('ℹ️  No token provided, checking user store...');
        const currentUser = get(user);
        
        if (currentUser?.access_token) {
          token = currentUser.access_token;
          console.log('✅ Using token from user store');
          console.log('Token from store (first 10 chars):', token.substring(0, 10) + '...');
        } else {
          console.log('❌ No token available in user store');
        }
      } else {
        console.log('ℹ️  Using provided token');
        console.log('Provided token (first 10 chars):', token.substring(0, 10) + '...');
      }
      
      // Make sure we have a token
      if (!token) {
        const error = new Error('No authentication token available');
        console.error('❌ Error:', error.message);
        throw error;
      }
      
      // Clean the token (remove 'Bearer ' prefix if present)
      const cleanToken = token.replace(/^Bearer\s+/i, '');
      console.log('🔑 Cleaned token length:', cleanToken.length);
      
      // Make the request with the token in the Authorization header
      console.log('\n🌐 Making request to /me endpoint...');
      console.log('Endpoint:', API_ENDPOINTS.AUTH.ME);
      
      try {
        const requestHeaders = {
          'Authorization': `Bearer ${cleanToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        };
        
        console.log('Request headers:', {
          ...requestHeaders,
          Authorization: `${requestHeaders.Authorization.substring(0, 20)}...`
        });
        
        const response = await api.get<{
          success: boolean;
          message: string;
          data: User;
        }>(
          API_ENDPOINTS.AUTH.ME,
          { 
            headers: requestHeaders,
            params: { local_kw: '' } // Add empty local_kw parameter
          }
        );
        
        console.log('✅ Received response from /me endpoint');
        console.log('Response status:', response ? 'Received' : 'No response');
        
        if (response) {
          console.log('Response data:', {
            success: response.success,
            message: response.message,
            userData: response.data ? {
              id: response.data.id,
              email: response.data.email,
              is_admin: response.data.is_admin
            } : 'No data'
          });
        }
        
        // Check if the response has the expected structure
        if (!response || !response.data) {
          const error = new Error('Invalid response from server');
          console.error('❌ Error:', error.message);
          console.error('Full response:', response);
          throw error;
        }
        
        console.log('✅ Successfully retrieved user data');
        return response.data;
        
      } catch (error: any) {
        console.error('❌ Error in /me request:', error);
        if (error.response) {
          console.error('Error response data:', error.response.data);
          console.error('Error status:', error.response.status);
          console.error('Error headers:', error.response.headers);
        } else if (error.request) {
          console.error('No response received:', error.request);
        } else {
          console.error('Error message:', error.message);
        }
        throw error;
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      throw error;
    }
  }

  static logout(): void {
    setUser(null);
    // Redirect to login page
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  static isAuthenticated(): boolean {
    let currentUser: User | null = null;
    const unsubscribe = user.subscribe((u) => {
      currentUser = u;
    });
    unsubscribe(); // Unsubscribe immediately after getting the value
    return !!(currentUser as any)?.access_token;
  }
}

export default AuthService;
