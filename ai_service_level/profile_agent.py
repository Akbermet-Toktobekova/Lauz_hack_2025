"""
Profile Agent - Data Preparation Script
Extracts minimal data needed for fraud screening: identity, onboarding notes, and last 3 transactions.
"""

import pandas as pd
import os
from typing import Optional, Dict


class ProfileAgent:
    """
    Profile Agent that aggregates essential data for a partner_id.
    Acts as the MVP "Profile Agent" data source.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the Profile Agent with data directory.
        
        Args:
            data_dir: Path to directory containing CSV files
        """
        self.data_dir = data_dir
        self._load_data()
    
    def _load_data(self):
        """Load all required CSV files into memory."""
        self.partner_df = pd.read_csv(os.path.join(self.data_dir, "partner.csv"))
        self.onboarding_df = pd.read_csv(os.path.join(self.data_dir, "client_onboarding_notes.csv"))
        self.partner_role_df = pd.read_csv(os.path.join(self.data_dir, "partner_role.csv"))
        self.business_rel_df = pd.read_csv(os.path.join(self.data_dir, "business_rel.csv"))
        self.br_to_account_df = pd.read_csv(os.path.join(self.data_dir, "br_to_account.csv"))
        self.account_df = pd.read_csv(os.path.join(self.data_dir, "account.csv"))
        self.transactions_df = pd.read_csv(os.path.join(self.data_dir, "transactions.csv"))
    
    def get_profile_text(self, partner_id: str) -> str:
        """
        Get aggregated profile text for a partner_id.
        
        Args:
            partner_id: The partner ID to look up
            
        Returns:
            Single concatenated text block containing:
            1. Identity/Name data from partner.csv
            2. Onboarding_Note from client_onboarding_notes.csv
            3. Last 3 transactions summary
        """
        # 1. Get identity/name data from partner.csv
        partner_info = self._get_partner_info(partner_id)
        
        # 2. Get onboarding note
        onboarding_note = self._get_onboarding_note(partner_id)
        
        # 3. Get last 3 transactions
        transactions = self._get_last_transactions(partner_id, limit=3)
        
        # Combine into single text block
        profile_text = self._format_profile(partner_info, onboarding_note, transactions)
        
        return profile_text
    
    def _get_partner_info(self, partner_id: str) -> Optional[Dict]:
        """Extract identity/name data from partner.csv."""
        partner = self.partner_df[self.partner_df["partner_id"] == partner_id]
        
        if partner.empty:
            return None
        
        return {
            "partner_id": partner_id,
            "name": partner.iloc[0]["partner_name"],
            "gender": partner.iloc[0]["partner_gender"],
            "birth_year": partner.iloc[0]["partner_birth_year"],
            "phone": partner.iloc[0]["partner_phone_number"],
            "address": partner.iloc[0]["partner_address"],
            "open_date": partner.iloc[0]["partner_open_date"],
            "industry": partner.iloc[0]["industry_gic2_code"],
            "class": partner.iloc[0]["partner_class_code"]
        }
    
    def _get_onboarding_note(self, partner_id: str) -> Optional[str]:
        """Extract onboarding note from client_onboarding_notes.csv."""
        # Note: Column name is Partner_ID (capitalized) in the CSV
        note = self.onboarding_df[self.onboarding_df["Partner_ID"] == partner_id]
        
        if note.empty:
            return None
        
        return note.iloc[0]["Onboarding_Note"]
    
    def _get_last_transactions(self, partner_id: str, limit: int = 3) -> list:
        """
        Get last N transactions for a partner through the join chain:
        partner_id → partner_role (entity_id = br_id) → business_rel (br_id) 
        → br_to_account (br_id) → account (account_id) → transactions (Account ID)
        """
        # Step 1: Get business relationships (br_id) from partner_role
        partner_roles = self.partner_role_df[
            self.partner_role_df["partner_id"] == partner_id
        ]
        
        if partner_roles.empty:
            return []
        
        # Get br_ids from entity_id where entity_type is 'BR'
        br_ids = partner_roles[partner_roles["entity_type"] == "BR"]["entity_id"].unique()
        
        if len(br_ids) == 0:
            return []
        
        # Step 2: Get accounts through br_to_account
        accounts = self.br_to_account_df[
            self.br_to_account_df["br_id"].isin(br_ids)
        ]["account_id"].unique()
        
        if len(accounts) == 0:
            return []
        
        # Step 3: Get transactions for these accounts
        # Note: Column name is "Account ID" (with space) in transactions.csv
        transactions = self.transactions_df[
            self.transactions_df["Account ID"].isin(accounts)
        ].copy()
        
        # Sort by Date (most recent first) and take last N
        transactions["Date"] = pd.to_datetime(transactions["Date"])
        transactions = transactions.sort_values("Date", ascending=False).head(limit)
        
        # Convert to list of dicts
        return transactions.to_dict("records")
    
    def _format_profile(self, partner_info: Optional[Dict], 
                       onboarding_note: Optional[str], 
                       transactions: list) -> str:
        """Format all data into a single text block."""
        lines = []
        
        # Identity section
        lines.append("=== CLIENT IDENTITY ===")
        if partner_info:
            lines.append(f"Partner ID: {partner_info['partner_id']}")
            lines.append(f"Name: {partner_info['name']}")
            lines.append(f"Gender: {partner_info['gender']}")
            lines.append(f"Birth Year: {partner_info['birth_year']}")
            lines.append(f"Phone: {partner_info['phone']}")
            lines.append(f"Address: {partner_info['address']}")
            lines.append(f"Account Open Date: {partner_info['open_date']}")
            lines.append(f"Industry: {partner_info['industry']}")
            lines.append(f"Class: {partner_info['class']}")
        else:
            lines.append("Identity information not found.")
        
        lines.append("")
        
        # Onboarding note section
        lines.append("=== ONBOARDING NOTES ===")
        if onboarding_note:
            lines.append(onboarding_note)
        else:
            lines.append("No onboarding notes available.")
        
        lines.append("")
        
        # Transactions section
        lines.append("=== RECENT TRANSACTIONS (Last 3) ===")
        if transactions:
            for i, tx in enumerate(transactions, 1):
                lines.append(f"Transaction {i}:")
                lines.append(f"  Date: {tx.get('Date', 'N/A')}")
                lines.append(f"  Type: {tx.get('Debit/Credit', 'N/A')}")
                lines.append(f"  Amount: {tx.get('Amount', 'N/A')} {tx.get('Currency', 'N/A')}")
                lines.append(f"  Balance: {tx.get('Balance', 'N/A')}")
                lines.append(f"  Transfer Type: {tx.get('Transfer_Type', 'N/A')}")
                if tx.get('counterparty_Account_ID'):
                    lines.append(f"  Counterparty Account: {tx.get('counterparty_Account_ID')}")
                if tx.get('ext_counterparty_Account_ID'):
                    lines.append(f"  External Counterparty: {tx.get('ext_counterparty_Account_ID')}")
                if tx.get('ext_counterparty_country'):
                    lines.append(f"  Counterparty Country: {tx.get('ext_counterparty_country')}")
                lines.append("")
        else:
            lines.append("No recent transactions found.")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    agent = ProfileAgent(data_dir="data")
    
    # Test with a sample partner_id
    test_partner_id = "96a660ff-08e0-49c1-be6d-bb22a84e742e"
    profile_text = agent.get_profile_text(test_partner_id)
    print(profile_text)

