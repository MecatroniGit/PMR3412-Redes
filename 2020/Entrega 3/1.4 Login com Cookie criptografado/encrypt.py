from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

class EncryptionManager:
    def __init__(self):
        key = bytes.fromhex('35b510952221abf4e5abc1ae3742ca90c1e5d083ef330392e1a8c15916e89b7f')
        nonce = bytes.fromhex('430c47416957b67e929aaf5a8de265cd')
        aes_context = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        self.encryptor = aes_context.encryptor()
        self.decryptor = aes_context.decryptor()

    def updateEncryptor(self, plaintext):
        return self.encryptor.update(plaintext)

    def finalizeEncryptor(self):
        return self.encryptor.finalize()
    
    def updateDecryptor(self, ciphertext):
        return self.decryptor.update(ciphertext)
    
    def finalizeDecryptor(self):
        return self.decryptor.finalize()

manager = EncryptionManager()

plaintexts = [
    b'1',
    b'2',
    b'3',
    b'4',
    b'5'
]

ciphertexts = []

for m in plaintexts:
    ciphertexts.append(manager.updateEncryptor(m))
ciphertexts.append(manager.finalizeEncryptor())

def xorbytes(abytes, bbytes):
    return bytes([a ^ b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])

for c in ciphertexts:
    plaintext = manager.updateDecryptor(c)
    ciphertext = c
    print ("Plaintext:", plaintext, "Cipher (hex):", ciphertext.hex())
    # print("Key:", xorbytes(plaintext, ciphertext).hex())
print("Recovered:", manager.finalizeDecryptor())