import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { User } from '$lib/types';

export const user = writable<User | null>(null);

export function setUser(userData: User | null) {
  user.set(userData);
  if (browser) {
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
    } else {
      localStorage.removeItem('user');
    }
  }
}

// Initialize user from localStorage if available
if (browser) {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      user.set(JSON.parse(storedUser));
    } catch (e) {
      console.error('Failed to parse stored user', e);
      localStorage.removeItem('user');
    }
  }
}
