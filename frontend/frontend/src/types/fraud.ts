/**
 * Type definitions for fraud analysis data
 * Matches backend API response structure from backend/app.py
 */

/**
 * Backend API Response Types
 */
export interface AssessRiskResponse {
  partner_id: string;
  risk_score: number; // 0-100 scale
  rationale: string;
  raw_response: string;
  status: "success";
}

export interface ProfileResponse {
  partner_id: string;
  profile_text: string;
  status: "success";
}

export interface HealthResponse {
  status: "healthy";
  llama_server: string;
}

export interface ApiError {
  error: string;
  message?: string;
}

/**
 * Combined frontend data structure
 */
export interface FraudAnalysisResponse {
  partner_id: string;
  risk_score: number; // 0-100 scale
  rationale: string;
  raw_response?: string;
  profile_text?: string;
  timestamp: string;
  ucp?: {
    recent_transactions?: Array<{
      Date?: string;
      Amount?: number;
      Currency?: string;
      [key: string]: any;
    }>;
    all_transactions?: Array<{
      Date?: string;
      Amount?: number;
      Currency?: string;
      [key: string]: any;
    }>;
    financial_aggregates?: {
      [key: string]: any;
    };
    [key: string]: any;
  };
  feature_contributions?: {
    [key: string]: any;
  };
  model_version?: string;
  [key: string]: any; // Allow additional fields from enhanced fraud agent
}

export interface QueryMessage {
  id: string;
  type: "user" | "assistant" | "error";
  content: string;
  timestamp: Date;
  data?: FraudAnalysisResponse;
  partnerId?: string;
  isQuestion?: boolean; // true if it's a Q&A query, false if it's a risk assessment
}

export interface QAResponse {
  partner_id: string;
  question: string;
  answer: string;
  citations: Array<{
    type: string;
    data: Record<string, any>;
  }>;
  ucp_snapshot: Record<string, any>;
  source: string;
  status: "success";
}

export type RiskLevel = "high" | "medium" | "low";
