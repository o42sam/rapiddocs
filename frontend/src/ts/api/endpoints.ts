import { apiClient } from './client';
import {
  DocumentGenerationRequest,
  GenerationJobResponse,
  JobStatusResponse,
  DocumentResponse,
} from '../types/document';

export const documentApi = {
  async generateDocument(request: DocumentGenerationRequest & { skip_validation?: boolean }): Promise<GenerationJobResponse> {
    const formData = new FormData();
    formData.append('description', request.description);
    formData.append('length', request.length.toString());
    formData.append('document_type', request.document_type);
    formData.append('use_watermark', request.use_watermark.toString());
    formData.append('statistics', JSON.stringify(request.statistics));
    formData.append('design_spec', JSON.stringify(request.design_spec));

    if (request.logo) {
      formData.append('logo', request.logo);
    }

    if (request.skip_validation !== undefined) {
      formData.append('skip_validation', request.skip_validation.toString());
    }

    const response = await apiClient.post<GenerationJobResponse>(
      '/generate/document',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await apiClient.get<JobStatusResponse>(`/generate/status/${jobId}`);
    return response.data;
  },

  async downloadDocument(jobId: string): Promise<Blob> {
    const response = await apiClient.get(`/generate/download/${jobId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async listDocuments(): Promise<DocumentResponse[]> {
    const response = await apiClient.get<DocumentResponse[]>('/documents');
    return response.data;
  },

  async getDocument(docId: string): Promise<DocumentResponse> {
    const response = await apiClient.get<DocumentResponse>(`/documents/${docId}`);
    return response.data;
  },

  async deleteDocument(docId: string): Promise<void> {
    await apiClient.delete(`/documents/${docId}`);
  },
};
