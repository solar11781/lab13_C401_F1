from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    # --- Thông tin thẻ & Ngân hàng (Ưu tiên cao nhất) ---
    "napas_card": r"\b9704[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}(?:[- ]?\d{3})?\b",
    "visa_card": r"\b4\d{3}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "mastercard": r"\b5[1-5]\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "cvv_cvc": r"(?i)\b(?:cvv|cvc)\s*[:=\-]?\s*\d{3,4}\b",
    
    # --- Bảo mật xác thực (Đi kèm keyword để tránh false positive với số tiền/ID) ---
    "otp_code": r"(?i)\b(?:otp|mã otp)\s*[:=\-]?\s*\d{4,8}\b",
    "pin_code": r"(?i)\b(?:pin|mã pin)\s*[:=\-]?\s*\d{4,6}\b",
    "password": r"(?i)\b(?:pass|password|mật khẩu|mk)\s*[:=\-]?\s*\S+\b",
    
    # --- Tài khoản & Giao dịch ---
    "transaction_id": r"\b[A-Z0-9]{12,24}\b",
    "bank_account": r"\b\d{8,15}\b", # Đặt dưới mã giao dịch và thẻ để tránh match một phần
    
    # --- Liên lạc & Mạng ---
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "mac_address": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b",

    # --- Giấy tờ tùy thân (Việt Nam) ---
    "cccd": r"\b\d{12}\b",                                 
    "cmnd": r"\b\d{9}\b",                                  
    "passport_vn": r"\b[A-Z]\d{7}\b",                      
    "tax_id_vn": r"\b\d{10}(?:-\d{3})?\b",                 
    "license_plate_vn": r"\b\d{2}[A-ZĐ][A-Z0-9]?[- .]?\d{3,4}(?:\.\d{2})?\b", 
    
    # --- Thông tin cá nhân cơ bản ---
    "date_of_birth": r"\b(?:0?[1-9]|[12][0-9]|3[01])[-/\.](?:0?[1-9]|1[012])[-/\.](?:19|20)\d\d\b", 
    
    # --- Địa chỉ (Nhận diện theo từ khóa) ---
    "address_keyword_vn": r"(?i)\b(?:thành phố|tp\.?|quận|q\.?|huyện|h\.?|phường|p\.?|xã|thị xã|tx\.?|đường|ngõ|ngách|thôn|xóm|ấp|khu phố|kp\.?)\b",
}

def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
