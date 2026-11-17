import secrets
from .database import connect
from .security import hash_password, verify_password

class BankingError(Exception):
    pass

def register_customer(name: str, username: str, password: str):
    name, username = name.strip(), username.strip().lower()
    if not name or not username or len(password) < 8:
        raise BankingError("Enter a name, username, and password of at least 8 characters.")
    password_hash, salt = hash_password(password)
    account_number = "BA" + secrets.token_hex(5).upper()
    try:
        with connect() as conn:
            cur = conn.execute(
                "INSERT INTO customers(name, username, password_hash, salt) VALUES(?,?,?,?)",
                (name, username, password_hash, salt)
            )
            customer_id = cur.lastrowid
            conn.execute(
                "INSERT INTO accounts(customer_id, account_number, balance) VALUES(?,?,0)",
                (customer_id, account_number)
            )
        return account_number
    except Exception as exc:
        if "UNIQUE constraint failed: customers.username" in str(exc):
            raise BankingError("That username is already registered.") from exc
        raise

def authenticate(username: str, password: str):
    with connect() as conn:
        row = conn.execute(
            """SELECT c.id, c.name, c.password_hash, c.salt, a.id AS account_id,
                      a.account_number, a.balance
               FROM customers c JOIN accounts a ON a.customer_id = c.id
               WHERE c.username = ?""",
            (username.strip().lower(),)
        ).fetchone()
    if row and verify_password(password, row["password_hash"], row["salt"]):
        return dict(row)
    return None

def get_account(account_id: int):
    with connect() as conn:
        row = conn.execute(
            "SELECT account_number, balance FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
    if not row:
        raise BankingError("Account not found.")
    return dict(row)

def deposit(account_id: int, amount: float):
    if amount <= 0:
        raise BankingError("Amount must be greater than zero.")
    with connect() as conn:
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, account_id))
        conn.execute(
            "INSERT INTO transactions(account_id, transaction_type, amount, note) VALUES(?,?,?,?)",
            (account_id, "DEPOSIT", amount, "Cash deposit")
        )

def withdraw(account_id: int, amount: float):
    if amount <= 0:
        raise BankingError("Amount must be greater than zero.")
    with connect() as conn:
        row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
        if not row:
            raise BankingError("Account not found.")
        if row["balance"] < amount:
            raise BankingError("Insufficient balance.")
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, account_id))
        conn.execute(
            "INSERT INTO transactions(account_id, transaction_type, amount, note) VALUES(?,?,?,?)",
            (account_id, "WITHDRAWAL", amount, "Cash withdrawal")
        )

def transfer(from_account_id: int, recipient_account_number: str, amount: float):
    if amount <= 0:
        raise BankingError("Amount must be greater than zero.")
    with connect() as conn:
        sender = conn.execute(
            "SELECT balance, account_number FROM accounts WHERE id = ?", (from_account_id,)
        ).fetchone()
        recipient = conn.execute(
            "SELECT id FROM accounts WHERE account_number = ?", (recipient_account_number.strip().upper(),)
        ).fetchone()
        if not sender or not recipient:
            raise BankingError("Sender or recipient account was not found.")
        if recipient["id"] == from_account_id:
            raise BankingError("You cannot transfer money to your own account.")
        if sender["balance"] < amount:
            raise BankingError("Insufficient balance.")
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_account_id))
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, recipient["id"]))
        conn.execute(
            "INSERT INTO transactions(account_id, transaction_type, amount, note) VALUES(?,?,?,?)",
            (from_account_id, "TRANSFER_OUT", amount, f"To {recipient_account_number.upper()}")
        )
        conn.execute(
            "INSERT INTO transactions(account_id, transaction_type, amount, note) VALUES(?,?,?,?)",
            (recipient["id"], "TRANSFER_IN", amount, f"From {sender['account_number']}")
        )

def transaction_history(account_id: int, limit: int = 20):
    with connect() as conn:
        rows = conn.execute(
            """SELECT transaction_type, amount, note, created_at
               FROM transactions WHERE account_id = ?
               ORDER BY id DESC LIMIT ?""",
            (account_id, limit)
        ).fetchall()
    return [dict(row) for row in rows]
