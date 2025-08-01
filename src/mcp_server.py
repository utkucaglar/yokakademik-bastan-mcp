#!/usr/bin/env python3
"""
Academic Scraper MCP Server
Real-time streaming scraping için
"""
import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Lazy loading - Selenium import'larını sadece gerektiğinde yap
# from src.scraper.academic_scraper import StreamingAcademicScraper
# from src.scraper.session_manager import create_session, get_session, list_sessions

# MCP Server
server = Server("academic-scraper")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """MCP Tools listesi"""
    return [
        Tool(
            name="scrape_academic_profiles",
            description="Akademik profil scraping - direkt sonuç döndürür",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Aranacak akademisyen adı"
                    },
                    "field_id": {
                        "type": "integer",
                        "description": "Alan ID (opsiyonel)"
                    },
                    "specialty_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Uzmanlık ID'leri (opsiyonel)"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email adresi (opsiyonel - tam eşleşme için)"
                    },
                    "wait_for_completion": {
                        "type": "boolean",
                        "description": "Tamamlanmasını bekle (true) veya session başlat (false)",
                        "default": true
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_session_status",
            description="Session durumunu kontrol et",
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
        # Lazy loading - Selenium import'larını sadece gerektiğinde yap
        try:
            from src.scraper.academic_scraper import StreamingAcademicScraper
            from src.scraper.session_manager import create_session, get_session, list_sessions
        except ImportError as e:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Scraping modülleri yüklenemedi: {str(e)}"
            }, ensure_ascii=False))]
        
        # Yeni session oluştur
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Session'ı başlat
        create_session(session_id)
        
        # wait_for_completion parametresini kontrol et
        wait_for_completion = arguments.get("wait_for_completion", True)
        
        if wait_for_completion:
            # Direkt scraping yap ve sonucu bekle
            scraper = StreamingAcademicScraper()
            profiles = []
            collaborators = []
            
            try:
                async for update in scraper.scrape_profiles_streaming(
                    name=arguments["name"],
                    session_id=session_id,
                    field_id=arguments.get("field_id"),
                    specialty_ids=arguments.get("specialty_ids"),
                    email=arguments.get("email")
                ):
                    if update.get("type") == "profile_added":
                        profiles.append(update["data"]["profile"])
                    elif update.get("type") == "collaborator_added":
                        collaborators.append(update["data"]["collaborator"])
                    elif update.get("type") == "completed":
                        break
                    elif update.get("type") == "error":
                        return [types.TextContent(type="text", text=json.dumps({
                            "error": update["data"]["message"]
                        }, ensure_ascii=False))]
                
                # Sonuçları döndür
                response = {
                    "type": "completed",
                    "data": {
                        "session_id": session_id,
                        "profiles": profiles,
                        "collaborators": collaborators,
                        "total_profiles": len(profiles),
                        "total_collaborators": len(collaborators),
                        "message": f"'{arguments['name']}' için {len(profiles)} profil bulundu"
                    }
                }
                
                return [types.TextContent(type="text", text=json.dumps(response, ensure_ascii=False))]
                
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({
                    "error": f"Scraping hatası: {str(e)}"
                }, ensure_ascii=False))]
        
        else:
            # Background task olarak scraping'i başlat
            asyncio.create_task(
                run_scraping_background(
                    session_id=session_id,
                    name=arguments["name"],
                    field_id=arguments.get("field_id"),
                    specialty_ids=arguments.get("specialty_ids"),
                    email=arguments.get("email")
                )
            )
            
            # Hemen session bilgisi döndür
            response = {
                "type": "session_started",
                "data": {
                    "session_id": session_id,
                    "message": f"'{arguments['name']}' için scraping başlatıldı",
                    "status": "running",
                    "timestamp": time.time(),
                    "check_status_with": f"get_session_status tool'u ile session_id: {session_id} kullanarak durumu kontrol edebilirsiniz"
                }
            }
            
            return [types.TextContent(type="text", text=json.dumps(response, ensure_ascii=False))]
    
    elif name == "get_session_status":
        # Lazy loading
        try:
            from src.scraper.session_manager import get_session
        except ImportError as e:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Session modülü yüklenemedi: {str(e)}"
            }, ensure_ascii=False))]
        
        session_id = arguments["session_id"]
        session = get_session(session_id)
        
        if session:
            status = session.get_status()
        else:
            status = {"session_id": session_id, "status": "not_found"}
        
        return [types.TextContent(type="text", text=json.dumps(status, ensure_ascii=False, indent=2))]
    
    elif name == "list_active_sessions":
        # Lazy loading
        try:
            from src.scraper.session_manager import list_sessions
        except ImportError as e:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Session modülü yüklenemedi: {str(e)}"
            }, ensure_ascii=False))]
        
        sessions_info = list_sessions()
        return [types.TextContent(type="text", text=json.dumps(sessions_info, ensure_ascii=False, indent=2))]
    
    elif name == "get_session_results":
        # Lazy loading
        try:
            from src.scraper.session_manager import get_session
        except ImportError as e:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Session modülü yüklenemedi: {str(e)}"
            }, ensure_ascii=False))]
        
        session_id = arguments["session_id"]
        session = get_session(session_id)
        
        if session:
            results = {
                "session_id": session_id,
                "profiles": session.profiles,
                "collaborators": session.collaborators,
                "status": session.status,
                "progress": session.progress,
                "total_profiles": len(session.profiles),
                "total_collaborators": len(session.collaborators)
            }
        else:
            results = {"session_id": session_id, "error": "Session bulunamadı"}
        
        return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]

async def run_scraping_background(session_id: str, name: str, field_id: int = None, 
                                 specialty_ids: List[int] = None, email: str = None):
    """Background'da scraping çalıştır"""
    # Lazy loading
    try:
        from src.scraper.academic_scraper import StreamingAcademicScraper
        from src.scraper.session_manager import get_session
    except ImportError as e:
        print(f"Background scraping hatası: {e}", file=sys.stderr)
        return
    
    scraper = StreamingAcademicScraper()
    
    try:
        async for update in scraper.scrape_profiles_streaming(
            name=name,
            session_id=session_id,
            field_id=field_id,
            specialty_ids=specialty_ids,
            email=email
        ):
            # Session'a update'i kaydet (real-time için)
            session = get_session(session_id)
            if session:
                session.last_update = update
                session.last_update_time = time.time()
    
    except Exception as e:
        session = get_session(session_id)
        if session:
            session.error_message = str(e)
            session.status = "error"

async def main():
    """MCP Server başlat"""
    # JSON-RPC protokolü için stderr'e print yapmıyoruz
    # stdio transport
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 