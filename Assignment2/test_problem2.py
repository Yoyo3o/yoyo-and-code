"""
Unit tests for Problem 2: BankAccount

Instructions:
Complete the unit test methods below using Python's unittest framework.
Your test methods must assert MULTIPLE ATTRIBUTES on the BankAccount object
(e.g., balance, status, transaction_history, summary) to verify state consistency.

Running tests:
    python -m unittest test_problem2.py -v
"""
import unittest
from problem2 import BankAccount


class TestBankAccount(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.account_empty = BankAccount("ACC001", "Alice", initial_balance=0.0, overdraft_limit=100.0)
        self.account_funded = BankAccount("ACC002", "Bob", initial_balance=200.0, overdraft_limit=50.0)

    def test_initial_state_multi_attributes(self):
        """
        Verify that a newly created account initializes all attributes correctly.
        Check balance, owner, status, overdraft_limit, transaction_history, and summary.
        """
        # Test empty account
        self.assertEqual(self.account_empty.account_id, "ACC001")
        self.assertEqual(self.account_empty.owner, "Alice")
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.overdraft_limit, 100.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(self.account_empty.transaction_history, [])
        self.assertEqual(
            self.account_empty.get_summary(),
            {
                "account_id": "ACC001",
                "owner": "Alice",
                "balance": 0.0,
                "status": "ACTIVE",
                "overdraft_limit": 100.0,
                "transaction_count": 0,
            },
        )

        # Test funded account
        self.assertEqual(self.account_funded.account_id, "ACC002")
        self.assertEqual(self.account_funded.owner, "Bob")
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(self.account_funded.overdraft_limit, 50.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 1)
        self.assertEqual(
            self.account_funded.transaction_history[0],
            {
                "type": "INITIAL_DEPOSIT",
                "amount": 200.0,
                "fee": 0.0,
                "balance_after": 200.0,
                "description": "Initial account opening deposit",
            },
        )
        self.assertEqual(self.account_funded.get_summary()["transaction_count"], 1)

    def test_deposit_updates_multiple_attributes(self):
        """
        Test that deposit correctly updates balance, transaction_history, and summary.
        """
        self.assertTrue(self.account_empty.deposit(150))

        self.assertEqual(self.account_empty.balance, 150.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[0]["type"], "DEPOSIT")
        self.assertEqual(self.account_empty.transaction_history[0]["amount"], 150.0)
        self.assertEqual(self.account_empty.transaction_history[0]["balance_after"], 150.0)
        self.assertEqual(self.account_empty.get_summary()["transaction_count"], 1)
        self.assertEqual(self.account_empty.get_summary()["balance"], 150.0)

    def test_withdrawal_within_balance_multi_attributes(self):
        """
        Test withdrawal when sufficient positive balance exists.
        """
        self.assertTrue(self.account_funded.withdraw(50, fee=2.50))

        self.assertEqual(self.account_funded.balance, 147.50)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 2)
        withdrawal = self.account_funded.transaction_history[-1]
        self.assertEqual(withdrawal["type"], "WITHDRAWAL")
        self.assertEqual(withdrawal["amount"], 50.0)
        self.assertEqual(withdrawal["fee"], 2.50)
        self.assertEqual(withdrawal["balance_after"], 147.50)
        self.assertEqual(self.account_funded.get_summary()["transaction_count"], 2)

    def test_overdraft_withdrawal_and_status_transition(self):
        """
        Test withdrawal that uses overdraft protection (balance becomes negative but >= -overdraft_limit).
        """
        self.assertTrue(self.account_empty.withdraw(50))

        self.assertEqual(self.account_empty.balance, -50.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[0]["type"], "WITHDRAWAL")
        self.assertEqual(self.account_empty.transaction_history[0]["balance_after"], -50.0)
        self.assertEqual(self.account_empty.get_summary()["status"], "OVERDRAWN")
        self.assertEqual(self.account_empty.get_summary()["transaction_count"], 1)

    def test_deposit_recovering_from_overdrawn_status(self):
        """
        Test that depositing enough money to bring balance >= 0 transitions status from OVERDRAWN to ACTIVE.
        """
        self.account_empty.withdraw(50)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")

        self.assertTrue(self.account_empty.deposit(50))

        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(len(self.account_empty.transaction_history), 2)
        self.assertEqual(self.account_empty.transaction_history[-1]["type"], "DEPOSIT")
        self.assertEqual(self.account_empty.transaction_history[-1]["balance_after"], 0.0)
        self.assertEqual(self.account_empty.get_summary()["status"], "ACTIVE")
        self.assertEqual(self.account_empty.get_summary()["transaction_count"], 2)

    def test_transfer_between_accounts_multi_attributes(self):
        """
        Test fund transfer between two accounts.
        """
        self.assertTrue(
            self.account_funded.transfer_to(
                self.account_empty, 50, transfer_fee=5
            )
        )

        self.assertEqual(self.account_funded.balance, 145.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 2)
        self.assertEqual(self.account_funded.transaction_history[-1]["type"], "WITHDRAWAL")
        self.assertEqual(self.account_funded.transaction_history[-1]["amount"], 50.0)
        self.assertEqual(self.account_funded.transaction_history[-1]["fee"], 5.0)
        self.assertEqual(self.account_empty.balance, 50.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[-1]["type"], "DEPOSIT")
        self.assertEqual(self.account_empty.get_summary()["transaction_count"], 1)

    def test_frozen_account_restrictions(self):
        """
        Test that a FROZEN account rejects deposits, withdrawals, and transfers with RuntimeError.
        """
        self.account_funded.freeze()

        self.assertEqual(self.account_funded.status, "FROZEN")
        with self.assertRaises(RuntimeError):
            self.account_funded.deposit(10)
        with self.assertRaises(RuntimeError):
            self.account_funded.withdraw(10)
        with self.assertRaises(RuntimeError):
            self.account_funded.transfer_to(self.account_empty, 10)

        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(len(self.account_funded.transaction_history), 1)
        self.assertEqual(self.account_funded.get_summary()["status"], "FROZEN")

        self.account_empty.freeze()
        with self.assertRaises(RuntimeError):
            self.account_funded.transfer_to(self.account_empty, 10)
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.status, "FROZEN")
        self.account_empty.unfreeze()
        self.assertEqual(self.account_empty.status, "ACTIVE")

    def test_invalid_operations_raise_exceptions(self):
        """
        Test exception handling
        """
        with self.assertRaises(ValueError):
            BankAccount("ACC003", "Carol", initial_balance=-1)
        with self.assertRaises(ValueError):
            BankAccount("ACC004", "Dan", overdraft_limit=-1)

        for invalid_amount in (0, -10):
            with self.assertRaises(ValueError):
                self.account_empty.deposit(invalid_amount)
            with self.assertRaises(ValueError):
                self.account_funded.withdraw(invalid_amount)
            with self.assertRaises(ValueError):
                self.account_funded.transfer_to(self.account_empty, invalid_amount)

        with self.assertRaises(ValueError):
            self.account_funded.withdraw(10, fee=-1)
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(101)
        with self.assertRaises(TypeError):
            self.account_funded.transfer_to("not an account", 10)

        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(self.account_empty.transaction_history, [])
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 1)


if __name__ == "__main__":
    unittest.main()
