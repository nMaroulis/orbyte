export interface CryptoWallet {
  id: number;
  address: string;
  currency: string;
  balance: number;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface FiatWallet {
  id: number;
  account_number: string;
  currency: string;
  balance: number;
  bank_name: string;
  iban?: string;
  swift_bic?: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface WalletsResponse {
  success: boolean;
  message: string;
  data: {
    cryptoWallets: CryptoWallet[];
    fiatWallets: FiatWallet[];
  };
}
