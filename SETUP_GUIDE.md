# Academic Scraper MCP Server - Kurulum Rehberi

## 🎯 Proje Özeti

Bu proje, mevcut YÖK Akademik scraping kodlarınızı **real-time streaming** yapan bir **MCP (Model Context Protocol) server**'a dönüştürür. Smithery ile entegre çalışarak, AI asistanlarınızın YÖK veritabanından akademisyen bilgilerini çekmesini sağlar.

## 🚀 Hızlı Başlangıç

### 1. Dependencies Kurulumu

```bash
pip install -r requirements.txt
```

### 2. Test Etme

```bash
python test_mcp_server.py
```

### 3. MCP Server Başlatma

```bash
python run_server.py
```

## 📁 Proje Yapısı

```
academic-scraper-mcp/
├── src/                          # Ana kaynak kodlar
│   ├── mcp_server.py             # MCP server ana dosyası
│   ├── scraper/
│   │   ├── academic_scraper.py   # Scraping logic (mevcut kodlarınızdan)
│   │   └── session_manager.py    # Session yönetimi
│   └── utils/
│       └── helpers.py            # Yardımcı fonksiyonlar
├── sessions/                     # Session verileri (otomatik oluşur)
├── config/
│   └── settings.json            # Konfigürasyon
├── main_codes/                  # Mevcut scraping kodlarınız
├── requirements.txt             # Python dependencies
├── run_server.py               # Server başlatıcı
└── test_mcp_server.py         # Test script'i
```

## 🔧 MCP Tools

### 1. `scrape_academic_profiles`

**Amaç:** Akademisyen profillerini real-time streaming ile çeker

**Parametreler:**
- `name` (required): Aranacak akademisyen adı
- `email` (optional): Belirli email ile eşleşme
- `field_id` (optional): Alan ID (fields.json'dan)
- `specialty_ids` (optional): Uzmanlık ID'leri listesi

**Örnek Kullanım:**
```json
{
  "name": "Ahmet Yılmaz",
  "email": "ahmet.yilmaz@example.com",
  "field_id": 2,
  "specialty_ids": [1, 3]
}
```

### 2. `get_session_status`

**Amaç:** Session durumunu kontrol eder

**Parametreler:**
- `session_id` (required): Session ID

### 3. `list_active_sessions`

**Amaç:** Aktif session'ları listeler

### 4. `get_session_results`

**Amaç:** Session sonuçlarını getirir

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

`main_codes/public/fields.json` dosyasından alan ve uzmanlık ID'lerini kullanabilirsiniz:

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

## 🎯 Smithery Entegrasyonu

### 1. Smithery Konfigürasyonu

`smithery.toml` dosyasına ekleyin:

```toml
[[mcpServers]]
command = "python"
args = ["run_server.py"]
```

### 2. Kullanım Örneği

Smithery'de şu şekilde kullanabilirsiniz:

```
"Ahmet Yılmaz adında bir akademisyen bul ve profillerini çek"
```

AI asistan otomatik olarak:
1. `scrape_academic_profiles` tool'unu çağırır
2. Real-time progress updates alır
3. Sonuçları analiz eder
4. Size rapor verir

## 📁 Session Verileri

Her scraping session'ı `sessions/` klasöründe saklanır:

```
sessions/session_20241201_143022_abc123/
├── session.json          # Session durumu
├── profiles.json         # Profil verileri
└── collaborators.json    # İşbirlikçi verileri
```

## 🧪 Test Etme

### 1. Unit Test

```bash
python test_mcp_server.py
```

### 2. MCP Server Test

```bash
python run_server.py
```

### 3. Smithery Test

Smithery'de şu komutları deneyin:

```
"Ahmet Yılmaz'ı ara ve profillerini getir"
"Fen Bilimleri alanında çalışan akademisyenleri bul"
"test@example.com email'ine sahip akademisyeni bul"
```

## 🔧 Konfigürasyon

`config/settings.json` dosyasından ayarları değiştirebilirsiniz:

```json
{
  "scraping": {
    "max_profiles": 100,
    "max_collaborators": 50,
    "timeout": 30,
    "delay_between_requests": 0.5
  },
  "webdriver": {
    "headless": true,
    "window_size": {"width": 1920, "height": 1080}
  }
}
```

## 🐛 Sorun Giderme

### 1. ChromeDriver Hatası

Server otomatik olarak ChromeDriver'ı yönetir. Manuel kurulum gerekmez.

### 2. Network Timeout

`config/settings.json`'da timeout değerlerini artırın.

### 3. Memory Sorunları

`max_profiles` ve `max_collaborators` değerlerini düşürün.

### 4. Session Temizleme

Eski session'lar otomatik temizlenir. Manuel temizlik için:

```bash
rm -rf sessions/*
```

## 📈 Performans Optimizasyonu

1. **Concurrent Sessions**: Çoklu session desteği
2. **Memory Efficient**: Progressive data loading
3. **Network Optimized**: Minimal HTTP requests
4. **Caching**: Session-based caching

## 🔒 Güvenlik

- Headless browser kullanımı
- Rate limiting (0.5s bekleme)
- Session isolation
- Error logging

## 🎉 Başarı!

Artık AI asistanlarınız YÖK Akademik veritabanından real-time streaming ile veri çekebilir!

---

**🎓 Academic Scraper MCP Server** - YÖK Akademik veritabanı real-time streaming scraper 