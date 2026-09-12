#!/usr/bin/env python3
"""
AES-GCM / PBKDF2 helper compatible with the supplied JavaScript.

JS-compatible settings:
  PBKDF2
  - password: UTF-8
  - salt: raw bytes
  - iterations: 100000
  - hash: SHA-256
  AES-GCM
  - key length: 256 bits
  - IV: raw bytes (12 bytes recommended)
  - ciphertext returned by WebCrypto includes the 16-byte GCM auth tag

Install:
    python -m pip install cryptography

Run:
    python crypto_ui.py
"""

import base64
import os
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


PBKDF2_ITERATIONS = 100_000
SALT_BYTES = 16
IV_BYTES = 12
KEY_BYTES = 32
GCM_TAG_BYTES = 16


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(value: str) -> bytes:
    # JS atob() is strict about Base64; strip harmless surrounding whitespace.
    return base64.b64decode(value.strip(), validate=True)


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_BYTES,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def decrypt_js_compatible(
    encrypted_b64: str,
    salt_b64: str,
    iv_b64: str,
    password: str,
) -> str:
    ciphertext = b64d(encrypted_b64)
    salt = b64d(salt_b64)
    iv = b64d(iv_b64)

    key = derive_key(password, salt)
    plaintext = AESGCM(key).decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")


def encrypt_js_compatible(
    plaintext: str,
    password: str,
    salt: bytes | None = None,
    iv: bytes | None = None,
) -> tuple[str, str, str]:
    salt = salt if salt is not None else os.urandom(SALT_BYTES)
    iv = iv if iv is not None else os.urandom(IV_BYTES)

    if len(salt) != SALT_BYTES:
        raise ValueError(f"Salt must be {SALT_BYTES} bytes.")
    if len(iv) != IV_BYTES:
        raise ValueError(f"IV must be {IV_BYTES} bytes.")

    key = derive_key(password, salt)
    ciphertext = AESGCM(key).encrypt(iv, plaintext.encode("utf-8"), None)

    # WebCrypto AES-GCM's returned ArrayBuffer is ciphertext || auth tag,
    # which is exactly the format produced by cryptography's AESGCM.encrypt().
    return b64e(ciphertext), b64e(salt), b64e(iv)


