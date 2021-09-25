import nacl.secret as salt
from nacl.encoding import Base64Encoder

class Salty:
    seed: bytes

    def __init__(self, seed: str):
        self.seed = bytes(seed, 'utf-8')
        self.box = salt.SecretBox(self.seed)

    async def decrypt (self, encrypted_text: bytes) -> str:
        return self.box.decrypt(
            encrypted_text,
            encoder=Base64Encoder
        ).decode('utf-8')

    async def encrypt (self, text: str) -> bytes:
        return self.box.encrypt(
            text.encode('utf-8'),
            encoder=Base64Encoder
        )