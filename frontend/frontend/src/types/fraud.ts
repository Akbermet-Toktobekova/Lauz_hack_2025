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
  raw_response: string;
  profile_text: string;
  timestamp: string;
}

export interface QueryMessage {
  id: string;
  type: "user" | "assistant" | "error";
  content: string;
  timestamp: Date;
  data?: FraudAnalysisResponse;
  partnerId?: string;
}

export type RiskLevel = "high" | "medium" | "low";
