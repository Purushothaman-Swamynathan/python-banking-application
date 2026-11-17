# Python Banking Application

A beginner-friendly, menu-driven banking application built with Python and SQLite.

## Features
- Customer registration and login
- Password hashing with PBKDF2-HMAC-SHA256
- Automatic account-number generation
- Deposit and withdrawal
- Account-to-account transfer
- Balance enquiry
- Transaction history
- SQLite database with relational tables

## Requirements
- Python 3.10 or later
- No third-party packages required to run the application

## Run
From this project folder:

```bash
python main.py
```

Register two users to test transfers. Save the recipient's account number shown at registration.

## Run tests (optional)
```bash
python -m pip install pytest
python -m pytest
```

## Database
The application creates `banking.db` automatically on first launch. It contains:
- `customers`
- `accounts`
- `transactions`

## Important scope note
This is an educational/demo project, not production banking software. It does not connect to a real bank, payment gateway, KYC service, or core banking system. Do not use real customer credentials or financial information.

## Suggested future enhancements
- GUI using Tkinter or a web interface using Flask/Django
- Admin dashboard and account statements
- Unit tests for deposits, withdrawals and transfers
- Decimal-based money handling and stronger transaction audit controls
- Role-based access, rate limiting, secure deployment and backups
