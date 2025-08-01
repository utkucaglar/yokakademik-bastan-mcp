# Academic Scraper MCP Server

YÖK Akademik veritabanından akademik profil ve işbirlikçi bilgilerini çeken real-time streaming MCP (Model Context Protocol) server.

## 🚀 Özellikler

- **Real-time Streaming**: Anlık güncellemeler ile scraping işlemi
- **Session Management**: Çoklu scraping session'larını yönetme
- **Flexible API**: Tek tool çağrısında direkt sonuç veya session-based yaklaşım
- **Academic Database**: YÖK Akademik veritabanı entegrasyonu
- **Collaborator Detection**: Akademik işbirlikçileri otomatik tespit

## 🛠️ MCP Tools

### 1. `scrape_academic_profiles`
Akademik profil scraping - direkt sonuç döndürür

**Parametreler:**
- `name` (required): Aranacak akademisyen adı
- `field_id` (optional): Alan ID
- `specialty_ids` (optional): Uzmanlık ID'leri array
- `email` (optional): Email adresi (tam eşleşme için)
- `wait_for_completion` (optional): Tamamlanmasını bekle (true) veya session başlat (false)

**Kullanım:**
```json
{
  "name": "scrape_academic_profiles",
  "arguments": {
    "name": "Ahmet Yılmaz",
    "wait_for_completion": true
  }
}
```

### 2. `get_session_status`
Session durumunu kontrol et

### 3. `list_active_sessions`
Aktif scraping session'larını listele

### 4. `get_session_results`
Session sonuçlarını getir (profiles ve collaborators)

## 📦 Kurulum

```bash
# Dependencies yükle
pip install -r requirements.txt

# Server'ı başlat
python run_server.py
```

## 🔧 Geliştirme

```bash
# Test et
python test_mcp_server.py

# Smithery ile deploy et
# smithery.yaml otomatik oluşturulacak
```

## 📁 Proje Yapısı

```
proje_apisiz/
├── src/
│   ├── mcp_server.py          # MCP Server ana dosyası
│   ├── scraper/
│   │   ├── academic_scraper.py    # Scraping logic
│   │   └── session_manager.py     # Session management
│   └── utils/
│       └── helpers.py             # Utility functions
├── main_codes/
│   └── public/
│       └── fields.json            # Academic fields database
├── requirements.txt               # Python dependencies
├── pyproject.toml               # Project configuration
└── run_server.py                # Server launcher
```

## 🎯 Kullanım Örnekleri

### Tek Tool Çağrısında Direkt Sonuç
```json
{
  "name": "scrape_academic_profiles",
  "arguments": {
    "name": "Ahmet Yılmaz",
    "wait_for_completion": true
  }
}
```

### Session-based Yaklaşım
```json
{
  "name": "scrape_academic_profiles",
  "arguments": {
    "name": "Ahmet Yılmaz",
    "wait_for_completion": false
  }
}
```

Sonra `get_session_status` ile durumu kontrol edin.

## 🔍 Academic Fields

`main_codes/public/fields.json` dosyası akademik alan ve uzmanlık bilgilerini içerir.

## 📊 Çıktı Formatı

```json
{
  "type": "completed",
  "data": {
    "session_id": "session_20250801_xxx",
    "profiles": [...],
    "collaborators": [...],
    "total_profiles": 24,
    "total_collaborators": 0,
    "message": "'Ahmet Yılmaz' için 24 profil bulundu"
  }
}
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

MIT License - detaylar için `LICENSE` dosyasına bakın.

## 🆘 Destek

Sorunlar için GitHub Issues kullanın veya team@example.com adresine email gönderin. 