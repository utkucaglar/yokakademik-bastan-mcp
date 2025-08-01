# Academic Scraper MCP Server

🎓 **YÖK Akademik Veritabanı Real-time Streaming Scraper**

[![smithery badge](https://smithery.ai/badge/@utkucaglar/yokakademik-bastan-mcp)](https://smithery.ai/server/@utkucaglar/yokakademik-bastan-mcp)

Bu MCP (Model Context Protocol) server, YÖK Akademik veritabanından akademisyen profil ve işbirlikçi bilgilerini real-time streaming ile çeker ve Smithery ile entegre çalışır.

## 🚀 Özellikler

- **Real-time Streaming**: Progress updates ile anlık durum takibi
- **Email Matching**: Belirli email ile eşleşme arama
- **Field Filtering**: Alan ve uzmanlık bazlı filtreleme
- **Collaborator Scraping**: İşbirlikçi bilgilerini otomatik çekme
- **Session Management**: Çoklu scraping session yönetimi
- **MCP Integration**: Smithery ile tam entegrasyon

## 📁 Proje Yapısı

```
academic-scraper-mcp/
├── src/
│   ├── __init__.py
│   ├── mcp_server.py                 # Ana MCP server
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── academic_scraper.py       # Scraping logic
│   │   └── session_manager.py        # Session yönetimi
│   └── utils/
│       ├── __init__.py
│       └── helpers.py                # Yardımcı fonksiyonlar
├── sessions/                         # Session verileri
├── main_codes/                       # Mevcut scraping kodları
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Proje konfigürasyonu
├── run_server.py                     # Server başlatıcı
└── README.md
```

## 🛠️ Kurulum

### Installing via Smithery

To install yokakademik-bastan-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@utkucaglar/yokakademik-bastan-mcp):

```bash
npx -y @smithery/cli install @utkucaglar/yokakademik-bastan-mcp --client claude
```

### 1. Dependencies Kurulumu

```bash
pip install -r requirements.txt
```

### 2. Chrome WebDriver

Server otomatik olarak ChromeDriver'ı yönetir, manuel kurulum gerekmez.

## 🚀 Kullanım

### MCP Server Başlatma

```bash
python run_server.py
```

### Smithery Konfigürasyonu

`smithery.toml` dosyasına ekleyin:

```toml
[[mcpServers]]
command = "python"
args = ["run_server.py"]
```

## 🔧 MCP Tools

### 1. `scrape_academic_profiles`

Akademisyen profillerini çeker.

**Parametreler:**
- `name` (required): Aranacak akademisyen adı
- `email` (optional): Belirli email ile eşleşme
- `field_id` (optional): Alan ID (fields.json'dan)
- `specialty_ids` (optional): Uzmanlık ID'leri listesi

**Örnek:**
```json
{
  "name": "Ahmet Yılmaz",
  "email": "ahmet.yilmaz@example.com",
  "field_id": 2,
  "specialty_ids": [1, 3]
}
```

### 2. `get_session_status`

Session durumunu kontrol eder.

**Parametreler:**
- `session_id` (required): Session ID

### 3. `list_active_sessions`

Aktif session'ları listeler.

### 4. `get_session_results`

Session sonuçlarını getirir.

**Parametreler:**
- `session_id` (required): Session ID

## 📊 Streaming Response Format

Server real-time streaming ile çalışır:

```json
{"type": "progress", "data": {"progress": 25, "step": "Profil işleniyor..."}}
{"type": "profile_added", "data": {"profile": {...}, "count": 5, "progress": 30}}
{"type": "email_match", "data": {"profile": {...}, "message": "Email bulundu!"}}
{"type": "collaborator_added", "data": {"collaborator": {...}, "count": 3, "total": 10}}
{"type": "completed", "data": {"session_id": "...", "profiles_count": 15, "collaborators_count": 8}}
```

## 🔍 Alan ve Uzmanlık Filtreleme

`fields.json` dosyasından alan ve uzmanlık ID'lerini kullanabilirsiniz:

```json
{
  "id": 2,
  "name": "Fen Bilimleri ve Matematik Temel Alanı",
  "specialties": [
    {"id": 1, "name": "Biyoloji"},
    {"id": 2, "name": "Fizik"},
    {"id": 3, "name": "İstatistik"}
  ]
}
```

## 📁 Session Verileri

Her scraping session'ı `sessions/` klasöründe saklanır:

```
sessions/session_20241201_143022_abc123/
├── session.json          # Session durumu
├── profiles.json         # Profil verileri
└── collaborators.json    # İşbirlikçi verileri
```

## 🐛 Hata Yönetimi

- **WebDriver Hataları**: Otomatik yeniden başlatma
- **Network Timeout**: Retry mekanizması
- **Session Timeout**: Heartbeat ile koruma
- **Memory Management**: Progressive loading

## 🔒 Güvenlik

- Headless browser kullanımı
- Rate limiting (0.5s bekleme)
- Session isolation
- Error logging

## 📈 Performans

- **Concurrent Sessions**: Çoklu session desteği
- **Memory Efficient**: Progressive data loading
- **Network Optimized**: Minimal HTTP requests
- **Caching**: Session-based caching

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorunlar için GitHub Issues kullanın veya email gönderin.

---

**🎓 Academic Scraper MCP Server** - YÖK Akademik veritabanı real-time streaming scraper 