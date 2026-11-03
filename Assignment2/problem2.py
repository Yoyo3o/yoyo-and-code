"""
Problem 2: Bank Account Management System (Developed by AI)
"""
from typing import List, Dict, Any, Optional


class BankAccount:
    """
    A bank account model with overdraft protection, status transitions,
    and detailed transaction tracking.

    Attributes:
        account_id (str): Unique identifier for the account.
        owner (str): Account holder's name.
        balance (float): Current balance.
        overdraft_limit (float): Maximum allowed negative balance (default: 100.0).
        status (str): Current status ("ACTIVE", "OVERDRAWN", "FROZEN").
        transaction_history (List[Dict[str, Any]]): List of recorded transactions.
    """

    def __init__(self, account_id: str, owner: str, initial_balance: float = 0.0, overdraft_limit: float = 100.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        if overdraft_limit < 0:
            raise ValueError("Overdraft limit cannot be negative")

        self.account_id = account_id
        self.owner = owner
        self.balance = float(initial_balance)
        self.overdraft_limit = float(overdraft_limit)
        self.status = "ACTIVE"
        self.transaction_history: List[Dict[str, Any]] = []

        if initial_balance > 0:
            self.transaction_history.append({
                "type": "INITIAL_DEPOSIT",
                "amount": float(initial_balance),
                "fee": 0.0,
                "balance_after": self.balance,
                "description": "Initial account opening deposit"
            })

    def deposit(self, amount: float) -> bool:
        """
        Deposit money into the account.
        
        Args:
            amount (float): Amount to deposit (must be > 0).
            
        Returns:
            bool: True if deposit was successful.
            
        Raises:
            ValueError: If amount <= 0.
            RuntimeError: If account is FROZEN.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        if self.status == "FROZEN":
            raise RuntimeError("Cannot deposit into a frozen account")

        self.balance += float(amount)
        if self.balance >= 0 and self.status == "OVERDRAWN":
            self.status = "ACTIVE"

        self.transaction_history.append({
            "type": "DEPOSIT",
            "amount": float(amount),
            "fee": 0.0,
            "balance_after": self.balance,
            "description": f"Deposit of ${amount:.2f}"
        })
        return True

    def withdraw(self, amount: float, fee: float = 0.0) -> bool:
        """
        Withdraw money from the account with optional transaction fee.
        
        Args:
            amount (float): Amount to withdraw (must be > 0).
            fee (float): Additional withdrawal fee (default: 0.0, must be >= 0).
            
        Returns:
            bool: True if withdrawal was successful.
            
        Raises:
            ValueError: If amount <= 0, fee < 0, or total exceeds balance + overdraft_limit.
            RuntimeError: If account is FROZEN.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        if self.status == "FROZEN":
            raise RuntimeError("Cannot withdraw from a frozen account")

        total_deduction = float(amount + fee)
        if self.balance - total_deduction < -self.overdraft_limit:
            raise ValueError(f"Insufficient funds: withdrawal would exceed overdraft limit of ${self.overdraft_limit:.2f}")

        self.balance -= total_deduction
        if self.balance < 0:
            self.status = "OVERDRAWN"

        self.transaction_history.append({
            "type": "WITHDRAWAL",
            "amount": float(amount),
            "fee": float(fee),
            "balance_after": self.balance,
            "description": f"Withdrawal of ${amount:.2f} (Fee: ${fee:.2f})"
        })
        return True

    def transfer_to(self, target_account: "BankAccount", amount: float, transfer_fee: float = 0.0) -> bool:
        """
        Transfer funds to another BankAccount.
        
        Args:
            target_account (BankAccount): The recipient account.
            amount (float): Amount to transfer (must be > 0).
            transfer_fee (float): Fee charged to the sender (default: 0.0).
            
        Returns:
            bool: True if transfer succeeded.
            
        Raises:
            TypeError: If target_account is not a BankAccount.
            RuntimeError: If either account is FROZEN.
            ValueError: If amount <= 0 or sender has insufficient funds.
        """
        if not isinstance(target_account, BankAccount):
            raise TypeError("Target account must be an instance of BankAccount")
        if self.status == "FROZEN":
            raise RuntimeError("Cannot transfer from a frozen account")
        if target_account.status == "FROZEN":
            raise RuntimeError("Cannot transfer to a frozen account")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        # Deduct from sender
        self.withdraw(amount, fee=transfer_fee)

        # Deposit to recipient
        target_account.deposit(amount)
        return True

    def freeze(self) -> None:
        """Freeze the account, preventing deposits and withdrawals."""
        self.status = "FROZEN"

    def unfreeze(self) -> None:
        """Unfreeze the account and restore appropriate active or overdrawn status."""
        self.status = "OVERDRAWN" if self.balance < 0 else "ACTIVE"

    def get_summary(self) -> Dict[str, Any]:
        """
        Return a summary dictionary of current account state.
        """
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": round(self.balance, 2),
            "status": self.status,
            "overdraft_limit": self.overdraft_limit,
            "transaction_count": len(self.transaction_history)
        }
