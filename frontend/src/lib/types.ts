// User related types
export interface User {
  id: number;
  email: string;
  wallet_address: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at?: string;
  access_token?: string; // Only used client-side
}

// GPU related types
export enum GPUStatus {
  AVAILABLE = 'available',
  IN_USE = 'in_use',
  MAINTENANCE = 'maintenance',
  OFFLINE = 'offline',
}

export enum GPUModel {
  RTX_4090 = 'rtx_4090',
  A100 = 'a100',
  H100 = 'h100',
  OTHER = 'other',
}

export interface GPU {
  id: number;
  name: string;
  model: GPUModel;
  vram_gb: number;
  price_per_hour: number;
  status: GPUStatus;
  owner_id: number;
  specs: Record<string, any>;
  os?: string;
  cpu_model?: string;
  cpu_cores?: number;
  ram_gb?: number;
  storage_gb?: number;
  network_speed_mbps?: number;
  created_at: string;
  updated_at?: string;
  owner?: User;
}

// Task related types
export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum TaskType {
  TEXT_GENERATION = 'text_generation',
  IMAGE_GENERATION = 'image_generation',
  MODEL_TRAINING = 'model_training',
  OTHER = 'other',
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  task_type: TaskType;
  status: TaskStatus;
  input_data: Record<string, any>;
  output_data?: Record<string, any>;
  cost: number;
  requester_id: number;
  gpu_id?: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
  requester?: User;
  gpu?: GPU;
}

// Payment related types
export enum PaymentStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
}

export interface Payment {
  id: number;
  amount: number;
  status: PaymentStatus;
  sender_id: number;
  receiver_id: number;
  task_id: number;
  transaction_hash?: string;
  created_at: string;
  updated_at?: string;
  sender?: User;
  receiver?: User;
  task?: Task;
}

// API response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Form types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  wallet_address: string;
}

export interface TaskFormData {
  title: string;
  description?: string;
  task_type: TaskType;
  input_data: Record<string, any>;
  gpu_id?: number;
}

export interface GPUFormData {
  name: string;
  model: GPUModel;
  vram_gb: number;
  price_per_hour: number;
  status: GPUStatus;
  specs: Record<string, any>;
}
