from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

def generate_vapid_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem, public_key_pem

def urlsafe_base64_encode(data):
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def remove_pem_headers(pem_data):
    return b''.join(pem_data.split(b'\n')[1:-1])

private_key_pem, public_key_pem = generate_vapid_keypair()

# Remove PEM headers and footers
private_key_bytes = remove_pem_headers(private_key_pem)
public_key_bytes = remove_pem_headers(public_key_pem)

# URL-safe Base64 encode the key bytes
vapid_private_key = urlsafe_base64_encode(private_key_bytes)
vapid_public_key = urlsafe_base64_encode(public_key_bytes)

print(f"Public Key: {vapid_public_key}")
print(f"Private Key: {vapid_private_key}")
