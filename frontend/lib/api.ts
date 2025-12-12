/**
 * API Client for Mini-Me Backend
 * Handles all API requests with Firebase authentication
 */

import axios, { AxiosInstance } from 'axios';
import { getIdToken } from './firebase';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// API CLIENT
// ============================================================================

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await getIdToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/signin';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Health check
   */
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Generate pixel art avatar
   * @param file Image file to process
   * @param sessionId Optional Stripe session ID for one-time payment
   * @returns Job ID and status
   */
  async generateAvatar(file: File, sessionId?: string): Promise<GenerateResponse> {
    const formData = new FormData();
    formData.append('file', file);

    // Add session_id as query parameter if present
    const url = sessionId ? `/api/generate?session_id=${sessionId}` : '/api/generate';

    const response = await this.client.post<GenerateResponse>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Get job status
   * @param jobId Job ID to check
   * @returns Job status and result URL if completed
   */
  async getJobStatus(jobId: string): Promise<JobResponse> {
    const response = await this.client.get<JobResponse>(`/api/jobs/${jobId}`);
    return response.data;
  }

  /**
   * Get user's job history
   * @param limit Number of jobs to return (default: 10)
   * @returns List of user jobs
   */
  async getUserJobs(limit: number = 10): Promise<JobListResponse> {
    const response = await this.client.get<JobListResponse>('/api/jobs', {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Poll job status until completed or failed
   * @param jobId Job ID to poll
   * @param onUpdate Callback for status updates
   * @param maxAttempts Maximum polling attempts (default: 60)
   * @param intervalMs Polling interval in milliseconds (default: 2000)
   */
  async pollJobStatus(
    jobId: string,
    onUpdate?: (status: JobResponse) => void,
    maxAttempts: number = 60,
    intervalMs: number = 2000
  ): Promise<JobResponse> {
    let attempts = 0;

    while (attempts < maxAttempts) {
      const job = await this.getJobStatus(jobId);

      if (onUpdate) {
        onUpdate(job);
      }

      // Check if job is complete or failed
      if (job.status === 'completed' || job.status === 'failed') {
        return job;
      }

      // Wait before next poll
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
      attempts++;
    }

    throw new Error('Job polling timeout exceeded');
  }

  /**
   * Create Stripe checkout session
   * @param paymentType Type of payment: 'pro' or 'onetime'
   * @returns Checkout session with redirect URL
   */
  async createCheckoutSession(paymentType: 'pro' | 'onetime'): Promise<CheckoutSessionResponse> {
    const response = await this.client.post<CheckoutSessionResponse>(
      '/api/payments/create-checkout-session',
      { payment_type: paymentType }
    );
    return response.data;
  }

  /**
   * Create Stripe customer portal session
   * @returns Portal URL for managing subscription
   */
  async createPortalSession(): Promise<{ url: string }> {
    const response = await this.client.post<{ url: string }>(
      '/api/payments/create-portal-session'
    );
    return response.data;
  }

  /**
   * Get current user's subscription status
   * @returns Subscription details
   */
  async getSubscriptionStatus(): Promise<SubscriptionStatus> {
    const response = await this.client.get<SubscriptionStatus>(
      '/api/payments/subscription-status'
    );
    return response.data;
  }
}

// ============================================================================
// TYPES
// ============================================================================

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface GenerateResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}

export interface JobResponse {
  job_id: string;
  user_id: string;
  status: JobStatus;
  input_image_url: string;
  output_image_url?: string;
  created_at: string;
  updated_at: string;
  error_message?: string;
  metadata?: {
    processing_time?: number;
    model_used?: string;
  };
}

export interface JobListResponse {
  jobs: JobResponse[];
  total: number;
}

export interface CheckoutSessionResponse {
  session_id: string;
  url: string;
}

export interface SubscriptionStatus {
  user_id: string;
  subscription_tier: string;
  subscription_status?: string;
  usage_count: number;
  usage_limit: number;
  trial_end?: string;
  current_period_end?: string;
  has_payment_method: boolean;
}

// ============================================================================
// EXPORTS
// ============================================================================

export const api = new ApiClient();
export default api;
