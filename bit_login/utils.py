import base64
import requests
from urllib.parse import urlparse, urlunparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def encode_vpn_host(host: str, 
                    vpn_key_str: str = 'wrdvpnisthebest!', 
                    vpn_iv_str: str = 'wrdvpnisthebest!') -> str:
    vpn_key = vpn_key_str.encode('utf-8')
    vpn_iv = vpn_iv_str.encode('utf-8')

    text_len = len(host)
    pad_len = (16 - (text_len % 16)) % 16
    padded_host = host + ('0' * pad_len)
    plaintext = padded_host.encode('utf-8')

    cipher = Cipher(algorithms.AES(vpn_key), modes.ECB(), backend=default_backend())
    
    ciphertext = bytearray(len(plaintext))
    feedback = bytearray(vpn_iv)
    for i in range(0, len(plaintext), 16):
        encryptor = cipher.encryptor()
        keystream = encryptor.update(bytes(feedback)) + encryptor.finalize()
        block = bytearray(16)
        for j in range(16):
            if i + j < len(plaintext):  
                block[j] = plaintext[i + j] ^ keystream[j]
                ciphertext[i + j] = block[j]
        
        feedback = block

    iv_hex = vpn_iv.hex()
    cipher_hex = ciphertext.hex()

    return iv_hex + cipher_hex[:text_len * 2]


def convert_to_webvpn_url(original_url: str) -> str:
    """
    将普通内网 URL 转换为 WebVPN 格式的 URL
    """
    parsed = urlparse(original_url)
    target_proto = parsed.scheme       
    target_host = parsed.hostname       
    
    if not target_host:
        return original_url  
        
    encoded_host = encode_vpn_host(target_host)
    
    new_path = f"/{target_proto}/{encoded_host}{parsed.path}"
    
    webvpn_url = urlunparse((
        'https', 
        'webvpn.bit.edu.cn', 
        new_path, 
        parsed.params, 
        parsed.query, 
        parsed.fragment
    ))
    
    return webvpn_url



XOR_KEY = b'bit-sso-AutoLogin-key'

def encrypt_password(pwd: str) -> str:
    if not pwd: return ""
    in_bytes = pwd.encode('utf-8')
    out_bytes = bytearray(len(in_bytes))
    for i in range(len(in_bytes)):
        out_bytes[i] = in_bytes[i] ^ XOR_KEY[i % len(XOR_KEY)]
    b64_str = base64.b64encode(out_bytes).decode('ascii')
    return "xor:" + b64_str

def decrypt_password(s: str) -> str:
    if not s or not s.startswith("xor:"): return s
    try:
        b64_bytes = base64.b64decode(s[4:])
        out_bytes = bytearray(len(b64_bytes))
        for i in range(len(b64_bytes)):
            out_bytes[i] = b64_bytes[i] ^ XOR_KEY[i % len(XOR_KEY)]
        return out_bytes.decode('utf-8')
    except Exception:
        return s

def check_network_env():
    """检查网络环境,校园网返回True
    """
    try:
        requests.get("http://10.0.0.55",timeout=3)
        return True
    except:
        return False