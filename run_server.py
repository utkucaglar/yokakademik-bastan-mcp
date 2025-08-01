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

from src.mcp_server import main as mcp_main

def main():
    """MCP Server main function"""
    # JSON-RPC protokolü için stderr'e print yapmıyoruz
    # Sadece hata durumlarında stderr kullanıyoruz
    
    try:
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        print("\n🛑 Server kapatılıyor...", file=sys.stderr)
    except Exception as e:
        print(f"❌ Server hatası: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 