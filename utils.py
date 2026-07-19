# utils.py
import re
from datetime import datetime

class Normalizer:
    @staticmethod
    def normalize_value(value, attr_type="string"):
        if attr_type == "date":
            return Normalizer._normalize_date(value)
        elif attr_type == "numeric":
            return Normalizer._normalize_numeric(value)
        else:
            return Normalizer._normalize_string(value)

    @staticmethod
    def _normalize_date(value):
        if isinstance(value, str):
            m = re.match(r'(\d{4})-(\d{2})-(\d{2})', value)
            if m:
                return value
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
                return dt.isoformat()
            except:
                pass
        return value

    @staticmethod
    def _normalize_numeric(value):
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            cleaned = re.sub(r'[^\d.]', '', value)
            try:
                return float(cleaned)
            except:
                pass
        return value

    @staticmethod
    def _normalize_string(value):
        if isinstance(value, str):
            return value.strip().lower()
        return value