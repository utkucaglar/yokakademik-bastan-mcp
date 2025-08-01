"""
Session yönetimi
"""
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class AcademicScrapingSession:
    """Akademik scraping session yöneticisi"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.status = "initialized"
        self.progress = 0
        self.current_step = ""
        self.profiles = []
        self.collaborators = []
        self.error_message = ""
        self.start_time = time.time()
        self.base_dir = Path(__file__).parent.parent.parent / "sessions" / session_id
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def update_progress(self, progress: int, step: str, data: Any = None):
        """Progress güncelleme"""
        self.progress = progress
        self.current_step = step
        self.status = "running" if progress < 100 else "completed"
        
        # Session dosyasına yaz
        session_data = {
            "session_id": self.session_id,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "profiles_count": len(self.profiles),
            "collaborators_count": len(self.collaborators),
            "start_time": self.start_time,
            "last_update": time.time()
        }
        
        with open(self.base_dir / "session.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    def add_profile(self, profile: Dict):
        """Profil ekle ve kaydet"""
        self.profiles.append(profile)
        
        # Profiles dosyasını güncelle
        with open(self.base_dir / "profiles.json", "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)
    
    def add_collaborator(self, collaborator: Dict):
        """İşbirlikçi ekle ve kaydet"""
        self.collaborators.append(collaborator)
        
        # Collaborators dosyasını güncelle
        with open(self.base_dir / "collaborators.json", "w", encoding="utf-8") as f:
            json.dump(self.collaborators, f, ensure_ascii=False, indent=2)
    
    def get_status(self) -> Dict:
        """Session durumunu döndür"""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "profiles_count": len(self.profiles),
            "collaborators_count": len(self.collaborators),
            "error_message": self.error_message,
            "start_time": self.start_time,
            "elapsed_time": time.time() - self.start_time
        }


# Global session yönetimi
active_sessions = {}
session_lock = threading.Lock()


def create_session(session_id: str) -> AcademicScrapingSession:
    """Yeni session oluştur"""
    with session_lock:
        session = AcademicScrapingSession(session_id)
        active_sessions[session_id] = session
        return session


def get_session(session_id: str) -> Optional[AcademicScrapingSession]:
    """Session getir"""
    with session_lock:
        return active_sessions.get(session_id)


def remove_session(session_id: str):
    """Session kaldır"""
    with session_lock:
        if session_id in active_sessions:
            del active_sessions[session_id]


def list_sessions() -> List[Dict]:
    """Aktif session'ları listele"""
    with session_lock:
        return [
            {
                "session_id": session_id,
                "status": session.status,
                "progress": session.progress,
                "profiles_count": len(session.profiles),
                "collaborators_count": len(session.collaborators)
            }
            for session_id, session in active_sessions.items()
        ] 