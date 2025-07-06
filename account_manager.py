import json
import os

ACCOUNTS_FILE = "accounts.json"

class AccountManager:
    def __init__(self):
        self.accounts = self.load_accounts()
        self.current_account = None

    def load_accounts(self):
        if not os.path.exists(ACCOUNTS_FILE):
            return {}
        with open(ACCOUNTS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_accounts(self):
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(self.accounts, f, indent=4)

    def create_account(self, name):
        if name in self.accounts:
            return False # Account already exists
        
        account_id = len(self.accounts) + 1
        self.accounts[name] = {
            "id": account_id,
            "highscore": 0,
            "save_file": f"save_{name}.json"
        }
        self.save_accounts()
        return True

    def get_account(self, name):
        return self.accounts.get(name)

    def set_current_account(self, name):
        if name in self.accounts:
            self.current_account = name
            return True
        return False

    def get_current_account_data(self):
        if self.current_account:
            return self.accounts[self.current_account]
        return None

account_manager = AccountManager()
