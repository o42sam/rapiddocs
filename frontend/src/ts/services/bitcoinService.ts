import { apiClient } from '../api/client';

export interface BitcoinPaymentInitRequest {
  package: 'small' | 'medium' | 'large';
}

export interface BitcoinPaymentInitResponse {
  payment_id: string;
  payment_address: string;
  amount_btc: number;
  amount_usd: number;
  qr_code_data: string; // Base64 encoded QR code image
  expires_at: string;
  message: string;
}

export interface BitcoinPaymentStatusRequest {
  payment_id: string;
}

export interface BitcoinPaymentStatusResponse {
  payment_id: string;
  status: string; // pending, confirming, confirmed, forwarded, failed, expired
  payment_address: string;
  amount_btc: number;
  amount_received_btc: number;
  amount_usd: number;
  confirmations: number;
  required_confirmations: number;
  tx_hash: string | null;
  forwarding_tx_hash: string | null;
  expires_at: string;
  credits: number;
  message: string;
}

export interface BitcoinPaymentConfirmResponse {
  success: boolean;
  payment_id: string;
  credits_added: number;
  new_balance: number;
  tx_hash: string;
  message: string;
}

class BitcoinService {
  async initiateBitcoinPayment(request: BitcoinPaymentInitRequest): Promise<BitcoinPaymentInitResponse> {
    const response = await apiClient.post<BitcoinPaymentInitResponse>(
      `/bitcoin/initiate`,
      request
    );
    return response.data;
  }

  async checkPaymentStatus(request: BitcoinPaymentStatusRequest): Promise<BitcoinPaymentStatusResponse> {
    const response = await apiClient.post<BitcoinPaymentStatusResponse>(
      `/bitcoin/status`,
      request
    );
    return response.data;
  }

  async confirmPayment(paymentId: string): Promise<BitcoinPaymentConfirmResponse> {
    const response = await apiClient.post<BitcoinPaymentConfirmResponse>(
      `/bitcoin/confirm/${paymentId}`
    );
    return response.data;
  }
}

export const bitcoinService = new BitcoinService();
