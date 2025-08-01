"""
Yardımcı fonksiyonlar
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


def load_fields() -> List[Dict]:
    """fields.json dosyasını yükle"""
    fields_path = Path(__file__).parent.parent.parent / "main_codes" / "public" / "fields.json"
    try:
        with open(fields_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] fields.json yüklenemedi: {e}")
        return []


def get_field_name_by_id(fields_data: List[Dict], field_id: int) -> Optional[str]:
    """Alan ID'sine göre alan adını döndür"""
    for field in fields_data:
        if field['id'] == field_id:
            return field['name']
    return None


def get_specialty_name_by_id(fields_data: List[Dict], field_id: int, specialty_id: int) -> Optional[str]:
    """Uzmanlık ID'sine göre uzmanlık adını döndür"""
    for field in fields_data:
        if field['id'] == field_id:
            for specialty in field['specialties']:
                if specialty['id'] == specialty_id:
                    return specialty['name']
    return None


def sanitize_filename(name: str) -> str:
    """Dosya adı için güvenli string oluştur"""
    return re.sub(r'[^A-Za-z0-9ĞÜŞİÖÇğüşiöç ]+', '_', name).strip().replace(" ", "_")


def parse_labels_and_keywords(line: str) -> tuple:
    """YÖK akademik kutucuk ayrıştırıcı"""
    parts = [p.strip() for p in line.split(';')]
    left = parts[0] if parts else ''
    rest_keywords = [p.strip() for p in parts[1:] if p.strip()]
    left_parts = re.split(r'\s{2,}|\t+', left)
    green_label = left_parts[0].strip() if len(left_parts) > 0 else '-'
    blue_label = left_parts[1].strip() if len(left_parts) > 1 else '-'
    keywords = []
    if len(left_parts) > 2:
        keywords += [p.strip() for p in left_parts[2:] if p.strip()]
    keywords += rest_keywords
    if not keywords:
        keywords = ['-']
    return green_label, blue_label, keywords


def create_session_dir(session_id: str) -> Path:
    """Session klasörünü oluştur"""
    session_dir = Path(__file__).parent.parent.parent / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir 