import random
import string
import time

class OTPGenerator:
    def __init__(self, expiry_seconds=300):
        self.expiry_seconds = expiry_seconds
        self.otp_store = {}

    def generate_otp(self, identifier: str, length: int = 6) -> str:
        """
        Generates a numeric OTP for a given identifier (e.g., email or phone).
        """
        otp = ''.join(random.choices(string.digits, k=length))
        self.otp_store[identifier] = {
            'otp': otp,
            'timestamp': time.time()
        }
        return otp

    def verify_otp(self, identifier: str, otp: str) -> bool:
        """
        Verifies if the provided OTP is valid and not expired for the identifier.
        """
        record = self.otp_store.get(identifier)
        if not record:
            return False
            
        if time.time() - record['timestamp'] > self.expiry_seconds:
            del self.otp_store[identifier]  # Clean up expired OTP
            return False
            
        if record['otp'] == otp:
            del self.otp_store[identifier]  # OTP used successfully, remove it
            return True
            
        return False

# Example usage:
# generator = OTPGenerator(expiry_seconds=300)
# otp = generator.generate_otp("user@example.com")
# is_valid = generator.verify_otp("user@example.com", otp)
