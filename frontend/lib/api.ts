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
   * @returns Job ID and status
   */
  async generateAvatar(file: File): Promise<GenerateResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<GenerateResponse>('/api/generate', formData, {
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

// ============================================================================
// EXPORTS
// ============================================================================

export const api = new ApiClient();
export default api;
