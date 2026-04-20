from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    # --- Liên lạc & Mạng ---
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",

    # --- Giấy tờ tùy thân (Việt Nam) ---
    "cccd": r"\b\d{12}\b",                                 # Căn cước công dân (12 số)
    "cmnd": r"\b\d{9}\b",                                  # Chứng minh nhân dân cũ (9 số)
    "passport_vn": r"\b[A-Z]\d{7}\b",                      # Hộ chiếu VN (1 chữ cái in hoa + 7 số)
    
    # --- Tài chính & Định danh khác ---
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "tax_id_vn": r"\b\d{10}(?:-\d{3})?\b",                 # Mã số thuế (10 số, hoặc 10 số - 3 số)
    "license_plate_vn": r"\b\d{2}[A-ZĐ][A-Z0-9]?[- .]?\d{3,4}(?:\.\d{2})?\b", # Biển số xe (VD: 29A-123.45, 59X1-12345)
    
    # --- Thông tin cá nhân cơ bản ---
    "date_of_birth": r"\b(?:0?[1-9]|[12][0-9]|3[01])[-/\.](?:0?[1-9]|1[012])[-/\.](?:19|20)\d\d\b", # dd/mm/yyyy hoặc dd-mm-yyyy
    
    # --- Địa chỉ (Nhận diện theo từ khóa) ---
    "address_keyword_vn": r"(?i)\b(?:thành phố|tp\.?|quận|q\.?|huyện|h\.?|phường|p\.?|xã|thị xã|tx\.?|đường|ngõ|ngách|thôn|xóm|ấp|khu phố|kp\.?)\b",

    "otp_code": r"\b\d{6}\b",                  # Mã OTP 6 số

    # 1. Thẻ nội địa Napas (Luôn bắt đầu bằng 9704, độ dài 16 hoặc 19 số)
    "napas_card": r"\b9704[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}(?:[- ]?\d{3})?\b",
    
    # 2. Thẻ Visa (Bắt đầu bằng 4, thường 16 số)
    "visa_card": r"\b4\d{3}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    
    # 3. Thẻ Mastercard (Bắt đầu từ 51-55, 16 số)
    "mastercard": r"\b5[1-5]\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    
    # 4. Số tài khoản ngân hàng VN (Thường từ 8 đến 15 số, không có chữ cái)
    # Lưu ý: Bắt từ 8 số trở lên để tránh nhầm với mã OTP hay số tiền nhỏ
    "bank_account": r"\b\d{8,15}\b",
    
    # 5. Mã giao dịch (Txn ID - Thường là chuỗi alphanumeric dài từ các app ngân hàng)
    "transaction_id": r"\b[A-Z0-9]{12,24}\b"

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
