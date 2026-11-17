from banking_app.security import hash_password, verify_password

def test_password_hash_and_verify():
    hashed, salt = hash_password("StrongPass123")
    assert verify_password("StrongPass123", hashed, salt)
    assert not verify_password("WrongPass123", hashed, salt)
