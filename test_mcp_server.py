#!/usr/bin/env python3
"""
MCP Server Test Script
"""
import asyncio
import json
import sys
from pathlib import Path

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.scraper.academic_scraper import StreamingAcademicScraper
from src.scraper.session_manager import create_session, get_session, list_sessions


async def test_scraping():
    """Test scraping fonksiyonu"""
    print("🧪 Academic Scraper MCP Server Test")
    print("=" * 50)
    
    # Test session oluştur
    session_id = f"test_session_{int(asyncio.get_event_loop().time())}"
    print(f"📝 Test session ID: {session_id}")
    
    # Scraper oluştur
    scraper = StreamingAcademicScraper()
    
    # Test parametreleri
    test_params = {
        "name": "Ahmet Yılmaz",
        "email": None,
        "field_id": 2,  # Fen Bilimleri
        "specialty_ids": [1]  # Biyoloji
    }
    
    print(f"🔍 Test parametreleri: {test_params}")
    print("⏳ Scraping başlatılıyor...")
    
    try:
        # Streaming test
        update_count = 0
        async for update in scraper.scrape_profiles_streaming(
            name=test_params["name"],
            session_id=session_id,
            field_id=test_params["field_id"],
            specialty_ids=test_params["specialty_ids"],
            email=test_params["email"]
        ):
            update_count += 1
            print(f"📊 Update {update_count}: {update['type']}")
            
            if update['type'] == 'profile_added':
                profile = update['data']['profile']
                print(f"  👤 Profil: {profile['name']} - {profile['title']}")
            
            elif update['type'] == 'collaborator_added':
                collab = update['data']['collaborator']
                print(f"  🤝 İşbirlikçi: {collab['name']}")
            
            elif update['type'] == 'completed':
                print(f"✅ Scraping tamamlandı!")
                print(f"   📊 Profil sayısı: {update['data']['profiles_count']}")
                print(f"   🤝 İşbirlikçi sayısı: {update['data']['collaborators_count']}")
                break
            
            elif update['type'] == 'error':
                print(f"❌ Hata: {update['data']['message']}")
                break
            
            # Test için sadece ilk 10 update'i göster
            if update_count >= 10:
                print("🛑 Test için 10 update'e ulaşıldı, durduruluyor...")
                break
    
    except Exception as e:
        print(f"❌ Test hatası: {e}")
    
    # Session durumunu kontrol et
    session = get_session(session_id)
    if session:
        status = session.get_status()
        print(f"\n📋 Session durumu:")
        print(f"   Status: {status['status']}")
        print(f"   Progress: {status['progress']}%")
        print(f"   Profiles: {status['profiles_count']}")
        print(f"   Collaborators: {status['collaborators_count']}")
    
    print("\n🎉 Test tamamlandı!")


async def test_session_management():
    """Session yönetimi test"""
    print("\n🧪 Session Management Test")
    print("=" * 30)
    
    # Test session'ları oluştur
    for i in range(3):
        session_id = f"test_session_{i}_{int(asyncio.get_event_loop().time())}"
        session = create_session(session_id)
        session.update_progress(i * 30, f"Test step {i}")
        print(f"✅ Session oluşturuldu: {session_id}")
    
    # Session'ları listele
    sessions = list_sessions()
    print(f"\n📋 Aktif session sayısı: {len(sessions)}")
    
    for session_info in sessions:
        print(f"   - {session_info['session_id']}: {session_info['status']} ({session_info['progress']}%)")


if __name__ == "__main__":
    print("🚀 Academic Scraper MCP Server Test Suite")
    print("=" * 60)
    
    # Test'leri çalıştır
    asyncio.run(test_session_management())
    asyncio.run(test_scraping()) 