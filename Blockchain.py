import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode,b64decode
import uuid

class Blockchain:
    def __init__(self,previous,data):
        self.previous = previous
        self.data = data

    def setHash(self,hash):
        self.hash = hash

    def getHash(string_data):
        return str(hashlib.sha3_512(str(string_data).encode("UTF-8")).hexdigest())

    def getIdentifier():
        return str(uuid.uuid4())

    def encryptMessage(string_data):
        # Set Encryptor
        with open('keys/pubkey.pem', 'rb') as pubkeyfile:
            pubkeypem = pubkeyfile.read()
        pubkey = RSA.importKey(pubkeypem)
        encryptor = PKCS1_OAEP.new(pubkey)
        # Encrypt Message
        byte_data = Blockchain.toByte(string_data)
        cipher_byte = encryptor.encrypt(byte_data)
        cipher_string = b64encode(cipher_byte).decode()
        return cipher_string

    def decryptMessage(cipher_data):
        # Set Decryptor
        with open('keys/privkey.pem', 'rb') as privkeyfile:
            privkeypem = privkeyfile.read()
        privkey = RSA.importKey(privkeypem)
        decryptor = PKCS1_OAEP.new(privkey)
        # Decrypt Message
        cipher_byte = b64decode(cipher_data.encode())
        plain_byte = decryptor.decrypt(cipher_byte)
        plain_string = Blockchain.toString(plain_byte)
        return plain_string

    # internal use
    def toByte(string_data):
        return string_data.encode("utf-8")

    def toString(byte_data):
        return byte_data.decode("utf-8")
