const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Candidate {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  skills: string[] | null;
  profile_links: Record<string, string> | null;
}

export interface QueueMetrics {
  queue_length: number;
  retry_queue_length: number;
  processed_count?: number;
  failed_count?: number;
}

export enum ApplicationStatus {
  APPLIED = 'APPLIED',
  INTERVIEWING = 'INTERVIEWING',
  REJECTED = 'REJECTED',
  HIRED = 'HIRED',
}

export interface Application {
  id: string;
  candidate_id: string;
  job_title: string;
  status: ApplicationStatus;
}

class ApiClient {
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    return response.json();
  }

  async getCandidates(): Promise<Candidate[]> {
    const response = await fetch(`${API_URL}/candidates`, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch candidates');
    }

    return response.json();
  }

  async getCandidate(candidateId: string): Promise<Candidate> {
    const response = await fetch(`${API_URL}/candidates/${candidateId}`, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch candidate');
    }

    return response.json();
  }

  async updateCandidate(candidateId: string, data: {
    full_name?: string;
    phone?: string;
    skills?: string[];
    profile_links?: Record<string, string>;
  }): Promise<Candidate> {
    const response = await fetch(`${API_URL}/candidates/${candidateId}`, {
      method: 'PUT',
      headers: {
        ...this.getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to update candidate');
    }

    return response.json();
  }

  async createCandidate(data: {
    full_name: string;
    email: string;
    phone?: string;
    skills?: string[];
    profile_links?: Record<string, string>;
  }): Promise<Candidate> {
    const response = await fetch(`${API_URL}/candidates`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create candidate');
    }

    return response.json();
  }

  async uploadResume(candidateId: string, file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/candidates/${candidateId}/resume-parsing`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload resume');
    }

    return response.json();
  }

  async getQueueMetrics(): Promise<QueueMetrics> {
    const response = await fetch(`${API_URL}/candidates/queue/metrics`, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch queue metrics');
    }

    return response.json();
  }

  async enrichProfile(candidateId: string, file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/candidates/${candidateId}/profile-enrichment`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to enrich profile');
    }

    return response.json();
  }

  // Application endpoints
  async getApplicationsForCandidate(candidateId: string): Promise<Application[]> {
    const response = await fetch(`${API_URL}/applications/candidate/${candidateId}`, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch applications');
    }

    return response.json();
  }

  async createApplication(data: {
    candidate_id: string;
    job_title: string;
    status: ApplicationStatus;
  }): Promise<Application> {
    const response = await fetch(`${API_URL}/applications`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create application');
    }

    return response.json();
  }

  async updateApplicationStatus(applicationId: string, status: ApplicationStatus): Promise<Application> {
    const response = await fetch(`${API_URL}/applications/${applicationId}`, {
      method: 'PATCH',
      headers: {
        ...this.getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });

    if (!response.ok) {
      throw new Error('Failed to update application status');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
