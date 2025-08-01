"""
Akademik scraping logic
"""
import asyncio
import json
import time
from typing import Any, Dict, Generator, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from ..utils.helpers import load_fields, get_field_name_by_id, get_specialty_name_by_id, parse_labels_and_keywords
from .session_manager import AcademicScrapingSession


class StreamingAcademicScraper:
    """Streaming Academic Scraper - Real-time progress updates ile"""
    
    def __init__(self):
        self.driver = None
        self.session = None
        self.fields_data = load_fields()
        
    def setup_driver(self):
        """WebDriver kurulumu"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0")
        
        # Performans optimizasyonu
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.set_window_size(1920, 1080)
    
    async def scrape_profiles_streaming(self, name: str, session_id: str, 
                                      field_id: Optional[int] = None,
                                      specialty_ids: Optional[List[int]] = None,
                                      email: Optional[str] = None) -> Generator[Dict, None, None]:
        """
        Ana profil scraping işlemi - streaming progress updates ile
        """
        
        self.session = AcademicScrapingSession(session_id)
        
        try:
            # Progress: 5% - WebDriver kurulumu
            self.session.update_progress(5, "WebDriver başlatılıyor...")
            yield {"type": "progress", "data": {"progress": 5, "step": "WebDriver başlatılıyor..."}}
            
            self.setup_driver()
            
            # Progress: 10% - YÖK sitesine giriş
            self.session.update_progress(10, "YÖK Akademik sitesine bağlanılıyor...")
            yield {"type": "progress", "data": {"progress": 10, "step": "YÖK sitesine bağlanılıyor..."}}
            
            self.driver.get("https://akademik.yok.gov.tr/AkademikArama/")
            
            # Çerez onayı
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Tümünü Kabul Et')]"))
                ).click()
            except:
                pass
            
            # Progress: 15% - Arama yapılıyor
            self.session.update_progress(15, f"'{name}' için arama yapılıyor...")
            yield {"type": "progress", "data": {"progress": 15, "step": f"'{name}' için arama yapılıyor..."}}
            
            # Arama
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "aramaTerim"))
            )
            
            search_box = self.driver.find_element(By.ID, "aramaTerim")
            search_box.send_keys(name)
            self.driver.find_element(By.ID, "searchButton").click()
            
            # Akademisyenler sekmesine geç
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Akademisyenler"))
            ).click()
            
            # Progress: 20% - Profiller yükleniyor
            self.session.update_progress(20, "Profil listesi yükleniyor...")
            yield {"type": "progress", "data": {"progress": 20, "step": "Profil listesi yükleniyor..."}}
            
            # Profilleri çek
            profile_count = 0
            page_num = 1
            progress_step = 70 / 100  # 20-90 arası progress için
            
            while profile_count < 100:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tr[id^='authorInfo_']"))
                    )
                except:
                    break
                
                profile_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr[id^='authorInfo_']")
                
                if not profile_rows:
                    break
                
                for i, row in enumerate(profile_rows):
                    if profile_count >= 100:
                        break
                    
                    try:
                        # Profil bilgilerini çek
                        profile_data = self._extract_profile_data(row, profile_count + 1)
                        
                        # Filtreleme (field_id, specialty_ids)
                        if field_id or specialty_ids:
                            if not self._filter_profile(profile_data, field_id, specialty_ids):
                                continue
                        
                        # Email kontrolü
                        if email and profile_data.get('email', '').lower() == email.lower():
                            # Email eşleşmesi bulundu!
                            self.session.add_profile(profile_data)
                            
                            yield {"type": "email_match", "data": {
                                "profile": profile_data,
                                "message": f"Email eşleşmesi bulundu: {profile_data['name']}"
                            }}
                            
                            # İşbirlikçi scraping'i başlat
                            async for collab_update in self._scrape_collaborators_streaming(profile_data):
                                yield collab_update
                            
                            return
                        
                        self.session.add_profile(profile_data)
                        profile_count += 1
                        
                        # Progress güncelle
                        current_progress = 20 + (profile_count * progress_step)
                        self.session.update_progress(
                            int(current_progress), 
                            f"Profil {profile_count}/100 işlendi: {profile_data['name']}"
                        )
                        
                        # Her profil için update gönder
                        yield {"type": "profile_added", "data": {
                            "profile": profile_data,
                            "count": profile_count,
                            "progress": int(current_progress)
                        }}
                        
                        # 0.5 saniye bekle (timeout prevention)
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        print(f"Profil işlenirken hata: {e}")
                        continue
                
                # Pagination
                try:
                    pagination = self.driver.find_element(By.CSS_SELECTOR, "ul.pagination")
                    active_li = pagination.find_element(By.CSS_SELECTOR, "li.active")
                    all_lis = pagination.find_elements(By.TAG_NAME, "li")
                    active_index = all_lis.index(active_li)
                    
                    if active_index == len(all_lis) - 1:
                        break
                    
                    next_li = all_lis[active_index + 1]
                    next_a = next_li.find_element(By.TAG_NAME, "a")
                    next_a.click()
                    page_num += 1
                    
                    # Sayfa değişimi için bekle
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Pagination hatası: {e}")
                    break
            
            # Progress: 90% - Scraping tamamlandı
            self.session.update_progress(90, "Profil scraping tamamlandı")
            yield {"type": "progress", "data": {"progress": 90, "step": "Profil scraping tamamlandı"}}
            
        except Exception as e:
            self.session.error_message = str(e)
            self.session.status = "error"
            yield {"type": "error", "data": {"message": str(e)}}
            
        finally:
            if self.driver:
                self.driver.quit()
            
            # Final progress
            self.session.update_progress(100, "İşlem tamamlandı")
            yield {"type": "completed", "data": {
                "session_id": session_id,
                "profiles_count": len(self.session.profiles),
                "collaborators_count": len(self.session.collaborators)
            }}
    
    async def _scrape_collaborators_streaming(self, profile_data: Dict) -> Generator[Dict, None, None]:
        """İşbirlikçi scraping - streaming"""
        
        try:
            self.session.update_progress(50, f"{profile_data['name']} için işbirlikçiler çekiliyor...")
            yield {"type": "progress", "data": {"progress": 50, "step": "İşbirlikçiler çekiliyor..."}}
            
            # Profil sayfasına git
            self.driver.get(profile_data['url'])
            
            # İşbirlikçiler sekmesine geç
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='viewAuthorGraphs.jsp']"))
            ).click()
            
            # SVG yüklenene kadar bekle
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "svg g")) > 2
            )
            
            # JavaScript ile işbirlikçileri çek
            script = """
            const gs = document.querySelectorAll('svg g');
            const results = [];
            for (let i = 2; i < gs.length; i++) {
                const name = gs[i].querySelector('text')?.textContent.trim() || '';
                gs[i].dispatchEvent(new MouseEvent('click', { bubbles: true }));
                const href = document.getElementById('pageUrl')?.href || '';
                results.push({ name, href });
            }
            return results;
            """
            
            collaborators_data = self.driver.execute_script(script)
            
            # Her işbirlikçi için detay çek
            for i, collab in enumerate(collaborators_data):
                try:
                    if collab['href']:
                        self.driver.get(collab['href'])
                        
                        # Detay bilgileri çek
                        collab_detail = self._extract_collaborator_data(collab, i + 1)
                        self.session.add_collaborator(collab_detail)
                        
                        # Progress update
                        collab_progress = 50 + ((i + 1) / len(collaborators_data)) * 40
                        self.session.update_progress(
                            int(collab_progress),
                            f"İşbirlikçi {i + 1}/{len(collaborators_data)}: {collab['name']}"
                        )
                        
                        yield {"type": "collaborator_added", "data": {
                            "collaborator": collab_detail,
                            "count": i + 1,
                            "total": len(collaborators_data),
                            "progress": int(collab_progress)
                        }}
                        
                        await asyncio.sleep(0.5)
                        
                except Exception as e:
                    print(f"İşbirlikçi detayı çekilirken hata: {e}")
                    
        except Exception as e:
            yield {"type": "error", "data": {"message": f"İşbirlikçi scraping hatası: {e}"}}
    
    def _extract_profile_data(self, row, profile_id: int) -> Dict:
        """Profil verilerini çıkar"""
        try:
            info_td = row.find_element(By.XPATH, "./td[h6]")
            link = row.find_element(By.CSS_SELECTOR, "a")
            img = row.find_element(By.CSS_SELECTOR, "img")
            
            name = link.text.strip()
            url = link.get_attribute("href")
            info = info_td.text.strip()
            img_src = img.get_attribute("src") if img else "/default_photo.jpg"
            
            info_lines = info.splitlines()
            title = info_lines[0].strip() if len(info_lines) > 0 else name
            header = info_lines[2].strip() if len(info_lines) > 2 else ''
            
            # Labels
            all_links = info_td.find_elements(By.CSS_SELECTOR, 'a.anahtarKelime')
            green_label = all_links[0].text.strip() if len(all_links) > 0 else ''
            blue_label = all_links[1].text.strip() if len(all_links) > 1 else ''
            
            # Email
            email = ''
            try:
                email_link = row.find_element(By.CSS_SELECTOR, "a[href^='mailto']")
                email = email_link.text.strip().replace('[at]', '@')
            except:
                pass
            
            return {
                "id": profile_id,
                "name": name,
                "title": title,
                "url": url,
                "info": info,
                "header": header,
                "green_label": green_label,
                "blue_label": blue_label,
                "email": email,
                "photoUrl": img_src
            }
            
        except Exception as e:
            print(f"Profil verisi çıkarılırken hata: {e}")
            return {}
    
    def _extract_collaborator_data(self, collab_data: Dict, collab_id: int) -> Dict:
        """İşbirlikçi verilerini çıkar"""
        try:
            # Temel bilgiler
            result = {
                "id": collab_id,
                "name": collab_data['name'],
                "url": collab_data['href'],
                "status": "completed",
                "deleted": False
            }
            
            if not collab_data['href']:
                result["deleted"] = True
                result["photoUrl"] = "/default_photo.jpg"
                return result
            
            # Detay sayfasından bilgi çek
            tds = self.driver.find_elements(By.XPATH, "//td[h6]")
            
            if not tds:
                result["deleted"] = True
                result["photoUrl"] = "/default_photo.jpg"
                return result
            
            info = tds[0].text
            info_lines = info.splitlines()
            
            result.update({
                "title": info_lines[0].strip() if len(info_lines) > 0 else collab_data['name'],
                "info": info_lines[2].strip() if len(info_lines) > 2 else '',
                "green_label": '',
                "blue_label": '',
                "keywords": '',
                "email": ''
            })
            
            # Labels ve keywords
            try:
                green_span = tds[0].find_element(By.CSS_SELECTOR, 'span.label-success')
                result["green_label"] = green_span.text.strip()
            except:
                pass
            
            try:
                blue_span = tds[0].find_element(By.CSS_SELECTOR, 'span.label-primary')
                result["blue_label"] = blue_span.text.strip()
            except:
                pass
            
            # Email
            try:
                email_link = tds[0].find_element(By.CSS_SELECTOR, "a[href^='mailto']")
                result["email"] = email_link.text.strip().replace('[at]', '@')
            except:
                pass
            
            # Foto
            try:
                img = self.driver.find_element(By.CSS_SELECTOR, "img.img-circle, img#imgPicture")
                result["photoUrl"] = img.get_attribute("src")
            except:
                result["photoUrl"] = "/default_photo.jpg"
            
            return result
            
        except Exception as e:
            print(f"İşbirlikçi verisi çıkarılırken hata: {e}")
            return collab_data
    
    def _filter_profile(self, profile: Dict, field_id: Optional[int], specialty_ids: Optional[List[int]]) -> bool:
        """Profil filtreleme"""
        if not field_id and not specialty_ids:
            return True
        
        # Field ID kontrolü
        if field_id:
            field_name = get_field_name_by_id(self.fields_data, field_id)
            if field_name and profile.get('green_label') != field_name:
                return False
        
        # Specialty ID kontrolü
        if specialty_ids and field_id:
            profile_specialty = profile.get('blue_label', '')
            for specialty_id in specialty_ids:
                specialty_name = get_specialty_name_by_id(self.fields_data, field_id, specialty_id)
                if specialty_name and profile_specialty == specialty_name:
                    return True
            return False
        
        return True 