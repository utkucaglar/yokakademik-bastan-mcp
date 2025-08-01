#!/usr/bin/env python3
"""
Academic Scraper MCP Server Launcher
"""
import asyncio
import sys
import os
from pathlib import Path

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mcp_server import main

if __name__ == "__main__":
    print("🎓 Academic Scraper MCP Server başlatılıyor...")
    print("📡 Smithery ile bağlantı kuruluyor...")
    print("🔧 Real-time streaming scraping aktif...")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server kapatılıyor...")
    except Exception as e:
        print(f"❌ Server hatası: {e}")
        sys.exit(1) 