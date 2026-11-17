from getpass import getpass
from .database import initialize_database
from .service import (
    BankingError, register_customer, authenticate, get_account,
    deposit, withdraw, transfer, transaction_history
)

def read_amount():
    try:
        amount = round(float(input("Amount (₹): ").strip()), 2)
        if amount <= 0:
            raise ValueError
        return amount
    except ValueError:
        print("Please enter a valid amount greater than zero.")
        return None

def customer_menu(user):
    while True:
        account = get_account(user["account_id"])
        print(f"\nWelcome, {user['name']} | Account: {account['account_number']}")
        print(f"Available balance: ₹{account['balance']:.2f}")
        print("1. Deposit\n2. Withdraw\n3. Transfer\n4. Transaction history\n5. Logout")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                amount = read_amount()
                if amount is not None:
                    deposit(user["account_id"], amount)
                    print("Deposit successful.")
            elif choice == "2":
                amount = read_amount()
                if amount is not None:
                    withdraw(user["account_id"], amount)
                    print("Withdrawal successful.")
            elif choice == "3":
                recipient = input("Recipient account number: ")
                amount = read_amount()
                if amount is not None:
                    transfer(user["account_id"], recipient, amount)
                    print("Transfer successful.")
            elif choice == "4":
                rows = transaction_history(user["account_id"])
                if not rows:
                    print("No transactions yet.")
                for row in rows:
                    print(f"{row['created_at']} | {row['transaction_type']:<12} | "
                          f"₹{row['amount']:.2f} | {row['note']}")
            elif choice == "5":
                break
            else:
                print("Choose a valid menu option.")
        except BankingError as exc:
            print(f"Error: {exc}")

def main():
    initialize_database()
    while True:
        print("\n========== PYTHON BANKING APPLICATION ==========")
        print("1. Register\n2. Login\n3. Exit")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                name = input("Full name: ")
                username = input("Create username: ")
                password = getpass("Create password (minimum 8 characters): ")
                account_number = register_customer(name, username, password)
                print(f"Registration successful. Your account number is {account_number}")
            elif choice == "2":
                username = input("Username: ")
                password = getpass("Password: ")
                user = authenticate(username, password)
                if user:
                    customer_menu(user)
                else:
                    print("Invalid username or password.")
            elif choice == "3":
                print("Thank you for using the application.")
                break
            else:
                print("Choose a valid menu option.")
        except BankingError as exc:
            print(f"Error: {exc}")

if __name__ == "__main__":
    main()
