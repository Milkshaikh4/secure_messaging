import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from dotenv import load_dotenv

load_dotenv()

AES_KEY = os.getenv("AES_KEY", "32bytessecretkey000000000000000000")  

def encrypt_message(plaintext: str) -> str:
    """
    Encrypts plaintext using AES-256 in CBC mode with a random IV.
    Returns a base64-encoded string containing IV + ciphertext.
    """
    iv = get_random_bytes(16)  # 128-bit IV
    cipher = AES.new(AES_KEY.encode("utf-8"), AES.MODE_CBC, iv=iv)

    # PKCS7 padding
    block_size = AES.block_size
    padding_length = block_size - (len(plaintext.encode("utf-8")) % block_size)
    padded_plaintext = plaintext + (chr(padding_length) * padding_length)

    encrypted_bytes = cipher.encrypt(padded_plaintext.encode("utf-8"))

    # Prepend IV to the encrypted bytes
    iv_and_ciphertext = iv + encrypted_bytes

    # Base64-encode
    return base64.b64encode(iv_and_ciphertext).decode("utf-8")


def decrypt_message(base64_ciphertext: str) -> str:
    """
    Decrypts a base64-encoded string containing IV + ciphertext, 
    returns the original plaintext (after unpadding).
    """
    raw_data = base64.b64decode(base64_ciphertext)
    iv = raw_data[:16]
    ciphertext = raw_data[16:]

    cipher = AES.new(AES_KEY.encode("utf-8"), AES.MODE_CBC, iv=iv)
    decrypted_padded_bytes = cipher.decrypt(ciphertext)

    # Remove PKCS7 padding
    padding_length = decrypted_padded_bytes[-1]
    decrypted_bytes = decrypted_padded_bytes[:-padding_length]

    return decrypted_bytes.decode("utf-8")
