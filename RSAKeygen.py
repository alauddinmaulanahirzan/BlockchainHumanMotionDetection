from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

def main():
    print("==> Generating 2048-bit RSA Keys",end="",flush=True)
    keyPair = RSA.generate(2048)
    pubKey = keyPair.publickey()
    print(" > [DONE]")

    print("==> Exporting Public Key",end="",flush=True)
    f = open('keys/pubkey.pem', 'wb')
    f.write(pubKey.exportKey('PEM'))
    f.close()
    print(" > [DONE]")

    print("==> Exporting Private Key",end="",flush=True)
    f = open('keys/privkey.pem', 'wb')
    f.write(keyPair.exportKey('PEM'))
    f.close()
    print(" > [DONE]")

if __name__ == '__main__':
    main()
