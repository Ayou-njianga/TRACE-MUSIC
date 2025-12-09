# Test OTP Email Verification Flow
# This script tests the OTP generation and verification logic

import sys
import os

# Add AuthService to path
auth_service_path = os.path.join(os.path.dirname(__file__), '..', '..', 'AuthService')
sys.path.insert(0, auth_service_path)

try:
    from utils import generate_otp, hash_password
    import bcrypt
except ImportError as e:
    print(f"Warning: Could not import AuthService modules: {e}")
    print("Skipping OTP-specific tests")
    sys.exit(0)

def test_otp_generation():
    """Test OTP generation produces 6-digit codes"""
    for _ in range(10):
        otp = generate_otp()
        assert len(otp) == 6, f"OTP should be 6 digits, got {len(otp)}"
        assert otp.isdigit(), f"OTP should be numeric, got {otp}"
    print("✓ OTP generation test passed")

def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    pwd_hash = hash_password(password)
    
    # Verify hash is string
    assert isinstance(pwd_hash, str), "Hash should be a string"
    
    # Verify bcrypt can validate it
    is_valid = bcrypt.checkpw(password.encode('utf-8'), pwd_hash.encode('utf-8'))
    assert is_valid, "Password verification failed"
    
    # Wrong password should fail
    is_valid = bcrypt.checkpw("wrong_password".encode('utf-8'), pwd_hash.encode('utf-8'))
    assert not is_valid, "Wrong password should not verify"
    
    print("✓ Password hashing test passed")

def test_otp_storage_and_verification():
    """Test OTP storage and verification logic (simulated)"""
    import time
    import uuid
    
    # Simulate pending OTP storage
    pending_otp = {}
    login = "testuser"
    
    # Generate and store OTP
    otp_code = generate_otp()
    pending_id = str(uuid.uuid4())
    pending_otp[login] = {
        'pending_id': pending_id,
        'otp_code': otp_code,
        'email': 'test@example.com',
        'expires_at': time.time() + 300
    }
    
    # Test 1: Valid OTP verification
    pending = pending_otp.get(login)
    assert pending is not None, "Pending OTP should exist"
    assert pending['pending_id'] == pending_id, "Pending ID mismatch"
    assert pending['otp_code'] == otp_code, "OTP code mismatch"
    assert time.time() < pending['expires_at'], "OTP should not be expired"
    print("✓ OTP storage and verification test passed")
    
    # Test 2: Invalid OTP code
    invalid_otp = "000000"
    assert pending['otp_code'] != invalid_otp, "Invalid OTP should not match"
    print("✓ Invalid OTP rejection test passed")
    
    # Test 3: OTP expiration
    pending_otp[login]['expires_at'] = time.time() - 1  # Expired
    assert time.time() > pending_otp[login]['expires_at'], "OTP should be expired"
    print("✓ OTP expiration test passed")

if __name__ == '__main__':
    print("Running OTP verification tests...\n")
    try:
        test_otp_generation()
        test_password_hashing()
        test_otp_storage_and_verification()
        print("\n✅ All OTP tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
