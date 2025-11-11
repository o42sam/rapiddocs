import { apiClient } from '../api/client';

export interface CreditsPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  currency: string;
}

export interface CreditsPurchaseRequest {
  package: 'small' | 'medium' | 'large';
  bitcoin_transaction_id: string;
}

export interface CreditsPurchaseResponse {
  message: string;
  credits_added: number;
  new_balance: number;
  transaction_id: string;
}

export interface CreditsBalanceResponse {
  credits: number;
  user_id: string;
}

export interface DocumentCost {
  document_type: string;
  cost: number;
}

class CreditsService {
  async getPackages(): Promise<CreditsPackage[]> {
    const response = await apiClient.get<{ packages: CreditsPackage[] }>(
      `/credits/packages`
    );
    return response.data.packages;
  }

  async getBalance(): Promise<CreditsBalanceResponse> {
    const response = await apiClient.get<CreditsBalanceResponse>(
      `/credits/balance`
    );
    return response.data;
  }

  async purchaseCredits(purchaseData: CreditsPurchaseRequest): Promise<CreditsPurchaseResponse> {
    const response = await apiClient.post<CreditsPurchaseResponse>(
      `/credits/purchase`,
      purchaseData
    );
    return response.data;
  }

  async getDocumentCost(documentType: string): Promise<DocumentCost> {
    const response = await apiClient.get<DocumentCost>(
      `/credits/cost/${documentType}`
    );
    return response.data;
  }

  async deductCredits(documentType: string): Promise<{ message: string; credits_deducted: number; new_balance: number }> {
    const response = await apiClient.post(
      `/credits/deduct`,
      null,
      {
        params: { document_type: documentType }
      }
    );
    return response.data;
  }
}

export const creditsService = new CreditsService();
