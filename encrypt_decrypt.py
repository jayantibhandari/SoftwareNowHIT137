"""
encrypt_decrypt.py

1. Ask the user for two numbers (shift1 and shift2).
2. Read text from "raw_text.txt" and encrypt it, saving result in "encrypt_text.txt".
3. While encrypting, also save extra info about each character in "encryption_meta.json"
   -This makes sure we can always get back the exact original text.
4. Use encrypted text + metadata to create "decrypted_text.txt".
5. Finally, check if "decrypted_text.txt" is same as "raw_text.txt".

We keep metadata because the encryption uses different shifts depending on which "half" a letterbelongs to.
Sometimes different letters could turn into same encrypted letter.
Without metadata, we wouldn't know which original letter it was.

"""
import json
import sys
import os
from typing import Tuple
import string

#integer input
def get_shifts() -> Tuple[int, int]:
    #Prompts the user repeatedly until two integers are provided.
    while True:
        try:
            s1 = int(input("Enter shift1 (integer): ").strip())
            s2 = int(input("Enter shift2 (integer): ").strip())
            return s1, s2
        except ValueError:
            print("Enter integer values for shift1 and shift2.")


#encrption of single character
def encrypt_char(ch: str, s1: int, s2: int) -> Tuple[str, str]:
    """
    This function takes one character and encrpts it based on:
    - If it's a small letter between a-m -> shift forward by (shift1 * shift2).
    - If it's a small letter between n-z -> shift backward by (shift1 + shift2).
    - If it's a capital letter between A-M -> shift backward by shift1.
    - If it's a capital letter between N-Z -> shift forward by (shift2 squared).
    - If it's not a letter (space, number, symbol) -> leave it as it is.
    It also returns a short code (like 'l1', 'l2', 'U1', etc.) so we know which rule was used.
    """
    if ch.islower():
        if 'a' <= ch <= 'm':
            k = (s1 * s2) % 26
            new = chr((ord(ch) - 97 + k) % 26 + 97)
            return new, 'l1'
        else: 
            k = (s1 + s2) % 26
            new = chr((ord(ch) - 97 - k) % 26 + 97)
            return new, 'l2'
    elif ch.isupper():
        if 'A' <= ch <= 'M':
            k = s1 % 26
            new = chr((ord(ch) - 65 - k) % 26 + 65)
            return new, 'U1'
        else: 
            k = (s2 * s2) % 26
            new = chr((ord(ch) - 65 + k) % 26 + 65)
            return new, 'U2'
    else:
        return ch, 'o'                #numbers, spaces, newline stay the same
    

#encrpytion of single letter
def encrypt_letter_only(ch: str, s1: int, s2: int) -> str:
    enc, _ = encrypt_char(ch, s1, s2)
    return enc


#encryption of entire file
def encrypt_file(s1: int, s2: int,
                 raw_path: str = "raw_text.txt",
                 enc_path: str = "encrypted_text.txt",
                 meta_path: str = "encryption_meta.json") -> None:
    """
    Read the file at raw_path, encrypt its content,
    save the encrypted text to enc_path,
    and save extra info for each character to meta_path.
    """
    if not os.path.exists(raw_path):
        print(f"ERROR: {raw_path} not found. Put your input text in this file and run again.")
        sys.exit(1)

    meta = []
    with open(raw_path, "r", encoding="utf-8") as fin, \
         open(enc_path, "w", encoding="utf-8") as fout:
        text = fin.read()
        #encrypt each character on by one, keeping spaces, newline, and all other characters unchanged.
        for ch in text:
            enc_char, code = encrypt_char(ch, s1, s2)
            fout.write(enc_char)
            meta.append(code)

        #save metadata as JSON list, with one entry for each character.
        with open(meta_path, "w", encoding="utf-8") as fmeta:
            json.dump(meta, fmeta, ensure_ascii=False)
        
        #check if each original letter maps to a unique encrypted letter.
        #if not, decryption without metadata could be ambiguous.
        letters = list(string.ascii_lowercase + string.ascii_uppercase)
        mapping = [encrypt_letter_only(ch, s1, s2) for ch in letters]
        if len(set(mapping)) != len(mapping):
            print("\nWARNING: The shifts you chose cause some letters to map to the same encrypted letter.")
            print("Without the metadata, decryption might not give the original text exactly.")
            print(f"To ensure exact decryption, we saved per-character metadata in '{meta_path}.")

        else:
            print("\nInfo: The chosen shifts give a unique mapping; metadata is still saved.")
            
        print(f"Encryption finished. Encrypted file: '{enc_path}', metadata file: '{meta_path}'.")


