"""
Unified Customer Profile (UCP) - Single Source of Truth
Central artifact that unifies all customer data for fraud detection and compliance Q&A
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import os


class UnifiedCustomerProfile:
    """
    Unified Customer Profile - The central artifact that combines:
    - Canonical Identity (Entity Resolution)
    - Static Profile Data
    - Account & Device Data
    - Financial & Transactional Aggregates
    - Risk & Audit Metadata
    """
    
    def __init__(self, partner_id: str):
        """
        Initialize UCP for a partner.
        
        Args:
            partner_id: The canonical partner ID
        """
        self.partner_id = partner_id
        self.created_at = datetime.now().isoformat()
        self.profile_data = {}
        self.transaction_aggregates = {}
        self.risk_metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert UCP to dictionary for storage/API."""
        return {
            "canonical_id": self.partner_id,
            "created_at": self.created_at,
            "identity": self.profile_data.get("identity", {}),
            "static_profile": self.profile_data.get("static_profile", {}),
            "account_data": self.profile_data.get("account_data", {}),
            "financial_aggregates": self.transaction_aggregates,
            "risk_metadata": self.risk_metadata,
            "onboarding_notes": self.profile_data.get("onboarding_notes", ""),
            "recent_transactions": self.profile_data.get("recent_transactions", [])
        }
    
    def to_text(self) -> str:
        """Convert UCP to text format for LLM context."""
        lines = []
        
        # Identity
        identity = self.profile_data.get("identity", {})
        lines.append("=== CANONICAL IDENTITY ===")
        lines.append(f"Partner ID: {self.partner_id}")
        lines.append(f"Name: {identity.get('name', 'N/A')}")
        lines.append(f"KYC Status: {identity.get('kyc_status', 'N/A')}")
        lines.append(f"Onboarding Date: {identity.get('onboarding_date', 'N/A')}")
        lines.append("")
        
        # Static Profile
        static = self.profile_data.get("static_profile", {})
        lines.append("=== STATIC PROFILE DATA ===")
        for key, value in static.items():
            if value:
                lines.append(f"{key}: {value}")
        lines.append("")
        
        # Financial Aggregates
        lines.append("=== FINANCIAL AGGREGATES ===")
        for key, value in self.transaction_aggregates.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        
        # Recent Transactions
        lines.append("=== RECENT TRANSACTIONS ===")
        for tx in self.profile_data.get("recent_transactions", [])[:5]:
            lines.append(f"Date: {tx.get('Date', 'N/A')}, "
                        f"Amount: {tx.get('Amount', 'N/A')} {tx.get('Currency', 'N/A')}, "
                        f"Type: {tx.get('Debit/Credit', 'N/A')}")
        lines.append("")
        
        # Risk Metadata
        if self.risk_metadata:
            lines.append("=== RISK & AUDIT METADATA ===")
            lines.append(f"Latest Risk Score: {self.risk_metadata.get('risk_score', 'N/A')}/100")
            lines.append(f"Model Version: {self.risk_metadata.get('model_version', 'N/A')}")
            if self.risk_metadata.get('explanation'):
                lines.append(f"Explanation: {self.risk_metadata.get('explanation')}")
        
        return "\n".join(lines)


