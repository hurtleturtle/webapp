#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from os import urandom
from argparse import ArgumentParser
import sys
from math import ceil


BLOCK_SIZE = 128


class PaddingOracleAttack:
    def __init__(self, message: str, iv=None, verbosity=0) -> None:
        self.verbosity = verbosity
        self.message = message
        self.iv = urandom(BLOCK_SIZE / 8) if not iv else iv
        self.cipher = self._create_cipher()

    def _create_cipher(self, key_length=32):
        key = urandom(key_length)
        cipher = Cipher(algorithms.AES(key.to_bytes(key_length, sys.byteorder)), modes.CBC(self.iv.to_bytes(len(self.iv), sys.byteorder)))
        return cipher

    def encrypt(self, message_bytes: bytes):
        # message_bytes = bytes(message, encoding='utf8')
        encryptor = self.cipher.encryptor()
        return encryptor.update(message_bytes) + encryptor.finalize()

    def decrypt(self, message_bytes: bytes):
        decryptor = self.cipher.decryptor()
        return decryptor.update(message_bytes) + decryptor.finalize()

    def pad(self, message: str, block_size=BLOCK_SIZE):
        message_bytes = bytes(message, encoding='utf8')
        padder = PKCS7(block_size).padder()
        return padder.update(message_bytes) + padder.finalize()

    def unpad(self, message_bytes: bytes, block_size=BLOCK_SIZE):
        unpadder = PKCS7(block_size).unpadder()
        return unpadder.update(message_bytes) + unpadder.finalize()

    def separate(self, message: int, block_size=BLOCK_SIZE):
        '''
            Separate the message into block_size chunks consisting of the IV first,
            followed by the message in hexadecimal
        '''
        num_characters = block_size // 4
        str_message = display(message)[2:]
        extra_zeroes = (num_characters - (len(str_message) % num_characters)) % num_characters
        str_message = str_message.zfill(extra_zeroes + len(str_message))
        num_elements = ceil(len(str_message) / num_characters)
        elements = [str_message[start * num_characters:(start + 1) * num_characters] for start in range(num_elements)]
        return elements if len(elements) > 1 else ['0' * num_characters, *elements]

    def decrypt_padding_oracle_attack(self, message: str) -> str:
        '''
            Decrypt and unpad a padding oracle attack
        '''
        return ''


def set_mask(self, number_of_zeroes, block_size=BLOCK_SIZE, verbosity=0):
    num_blocks = max(ceil(number_of_zeroes / (block_size / 8)), 1)
    mask = (2 ** (num_blocks * block_size)) - 1
    zero_mask = ((2 ** (number_of_zeroes * 8)) - 1) 
    zero_mask = zero_mask << (block_size - zero_mask.bit_length())
    
    if verbosity:
        print(f'Mask: {mask:#x}\nZero Mask: {zero_mask:#x}')
        print(f'Bit lengths:', end='\n\t')
        print(f'Mask: {mask.bit_length()}', f'Zero Mask: {zero_mask.bit_length()}', 
                f'Block size: {block_size}', f'Num zeroes: {number_of_zeroes}', f'Num blocks: {num_blocks}\n', sep="\n\t")

    return mask ^ zero_mask


def mask(self, message, number_of_zeroes):
    if isinstance(message, bytes):
        message = int.from_bytes(message, sys.byteorder)
    return message & set_mask(number_of_zeroes, message.bit_length())
    

def display(message):
    if isinstance(message, bytes):
        int_message = int.from_bytes(message, sys.byteorder)
    else:
        int_message = message
    return f'{int_message:#0x}'


def get_args():
    parser = ArgumentParser()
    parser.add_argument('num_zeroes', type=int, help='Number of bytes to zero in IV')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    key = 0xe9e321cf53195b1c7884456921c567c080d89ea9c03762a6bb122fb0eee6a498 # urandom(32)
    iv = 0xc68d75111c1b79590f2e4deae3ea068c # urandom(16)
    cipher = Cipher(algorithms.AES(key.to_bytes(32, sys.byteorder)), modes.CBC(iv.to_bytes(16, sys.byteorder)))
    message = 'Test'
    padded_message = pad(message)
    enc_message = encrypt(padded_message, cipher)
    joined_message = int(display(iv) + display(enc_message)[2:], 16)
    decrypted_message = decrypt(enc_message, cipher)
    unpadded_message = unpad(decrypted_message)
    padding_oracle_attack_msg = mask(joined_message, args.num_zeroes)
    padding_oracle_iv, *padding_oracle_encrypted_msg = separate(padding_oracle_attack_msg)
    padding_oracle_decrypted_msg = decrypt(int(''.join(padding_oracle_encrypted_msg), 16).to_bytes(16, sys.byteorder), cipher)

    try:
        padding_oracle_unpadded_msg = unpad(padding_oracle_decrypted_msg)
    except ValueError as e:
        padding_oracle_unpadded_msg = e

    output = f'*** Initial Conditions ***\nKey: {display(key)}\nInitialisation Vector (IV): {display(iv)}\n\n'
    output += f'*** Encryption ***\nOriginal Message: {message}\nPadded Message:{display(padded_message)}\nEncrypted message: {display(enc_message)}\n\n'
    output += f'*** Padding Oracle Attack ***\nOriginal IV & Encrypted Message:\t{display(joined_message)}\n'
    output += f'Attack Message:\t\t{display(padding_oracle_attack_msg)}\n'
    output += f'Components:\n\tIV: {padding_oracle_iv}\n\tMessage: {padding_oracle_encrypted_msg}\n\n'
    output += f'*** Decryption ***\nDecrypted Message: {display(decrypted_message)}\nUnpadded message: {unpadded_message}\n\n'
    output += f'*** Padding Oracle Decryption ***\nDecrypted Message: {display(padding_oracle_decrypted_msg)}\nUnpadded Message: {padding_oracle_unpadded_msg}\n'
    print(output)


