/**
 * API service layer for fraud analysis
 * Connects to Flask backend at backend/app.py
 * 
 * Backend Endpoints:
 * - GET /health - Health check
 * - POST /api/assess-risk - Risk assessment
 * - POST /api/profile - Partner profile
 */

import { AssessRiskResponse, ProfileResponse, HealthResponse, FraudAnalysisResponse, ApiError } from "@/types/fraud";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5001";

/**
 * Check backend health status
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to the backend server. Make sure Flask is running on port 5001.");
    }
    throw error;
  }
};

/**
 * Assess fraud/AML risk for a partner
 * 
 * @param partnerId - Partner UUID identifier
 * @returns Risk assessment response
 */
export const assessRisk = async (partnerId: string): Promise<AssessRiskResponse> => {
  if (!partnerId || typeof partnerId !== "string" || partnerId.trim() === "") {
    throw new Error("partner_id is required and must be a non-empty string");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/assess-risk`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ partner_id: partnerId.trim() }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `API request failed: ${response.status} ${response.statusText}`,
      }));
      const errorMessage = errorData.error || errorData.message || `API request failed: ${response.status}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to the backend server. Make sure Flask is running on port 5001.");
    }
    throw error;
  }
};

/**
 * Get partner profile data
 * 
 * @param partnerId - Partner UUID identifier
 * @returns Profile response
 */
export const getProfile = async (partnerId: string): Promise<ProfileResponse> => {
  if (!partnerId || typeof partnerId !== "string" || partnerId.trim() === "") {
    throw new Error("partner_id is required and must be a non-empty string");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/profile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ partner_id: partnerId.trim() }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `API request failed: ${response.status} ${response.statusText}`,
      }));
      const errorMessage = errorData.error || errorData.message || `API request failed: ${response.status}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to the backend server.");
    }
    throw error;
  }
};

/**
 * Combined function to fetch both risk assessment and profile in parallel
 * 
 * @param partnerId - Partner UUID identifier
 * @returns Combined fraud analysis response
 */
export const analyzeFraudRisk = async (partnerId: string): Promise<FraudAnalysisResponse> => {
  try {
    const [riskData, profileData] = await Promise.all([
      assessRisk(partnerId),
      getProfile(partnerId),
    ]);

    return {
      partner_id: partnerId,
      risk_score: riskData.risk_score,
      rationale: riskData.rationale,
      raw_response: riskData.raw_response,
      profile_text: profileData.profile_text,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    throw error;
  }
};

/**
 * Ask a question about a customer using RAG
 * 
 * @param partnerId - Partner UUID identifier
 * @param question - Natural language question
 * @returns Q&A response with answer and citations
 */
export const askQuestion = async (partnerId: string, question: string): Promise<any> => {
  if (!partnerId || typeof partnerId !== "string" || partnerId.trim() === "") {
    throw new Error("partner_id is required and must be a non-empty string");
  }
  if (!question || typeof question !== "string" || question.trim() === "") {
    throw new Error("question is required and must be a non-empty string");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/qa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        partner_id: partnerId.trim(),
        question: question.trim()
      }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `API request failed: ${response.status} ${response.statusText}`,
      }));
      const errorMessage = errorData.error || errorData.message || `API request failed: ${response.status}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to the backend server. Make sure Flask is running on port 5001.");
    }
    throw error;
  }
};

/**
 * Chatbot endpoint - accepts natural language and handles everything
 * 
 * @param message - Natural language message (can include Partner ID or reference previous conversation)
 * @param conversationHistory - Previous messages in the conversation
 * @returns Chatbot response with action type and data
 */
export const sendChatMessage = async (
  message: string, 
  conversationHistory?: Array<{content: string; partner_id?: string}>
): Promise<any> => {
  if (!message || typeof message !== "string" || message.trim() === "") {
    throw new Error("message is required and must be a non-empty string");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/chatbot`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        message: message.trim(),
        conversation_history: conversationHistory || []
      }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `API request failed: ${response.status} ${response.statusText}`,
      }));
      const errorMessage = errorData.error || errorData.message || `API request failed: ${response.status}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error("Network error: Unable to connect to the backend server. Make sure Flask is running on port 5001.");
    }
    throw error;
  }
};
