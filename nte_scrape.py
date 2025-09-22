import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "https://muhfd.metu.edu.tr"
NTE_COURSES_URL = "https://muhfd.metu.edu.tr/en/nte-courses"

def get_department_links():
    """
    'NTE Courses' sayfasındaki departman linklerini (department-...) toplayıp bir liste döndürür.
    """
    resp = requests.get(NTE_COURSES_URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    department_links = []

    for link in soup.find_all('a'):
        href = link.get('href', '')
        # Ör: href="department-architecture"
        if "department-" in href:
            # /en/ ifadesi gerekebilir, urljoin ile birleştiriyoruz:
            full_url = urljoin(BASE_URL + "/en/", href)
            department_links.append(full_url)
            try:
                department_links.append("https://muhfd.metu.edu.tr/en/computer-education-and-instructional-technology")
            except:
                pass

            try:
                department_links.append("https://muhfd.metu.edu.tr/en/meslek-yuksek-okulu-myo")
            except:
                pass

    return department_links

def get_department_data(dept_url):
    """
    Verilen departman sayfasından:
      - department_name (ör. 'Department of Architecture')
      - courses = [ { "code": "...", "name": "...", "credits": "..." }, ... ]
    döndürür.
    """
    r = requests.get(dept_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    # 1) Departman adını al
    header_el = soup.find('h1', id='page-title')
    if header_el:
        department_name = header_el.get_text(strip=True)
    else:
        department_name = "Unknown Department"

    # 2) Tabloyu bul
    table = soup.find('table')
    courses = []

    if table:
        rows = table.find_all('tr')
        # İlk satır tablo başlığı, [1:] ile atlıyoruz
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                code = cols[0].get_text(strip=True)
                name = cols[1].get_text(strip=True)
                credits = cols[2].get_text(strip=True)
                courses.append({
                    "code": code,
                    "name": name,
                    "credits": credits
                })

    return department_name, courses

def main():
    # Departmanları tutacağımız sözlük (dict). 
    # Her key bir departman adı, value ise bu departmandaki dersleri TUTAN BİR SET.
    # (set -> {(code, name, credits), ...})
    departments_dict = {}

    # 1) Tüm departman linklerini al
    dept_links = get_department_links()
    print("[INFO] Bulunan departman link sayısı:", len(dept_links))

    # 2) Her departmandan verileri topla
    for link in dept_links:
        dept_name, courses = get_department_data(link)
        
        # Eğer bu departman yoksa, set olarak başlat
        if dept_name not in departments_dict:
            departments_dict[dept_name] = set()
        
        # Şimdi bu departmandaki "courses" listesini set'e ekle
        for c in courses:
            # (code, name, credits) -> tuple halinde ekliyoruz ki set içinde tutulabilsin
            departments_dict[dept_name].add((c["code"], c["name"], c["credits"]))

    # 3) JSON’a yazmadan önce set'i liste-dict formatına dönüştür
    final_output = {}
    for dept_name, course_set in departments_dict.items():
        # Bu departmandaki course_set -> {(code, name, credits), ...}
        course_list = []
        for (code, name, credits) in course_set:
            course_list.append({
                "code": code,
                "name": name,
                "credits": credits
            })
        final_output[dept_name] = course_list

    # 4) JSON dosyasına kaydet
    with open("nte_deneme.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
    
    print("[SUCCESS] 'nte_yeni.json' dosyasına yazıldı.")
    print("[INFO] Toplam departman:", len(final_output))

if __name__ == "__main__":
    main()
