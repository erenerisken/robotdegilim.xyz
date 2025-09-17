#!/usr/bin/env python3
"""
NTE Backend Test Script
Bu script backend'in NTE işlemlerini test eder.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:3000"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_status():
    """Backend durumunu kontrol et."""
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        log(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            log(f"Backend Status: {data.get('status', 'unknown')}")
            log(f"Departments Ready: {data.get('depts_ready', False)}")
            log(f"Queued Musts: {data.get('queued_musts', False)}")
            log(f"Version: {data.get('version', 'unknown')}")
            return True
        else:
            log(f"Status Error: {response.text}")
            return False
    except Exception as e:
        log(f"Status Request Failed: {e}")
        return False

def test_scrape():
    """Scraping işlemini başlat ve NTE processing'i tetikle."""
    try:
        log("🚀 Starting scrape request...")
        response = requests.get(f"{BASE_URL}/run-scrape", timeout=300)  # 5 dakika timeout
        
        log(f"Scrape Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Success: {data.get('status', 'unknown')}")
            return True
        elif response.status_code == 503:
            data = response.json()
            log(f"⏳ Busy: {data.get('status', 'system busy')}")
            return False
        else:
            log(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log("⏰ Scrape request timed out (this is normal for long operations)")
        return True  # Timeout normal olabilir
    except Exception as e:
        log(f"❌ Scrape Request Failed: {e}")
        return False

def check_s3_files():
    """S3'te oluşan dosyaları kontrol et."""
    files_to_check = [
        ("https://robotd.s3.eu-central-1.amazonaws.com/data.json", "Course Data"),
        ("https://robotd.s3.eu-central-1.amazonaws.com/departments.json", "Departments Data"),
        ("https://robotd.s3.eu-central-1.amazonaws.com/nte-available.json", "NTE Available")
    ]
    
    log("🔍 Checking S3 files...")
    
    for url, name in files_to_check:
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                log(f"✅ {name}: Available")
                # Son değişiklik zamanını kontrol et
                if 'last-modified' in response.headers:
                    log(f"   Last Modified: {response.headers['last-modified']}")
            else:
                log(f"❌ {name}: Not found ({response.status_code})")
        except Exception as e:
            log(f"❌ {name}: Error checking - {e}")

def check_nte_content():
    """NTE dosyasının içeriğini kontrol et."""
    try:
        log("📄 Checking NTE content...")
        response = requests.get("https://robotd.s3.eu-central-1.amazonaws.com/nte-available.json", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ NTE file loaded successfully")
            log(f"   Total NTE courses: {len(data)}")
            
            if len(data) > 0:
                # İlk birkaç dersi göster
                log("   Sample courses:")
                for i, course in enumerate(data[:3]):
                    code = course.get('code', {})
                    dept_code = code.get('departmental', 'N/A')
                    name = course.get('name', 'N/A')
                    sections = len(course.get('sections', []))
                    log(f"     {i+1}. {dept_code} - {name[:50]}... ({sections} sections)")
            
            return True
        else:
            log(f"❌ NTE file not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ NTE content check failed: {e}")
        return False

def check_logs():
    """Log dosyalarını kontrol et."""
    import os
    from pathlib import Path
    
    log_dir = Path("storage/logs")
    if log_dir.exists():
        log("📋 Checking log files...")
        for log_file in log_dir.glob("*.log"):
            size = log_file.stat().st_size
            log(f"   {log_file.name}: {size} bytes")
            
            # Son birkaç log satırını göster
            if log_file.name == "jobs.log" and size > 0:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            log("   Recent job logs:")
                            for line in lines[-5:]:  # Son 5 satır
                                log(f"     {line.strip()}")
                except Exception as e:
                    log(f"   Error reading {log_file.name}: {e}")
    else:
        log("📋 No log directory found")

def main():
    log("🧪 NTE Backend Test Started")
    log("=" * 50)
    
    # 1. Backend durumu
    if not test_status():
        log("❌ Backend not responding. Make sure it's running on port 3000")
        return
    
    time.sleep(1)
    
    # 2. Scraping testi (bu NTE processing'i de tetikler)
    log("\n" + "=" * 50)
    log("🔄 Testing Scrape + NTE Processing...")
    
    scrape_success = test_scrape()
    
    # 3. Biraz bekle (işlem tamamlansın)
    if scrape_success:
        log("⏳ Waiting for processing to complete...")
        time.sleep(10)  # 10 saniye bekle
        
        # 4. S3 dosyalarını kontrol et
        log("\n" + "=" * 50)
        check_s3_files()
        
        # 5. NTE içeriğini kontrol et
        log("\n" + "=" * 50)
        check_nte_content()
    
    # 6. Log dosyalarını kontrol et
    log("\n" + "=" * 50)
    check_logs()
    
    log("\n" + "=" * 50)
    log("🏁 Test completed!")

if __name__ == "__main__":
    main() 