class UCPBuilder:
    """
    Builder class to construct Unified Customer Profiles from raw data.
    Implements Entity Resolution and Feature Engineering.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize UCP Builder with data directory."""
        self.data_dir = data_dir
        self._load_data()
    
    def _load_data(self):
        """Load all required CSV files."""
        self.partner_df = pd.read_csv(os.path.join(self.data_dir, "partner.csv"))
        self.onboarding_df = pd.read_csv(os.path.join(self.data_dir, "client_onboarding_notes.csv"))
        self.partner_role_df = pd.read_csv(os.path.join(self.data_dir, "partner_role.csv"))
        self.business_rel_df = pd.read_csv(os.path.join(self.data_dir, "business_rel.csv"))
        self.br_to_account_df = pd.read_csv(os.path.join(self.data_dir, "br_to_account.csv"))
        self.account_df = pd.read_csv(os.path.join(self.data_dir, "account.csv"))
        self.transactions_df = pd.read_csv(os.path.join(self.data_dir, "transactions.csv"))
    
    def build_ucp(self, partner_id: str) -> UnifiedCustomerProfile:
        """
        Build a Unified Customer Profile for a partner.
        
        Args:
            partner_id: The partner ID to build UCP for
            
        Returns:
            UnifiedCustomerProfile object
        """
        ucp = UnifiedCustomerProfile(partner_id)
        
        # I. Canonical Identity
        identity = self._extract_identity(partner_id)
        ucp.profile_data["identity"] = identity
        
        # II. Static Profile Data
        static_profile = self._extract_static_profile(partner_id)
        ucp.profile_data["static_profile"] = static_profile
        
        # III. Account & Device Data
        account_data = self._extract_account_data(partner_id)
        ucp.profile_data["account_data"] = account_data
        
        # IV. Financial & Transactional Aggregates
        financial_aggregates = self._calculate_financial_aggregates(partner_id)
        ucp.transaction_aggregates = financial_aggregates
        
        # V. Recent Transactions
        recent_tx = self._get_recent_transactions(partner_id, limit=5)
        ucp.profile_data["recent_transactions"] = recent_tx
        
        # VI. Onboarding Notes
        onboarding_note = self._get_onboarding_note(partner_id)
        ucp.profile_data["onboarding_notes"] = onboarding_note
        
        return ucp
    
    def _extract_identity(self, partner_id: str) -> Dict:
        """Extract canonical identity information."""
        partner = self.partner_df[self.partner_df["partner_id"] == partner_id]
        
        if partner.empty:
            return {}
        
        p = partner.iloc[0]
        return {
            "canonical_id": partner_id,
            "name": p.get("partner_name", ""),
            "kyc_status": "verified" if p.get("partner_open_date") else "pending",
            "onboarding_date": p.get("partner_open_date", ""),
            "industry": p.get("industry_gic2_code", ""),
            "class": p.get("partner_class_code", "")
        }
    
    def _extract_static_profile(self, partner_id: str) -> Dict:
        """Extract static profile data."""
        partner = self.partner_df[self.partner_df["partner_id"] == partner_id]
        
        if partner.empty:
            return {}
        
        p = partner.iloc[0]
        return {
            "full_name": p.get("partner_name", ""),
            "dob": p.get("partner_birth_year", ""),
            "gender": p.get("partner_gender", ""),
            "primary_address": p.get("partner_address", ""),
            "phone": p.get("partner_phone_number", ""),
            "open_date": p.get("partner_open_date", ""),
            "close_date": p.get("partner_close_date", "")
        }
    
    def _extract_account_data(self, partner_id: str) -> Dict:
        """Extract account and device data."""
        # Get business relationships
        partner_roles = self.partner_role_df[
            self.partner_role_df["partner_id"] == partner_id
        ]
        
        br_ids = partner_roles[partner_roles["entity_type"] == "BR"]["entity_id"].unique()
        
        if len(br_ids) == 0:
            return {"account_count": 0, "accounts": []}
        
        # Get accounts
        accounts = self.br_to_account_df[
            self.br_to_account_df["br_id"].isin(br_ids)
        ]
        
        account_ids = accounts["account_id"].unique()
        account_details = self.account_df[self.account_df["account_id"].isin(account_ids)]
        
        return {
            "account_count": len(account_ids),
            "accounts": account_details.to_dict("records") if not account_details.empty else [],
            "account_status": "active" if len(account_ids) > 0 else "inactive"
        }
    
    def _calculate_financial_aggregates(self, partner_id: str) -> Dict:
        """Calculate financial aggregates (feature engineering)."""
        # Get transactions
        transactions = self._get_all_transactions(partner_id)
        
        if not transactions:
            return {
                "total_spending_30d": 0,
                "total_spending_90d": 0,
                "avg_tx_value_90d": 0,
                "velocity_tx_per_hour": 0,
                "tx_count_30d": 0,
                "tx_count_90d": 0,
                "max_tx_amount": 0,
                "min_tx_amount": 0
            }
        
        df = pd.DataFrame(transactions)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce')
        
        now = pd.Timestamp.now()
        df_30d = df[df["Date"] >= (now - pd.Timedelta(days=30))]
        df_90d = df[df["Date"] >= (now - pd.Timedelta(days=90))]
        
        # Calculate velocity (transactions per hour in last 30 days)
        if len(df_30d) > 0:
            time_span_hours = (df_30d["Date"].max() - df_30d["Date"].min()).total_seconds() / 3600
            velocity = len(df_30d) / max(time_span_hours, 1)
        else:
            velocity = 0
        
        # Calculate aggregates
        debit_30d = df_30d[df_30d["Debit/Credit"] == "debit"]["Amount"].sum()
        debit_90d = df_90d[df_90d["Debit/Credit"] == "debit"]["Amount"].sum()
        
        return {
            "total_spending_30d": float(debit_30d) if not pd.isna(debit_30d) else 0,
            "total_spending_90d": float(debit_90d) if not pd.isna(debit_90d) else 0,
            "avg_tx_value_90d": float(df_90d["Amount"].mean()) if len(df_90d) > 0 else 0,
            "velocity_tx_per_hour": velocity,
            "tx_count_30d": len(df_30d),
            "tx_count_90d": len(df_90d),
            "max_tx_amount": float(df["Amount"].max()) if len(df) > 0 else 0,
            "min_tx_amount": float(df["Amount"].min()) if len(df) > 0 else 0
        }
    
    def _get_all_transactions(self, partner_id: str) -> List[Dict]:
        """Get all transactions for a partner."""
        partner_roles = self.partner_role_df[
            self.partner_role_df["partner_id"] == partner_id
        ]
        
        br_ids = partner_roles[partner_roles["entity_type"] == "BR"]["entity_id"].unique()
        
        if len(br_ids) == 0:
            return []
        
        accounts = self.br_to_account_df[
            self.br_to_account_df["br_id"].isin(br_ids)
        ]["account_id"].unique()
        
        if len(accounts) == 0:
            return []
        
        transactions = self.transactions_df[
            self.transactions_df["Account ID"].isin(accounts)
        ]
        
        return transactions.to_dict("records")
    
    def _get_recent_transactions(self, partner_id: str, limit: int = 5) -> List[Dict]:
        """Get recent transactions."""
        transactions = self._get_all_transactions(partner_id)
        
        if not transactions:
            return []
        
        df = pd.DataFrame(transactions)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date", ascending=False).head(limit)
        
        return df.to_dict("records")
    
    def _get_onboarding_note(self, partner_id: str) -> str:
        """Get onboarding notes."""
        note = self.onboarding_df[self.onboarding_df["Partner_ID"] == partner_id]
        
        if note.empty:
            return ""
        
        return note.iloc[0]["Onboarding_Note"]

