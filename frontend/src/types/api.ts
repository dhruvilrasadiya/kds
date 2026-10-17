/**
 * TypeScript types for the Smart Kitchen Queue Management System API
 * Based on the backend Pydantic models
 */

// Enums
export enum OrderStatus {
  PENDING = "pending",
  ACCEPTED = "accepted", 
  PREPARING = "preparing",
  COOKING = "cooking",
  READY = "ready",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  HOLD = "on-hold"
}

export enum ItemStatus {
  PENDING = "pending",
  ASSIGNED = "assigned",
  IN_PROGRESS = "in_progress", 
  COMPLETED = "completed",
  CANCELLED = "cancelled"
}

export enum KitchenStatus {
  ACTIVE = "active",
  MAINTENANCE = "maintenance",
  OFFLINE = "offline"
}

export enum PriorityLevel {
  NONE = "none",
  LOW = "low",
  MEDIUM = "medium", 
  HIGH = "high",
  URGENT = "urgent"
}

export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard",
  EXPERT = "expert"
}

// Base Models
export interface MenuItem {
  item_id: string;
  name: string;
  kitchen_id: string;
  prep_time: number;
  difficulty: DifficultyLevel;
  description?: string;
  price?: number;
  image?: string;
  calories?: number;
  category?: string;
}

export interface Kitchen {
  kitchen_id: string;
  name: string;
  capacity: number;
  current_load: number;
  specialization: string;
  status?: KitchenStatus;
  staff_count?: number;
}

export interface QueueItem {
  queue_id: string;
  order_id: string;
  item_id: string;
  kitchen_id: string;
  status: ItemStatus;
  priority: PriorityLevel;
  estimated_start_time?: string;
  estimated_completion_time?: string;
  actual_start_time?: string;
  actual_completion_time?: string;
  starvation_count: number;
  assigned_staff?: string;
}

export interface Order {
  order_id: string;
  items: string[];
  timestamp: string;
  status: OrderStatus;
  estimated_completion?: string;
  actual_completion?: string;
  queue_items: QueueItem[];
  total_prep_time?: number;
  customer_id?: string;
  notes?: string;
  table_number?: string;
  customer_name?: string;
}

export interface PerformanceRecord {
  date: string;
  kitchen_id: string;
  item_id: string;
  order_id: string;
  actual_prep_time: number;
  scheduled_prep_time: number;
  delay_minutes: number;
  kitchen_load: number;
  staff_efficiency?: number;
  quality_score?: number;
}

// Request Models
export interface CreateOrderRequest {
  items: string[];
  customer_id?: string;
  notes?: string;
  table_number?: string;
  customer_name?: string;
}

export interface UpdateOrderRequest {
  status?: OrderStatus;
  notes?: string;
}

export interface CompleteItemRequest {
  queue_id: string;
  actual_completion_time?: string;
  quality_notes?: string;
}

export interface KitchenStatusUpdateRequest {
  kitchen_id: string;
  status: KitchenStatus;
  notes?: string;
}

export interface PerformanceQueryRequest {
  start_date?: string;
  end_date?: string;
  kitchen_id?: string;
  item_id?: string;
}

// Response Models
export interface BaseResponse {
  success: boolean;
  message: string;
  timestamp: string;
}

export interface OrderResponse extends BaseResponse {
  order?: Order;
}

export interface OrderListResponse extends BaseResponse {
  orders: Order[];
  total_count: number;
}

export interface KitchenStatusResponse extends BaseResponse {
  kitchen: Kitchen;
  queue_items: QueueItem[];
  performance_metrics?: Record<string, any>;
}

export interface KitchenStatusListResponse extends BaseResponse {
  kitchens: Kitchen[];
  total_active_orders: number;
}

export interface QueueStatusResponse extends BaseResponse {
  queue_items: QueueItem[];
  total_items: number;
  kitchen_loads: Record<string, number>;
}

export interface PerformanceMetricsResponse extends BaseResponse {
  metrics: Record<string, any>;
  period_start?: string;
  period_end?: string;
}

export interface PerformanceHistoryResponse extends BaseResponse {
  records: PerformanceRecord[];
  total_count: number;
}

export interface SystemHealthResponse extends BaseResponse {
  status: string;
  components: Record<string, string>;
  uptime?: string;
  version?: string;
}

export interface ErrorResponse extends BaseResponse {
  error_code?: string;
  details?: Record<string, any>;
}

// API Configuration
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
}

// Utility Types
export type ApiResponse<T> = T | ErrorResponse;
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}