#decrypt using metadata
def decrypt_file(s1: int, s2: int,
                 enc_path: str = "encrypted_text.txt",
                 deco_path: str = "decrypted_text.txt",
                 meta_path: str = "encryption_meta.json") -> None:
    """
    Read the encrypted file and metadata, then reconstruct the original text exactly.
    """
    if not os.path.exists(enc_path):
        print(f"ERROR: {enc_path} not found. Cannot decrypt.")
        sys.exit(1)
    if not os.path.exists(meta_path):
        print(f"ERROR: {meta_path} not found. Metadata is needed to decrypt the text exactly without any ambiguity.")
        sys.exit(1)

    with open(enc_path, "r", encoding="utf-8") as fin, \
         open(meta_path, "r", encoding="utf-8") as fmeta:
        enc_text = fin.read()
        meta = json.load(fmeta)

    if len(enc_text) != len(meta):
        print("ERROR: Metadat and encrypted file lengths don't match. Stopping decryption.")
        sys.exit(1)

    out_chars = []
    #reverse each character using the exact rule stored in metadata.
    for enc_ch, code in zip(enc_text, meta):
        if code == 'l1':
            #if the original letter was lowercase a-m, shift ot forward by s1 * s2 for encryption.
            k = (s1 * s2) % 26
            orig = chr((ord(enc_ch) - 97 - k) % 26 + 97)
            out_chars.append(orig)
        elif code == 'l2':
            #if the original letter was lowercase n-z, shift it backward by s1 + s2 for encryption.
            k = (s1 + s2) % 26
            orig = chr((ord(enc_ch) - 97 + k) % 26 + 97)
            out_chars.append(orig)
        elif code == 'U1':
            #if the original letter was uppercase A-M, shift it backward by s1 for encryption.
            k = s1 % 26
            orig = chr((ord(enc_ch) - 65 + k) % 26 + 65) 
            out_chars.append(orig)
        elif code == 'U2':
            #if the original letter was uppercase N-Z, shift it forward by s2 squared for encryption.
            k = (s2 * s2) % 26
            orig = chr((ord(enc_ch) - 65 - k) % 26 + 65)
            out_chars.append(orig)
        else:
            #'o' -> unchanged
            out_chars.append(enc_ch)
        
    with open(deco_path, "w", encoding="utf-8") as fout:
        fout.write("".join(out_chars))

    print(f"Decryption complete. Decrypted file: '{deco_path}'.")


#Verify
def verify_files(raw_path: str = "raw_text.txt", deco_path: str = "decrypted_text.txt") -> bool:
    #compare the original file and decrypted file to see if they match exactly.
    if not os.path.exists(raw_path):
        print(f"ERROR: {raw_path} not found for verification.")
        return False
    if not os.path.exists(deco_path):
        print(f"ERROR: {deco_path} not found for verification.")
        return False
    
    with open(raw_path, "r", encoding="utf-8") as fraw, \
    open(deco_path, "r", encoding="utf-8") as fdec:
        raw = fraw.read()
        dec = fdec.read()

    if raw == dec:
        print("VERIFICATION: SUCCESS - decrypted text matches the original exactly.")
        return True
    else:
        print("VERIFICATION: FAILED - decrypted text does NOT match the original.")
        #show the first place where the texts differ and a little context for debugging
        i = 0
        minlen = min(len(raw), len(dec))
        while i < minlen and raw[i] == dec[i]:
            i += 1
            print(f"First mismatch position: {i}")
            context = 10
            print("Original context: ...", raw[max(0, i-context):i+context].replace("\n", "\\n"))
            print("Decoded context: ...", dec[max(0, i-context):i+context].replace("\n", "\\n"))
            if len(raw) != len(dec):
                print(f"(Lengths differ: original {len(raw)} chars, decrypted {len(dec)} chars)")
                return False
            

#main program flow
def main():
    print("=== Simple file encrypt/decrypt program ===")
    s1, s2 = get_shifts()

if __name__ == "__main__":
    s1 = int(input("Enter shift1 value: "))
    s2 = int(input("Enter shift2 value: "))

    #paths
    raw_path = "raw_text.txt"
    enc_path = "encrypted_text.txt"
    meta_path = "encryption_meta.json"
    deco_path = "decrypted_text.txt"

    #1. Encrypt
    encrypt_file(s1, s2, raw_path=raw_path, enc_path=enc_path, meta_path=meta_path)
    #2. Decrypt
    decrypt_file(s1, s2, enc_path=enc_path, deco_path=deco_path, meta_path=meta_path)
    #3. Verify
    verify_files(raw_path=raw_path, deco_path=deco_path)

