#!/usr/bin/env python3
"""
MCP Server for Academic Profile Scraping with Real-time Streaming
Bu server, YÖK Akademik veritabanından profil ve işbirlikçi bilgilerini
real-time olarak çeker ve progress updates gönderir.
"""

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Generator
from pathlib import Path

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

# Local imports
from .scraper.academic_scraper import StreamingAcademicScraper
from .scraper.session_manager import create_session, get_session, list_sessions

# MCP Server Setup
server = Server("academic-scraper")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """MCP tools listesi"""
    return [
        Tool(
            name="scrape_academic_profiles",
            description="YÖK Akademik veritabanından profil bilgilerini real-time streaming ile çeker",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Aranacak akademisyen adı"
                    },
                    "email": {
                        "type": "string",
                        "description": "Belirli bir email ile eşleşme aranacaksa (opsiyonel)"
                    },
                    "field_id": {
                        "type": "integer",
                        "description": "Alan ID (fields.json'dan)"
                    },
                    "specialty_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Uzmanlık ID'leri listesi"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_session_status",
            description="Aktif scraping session durumunu kontrol et",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="list_active_sessions",
            description="Aktif scraping session'larını listele",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_session_results",
            description="Session sonuçlarını getir (profiles ve collaborators)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Tool çağrı handler"""
    
    if name == "scrape_academic_profiles":
        # Yeni session oluştur
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        scraper = StreamingAcademicScraper()
        results = []
        
        try:
            # Streaming generator'ı çalıştır
            async for update in scraper.scrape_profiles_streaming(
                name=arguments["name"],
                session_id=session_id,
                field_id=arguments.get("field_id"),
                specialty_ids=arguments.get("specialty_ids"),
                email=arguments.get("email")
            ):
                # Her update'i hemen döndür
                results.append(json.dumps(update, ensure_ascii=False))
                
                # Timeout prevention - her 30 saniyede heartbeat
                if len(results) % 60 == 0:  # ~30 saniye (0.5s * 60)
                    heartbeat = {
                        "type": "heartbeat", 
                        "timestamp": time.time(),
                        "session_id": session_id
                    }
                    results.append(json.dumps(heartbeat, ensure_ascii=False))
        
        except Exception as e:
            error_result = {
                "type": "error",
                "data": {"message": str(e), "session_id": session_id}
            }
            results.append(json.dumps(error_result, ensure_ascii=False))
        
        # Tüm sonuçları birleştir
        final_result = "\n".join(results)
        
        return [types.TextContent(type="text", text=final_result)]
    
    elif name == "get_session_status":
        session_id = arguments["session_id"]
        session = get_session(session_id)
        
        if session:
            status = session.get_status()
        else:
            status = {"session_id": session_id, "status": "not_found"}
        
        return [types.TextContent(type="text", text=json.dumps(status, ensure_ascii=False, indent=2))]
    
    elif name == "list_active_sessions":
        sessions_info = list_sessions()
        return [types.TextContent(type="text", text=json.dumps(sessions_info, ensure_ascii=False, indent=2))]
    
    elif name == "get_session_results":
        session_id = arguments["session_id"]
        session = get_session(session_id)
        
        if session:
            results = {
                "session_id": session_id,
                "profiles": session.profiles,
                "collaborators": session.collaborators,
                "status": session.status,
                "progress": session.progress
            }
        else:
            results = {"session_id": session_id, "status": "not_found"}
        
        return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]
    
    else:
        raise ValueError(f"Bilinmeyen tool: {name}")

async def main():
    """Ana MCP server fonksiyonu"""
    print("🎓 Academic Scraper MCP Server başlatılıyor...")
    print("📡 Smithery ile bağlantı kuruluyor...")
    
    # Stdio üzerinden MCP server'ı çalıştır
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="academic-scraper",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main()) 