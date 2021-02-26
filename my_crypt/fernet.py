import os
from crypt import *
import time

f = open('file.pdf', 'rb')
file_content = f.read()
f.close()

start_program = time.time()
key = generate_key_derivation(b"", "ambos")
gen_key = time.time()
token = encrypt(key, file_content)

f3 = open("token.pdf", "wb")
f2 = open("token.bin", "wb")
f2.write(token)
f3.write(token)
f2.close()
f3.close()

f = open('token.bin', 'rb')
file_content = f.read()
f.close()

enc = time.time()
key2 = generate_key_derivation(b"", "ambos")
s_b = decrypt(key2, file_content)
dec = time.time()


f2 = open("file-rewrote.pdf", "wb")
f2.write(s_b)
f2.close()

print("program done !")
