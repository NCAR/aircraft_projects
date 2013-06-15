'''decrypt.py - Python source designed to decrypt IWG1 messages from NOAA.'''

import base64
import string
import hashlib
from Crypto.Cipher import AES

# Encryption Setup
padding = '^'
mode = AES.MODE_CBC
BLOCK_SIZE = 32
sharedpw = 'rvDwR#6L+NeP'
key = hashlib.sha256(sharedpw).digest()
#print "hashlib.sha256(sharedpw).hexdigest(): "+hashlib.sha256(sharedpw).hexdigest()
#print "key:                               "+key

# one-liner to sufficiently pad the text to be encrypted
#pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * padding

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
#EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(padding)

cipher = AES.new(key)

def decode(data):
    return DecodeAES(cipher, data)
