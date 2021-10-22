#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from os import urandom
from argparse import ArgumentParser
import sys

BLOCK_SIZE = 128


def pad(message, block_size=BLOCK_SIZE):
    message_bytes = bytes(message, encoding='utf8')
    padder = PKCS7(block_size).padder()
    return padder.update(message_bytes) + padder.finalize()


def encrypt(message_bytes, cipher):
    # message_bytes = bytes(message, encoding='utf8')
    encryptor = cipher.encryptor()
    return encryptor.update(message_bytes) + encryptor.finalize()


def decrypt(message_bytes, cipher):
    decryptor = cipher.decryptor()
    return decryptor.update(message_bytes) + decryptor.finalize()


def unpad(message_bytes, block_size=BLOCK_SIZE):
    unpadder = PKCS7(block_size).unpadder()
    return unpadder.update(message_bytes) + unpadder.finalize()


def display(message):
    if isinstance(message, bytes):
        int_message = int.from_bytes(message, sys.byteorder)
    else:
        int_message = message
    return f'{int_message:#x}'


def set_mask(number_of_zeroes, block_size=BLOCK_SIZE):
    mask = (2 ** BLOCK_SIZE) - 1
    zero_mask = (2 ** (number_of_zeroes * 8)) - 1

    # print(f'Mask: {mask:#x}\nZero Mask: {zero_mask:#x}\n\n')

    return mask & ~zero_mask


def mask_iv(iv, number_of_zeros):
    if isinstance(iv, bytes):
        iv = int.from_bytes(iv, sys.byteorder)
    return iv & set_mask(number_of_zeros)


def get_args():
    parser = ArgumentParser()
    parser.add_argument('num_zeroes', type=int, help='Number of bytes to zero in IV')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    key = 0xe9e321cf53195b1c7884456921c567c080d89ea9c03762a6bb122fb0eee6a498 # urandom(32)
    iv = 0xc68d75111c1b79590f2e4deae3ea068c # urandom(16)
    masked_iv = mask_iv(iv, args.num_zeroes)
    cipher = Cipher(algorithms.AES(key.to_bytes(32, sys.byteorder)), modes.CBC(iv.to_bytes(16, sys.byteorder)))
    message = 'Test'
    padded_message = pad(message)
    enc_message = encrypt(padded_message, cipher)
    decrypted_message = decrypt(enc_message, cipher)
    unpadded_message = unpad(decrypted_message)
    output = f'*** Initial Conditions ***\nKey: {display(key)}\nInitialisation Vector (IV): {display(iv)}\nMasked IV: {display(masked_iv)}\n\n'
    output += f'*** Encryption ***\nOriginal Message: {message}\nPadded Message: {display(padded_message)}\nEncrypted message: {display(enc_message)}\n'
    output += f'\n*** Decryption ***\nDecrypted Message {display(decrypted_message)}\nUnpadded message: {unpadded_message}'
    print(output)