class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JS AES-GCM Crypto Tool")
        self.geometry("980x760")
        self.minsize(820, 650)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self._build_ui()

    @staticmethod
    def _label(parent, text, row, column=0, **kwargs):
        label = ttk.Label(parent, text=text, **kwargs)
        label.grid(row=row, column=column, sticky="w", padx=8, pady=(8, 3))
        return label

    @staticmethod
    def _text(parent, height=6, width=80):
        return ScrolledText(
            parent,
            height=height,
            width=width,
            wrap="word",
            undo=True,
            font=("TkFixedFont", 10),
        )

    @staticmethod
    def _entry(parent, show=None, width=85):
        return ttk.Entry(parent, width=width, show=show)

    def _build_ui(self):
        header = ttk.Frame(self, padding=(14, 12))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="JS-Compatible AES-256-GCM / PBKDF2 Tool",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=(
                "Matches your browser code: UTF-8 password, PBKDF2-SHA256, "
                "100,000 iterations, AES-GCM-256."
            ),
        ).pack(anchor="w", pady=(4, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        decrypt_tab = ttk.Frame(notebook, padding=12)
        encrypt_tab = ttk.Frame(notebook, padding=12)

        notebook.add(decrypt_tab, text="Decrypt")
        notebook.add(encrypt_tab, text="Encrypt")

        self._build_decrypt_tab(decrypt_tab)
        self._build_encrypt_tab(encrypt_tab)

    def _build_decrypt_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(9, weight=1)

        ttk.Label(
            parent,
            text="Enter the same values used by your JavaScript.",
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.dec_password = self._entry(parent, show="*")
        self.dec_cipher = self._text(parent, height=7)
        self.dec_salt = self._entry(parent)
        self.dec_iv = self._entry(parent)

        self._label(parent, "Code / password (the JS lowercases it):", 1)
        self.dec_password.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 5))

        self._label(parent, "Encrypted data (Base64):", 3)
        self.dec_cipher.grid(row=4, column=0, sticky="nsew", padx=8, pady=(0, 5))

        self._label(parent, "Salt (Base64):", 5)
        self.dec_salt.grid(row=6, column=0, sticky="ew", padx=8, pady=(0, 5))

        self._label(parent, "IV (Base64):", 7)
        self.dec_iv.grid(row=8, column=0, sticky="ew", padx=8, pady=(0, 5))

        controls = ttk.Frame(parent)
        controls.grid(row=9, column=0, sticky="new", padx=8, pady=(10, 0))
        self.dec_button = ttk.Button(
            controls, text="Decrypt", command=self._decrypt
        )
        self.dec_button.pack(side="left")

        ttk.Button(
            controls, text="Clear", command=self._clear_decrypt
        ).pack(side="left", padx=(8, 0))

        ttk.Label(
            controls,
            text="Wrong password / modified data will fail AES-GCM authentication.",
        ).pack(side="left", padx=(14, 0))

        ttk.Label(parent, text="Decoded plaintext:").grid(
            row=10, column=0, sticky="w", padx=8, pady=(14, 3)
        )

        self.dec_output = self._text(parent, height=10)
        self.dec_output.grid(row=11, column=0, sticky="nsew", padx=8, pady=(0, 8))
        parent.rowconfigure(11, weight=1)

    def _build_encrypt_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(10, weight=1)

        ttk.Label(
            parent,
            text="Create Base64 values that your JavaScript can decrypt.",
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.enc_password = self._entry(parent, show="*")
        self.enc_plain = self._text(parent, height=7)
        self.enc_suffix = ttk.Entry(parent, width=40)
        self.enc_suffix.insert(0, "ge3tviek30")

        self._label(parent, "Code / password:", 1)
        self.enc_password.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 5))

        self._label(parent, "Plaintext to encrypt:", 3)
        self.enc_plain.grid(row=4, column=0, sticky="nsew", padx=8, pady=(0, 5))

        suffix_frame = ttk.Frame(parent)
        suffix_frame.grid(row=5, column=0, sticky="ew", padx=8, pady=(6, 0))
        suffix_frame.columnconfigure(1, weight=1)

        ttk.Label(
            suffix_frame, text="Optional verification suffix:"
        ).grid(row=0, column=0, sticky="w")
        self.enc_suffix.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        ttk.Label(
            parent,
            text=(
                "The suffix is appended before encryption, so the result is directly "
                "compatible with decrypted.endsWith(verificationSequence)."
            ),
            wraplength=900,
        ).grid(row=6, column=0, sticky="w", padx=8, pady=(5, 5))

        controls = ttk.Frame(parent)
        controls.grid(row=7, column=0, sticky="ew", padx=8, pady=(8, 0))

        ttk.Button(
            controls, text="Encrypt", command=self._encrypt
        ).pack(side="left")

        ttk.Button(
            controls, text="Generate new salt + IV", command=self._generate_randoms
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            controls, text="Clear", command=self._clear_encrypt
        ).pack(side="left", padx=(8, 0))

        ttk.Label(parent, text="Encrypted data (Base64):").grid(
            row=8, column=0, sticky="w", padx=8, pady=(14, 3)
        )
        self.enc_cipher = self._text(parent, height=5)
        self.enc_cipher.grid(row=9, column=0, sticky="nsew", padx=8, pady=(0, 5))

        outputs = ttk.Frame(parent)
        outputs.grid(row=10, column=0, sticky="ew", padx=8, pady=(4, 0))
        outputs.columnconfigure(1, weight=1)
        outputs.columnconfigure(3, weight=1)

        ttk.Label(outputs, text="Salt (Base64):").grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        self.enc_salt = ttk.Entry(outputs)
        self.enc_salt.grid(row=0, column=1, sticky="ew", padx=(0, 15))

        ttk.Label(outputs, text="IV (Base64):").grid(
            row=0, column=2, sticky="w", padx=(0, 6)
        )
        self.enc_iv = ttk.Entry(outputs)
        self.enc_iv.grid(row=0, column=3, sticky="ew")

        self._generate_randoms()

    def _generate_randoms(self):
        salt = os.urandom(SALT_BYTES)
        iv = os.urandom(IV_BYTES)

        self._replace_entry(self.enc_salt, b64e(salt))
        self._replace_entry(self.enc_iv, b64e(iv))

    @staticmethod
    def _replace_entry(entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def _decrypt(self):
        password = self.dec_password.get().lower()
        cipher = self.dec_cipher.get("1.0", "end-1c").strip()
        salt = self.dec_salt.get().strip()
        iv = self.dec_iv.get().strip()

        if not password or not cipher or not salt or not iv:
            messagebox.showwarning(
                "Missing input",
                "Enter the code, encrypted data, salt, and IV.",
            )
            return

        try:
            plaintext = decrypt_js_compatible(cipher, salt, iv, password)
        except Exception as exc:
            self.dec_output.delete("1.0", "end")
            if isinstance(exc, UnicodeDecodeError):
                detail = "The decrypted bytes are not valid UTF-8."
            else:
                detail = (
                    "Decryption failed. Check the password, Base64 values, "
                    "salt/IV, and that the ciphertext was produced with AES-GCM."
                )
            messagebox.showerror("Decryption failed", detail)
            return

        self.dec_output.delete("1.0", "end")
        self.dec_output.insert("1.0", plaintext)

    def _encrypt(self):
        password = self.enc_password.get().lower()
        plaintext = self.enc_plain.get("1.0", "end-1c")
        suffix = self.enc_suffix.get()

        if not password:
            messagebox.showwarning("Missing password", "Enter a code / password.")
            return

        if plaintext == "":
            messagebox.showwarning("Missing plaintext", "Enter data to encrypt.")
            return

        try:
            salt = b64d(self.enc_salt.get().strip())
            iv = b64d(self.enc_iv.get().strip())

            final_plaintext = plaintext + suffix
            cipher_b64, salt_b64, iv_b64 = encrypt_js_compatible(
                final_plaintext, password, salt=salt, iv=iv
            )
        except Exception as exc:
            messagebox.showerror("Encryption failed", str(exc))
            return

        self.enc_cipher.delete("1.0", "end")
        self.enc_cipher.insert("1.0", cipher_b64)
        self._replace_entry(self.enc_salt, salt_b64)
        self._replace_entry(self.enc_iv, iv_b64)

    def _clear_decrypt(self):
        self.dec_password.delete(0, "end")
        self.dec_cipher.delete("1.0", "end")
        self.dec_salt.delete(0, "end")
        self.dec_iv.delete(0, "end")
        self.dec_output.delete("1.0", "end")

    def _clear_encrypt(self):
        self.enc_password.delete(0, "end")
        self.enc_plain.delete("1.0", "end")
        self.enc_cipher.delete("1.0", "end")
        self._generate_randoms()


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
