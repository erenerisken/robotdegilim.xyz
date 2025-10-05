import logging
from bs4 import BeautifulSoup


from backend.src.errors import AbortNteListError
from src.config import app_constants
from src.utils.io import write_json
from src.nte.fetch import get_nte_courses, get_department_data
from src.nte.parse import extract_courses, extract_department_links

logger = logging.getLogger(app_constants.log_nte_list)

def nte_list():
    try:
        # Departmanları tutacağımız sözlük (dict). 
        # Her key bir departman adı, value ise bu departmandaki dersleri TUTAN BİR SET.
        # (set -> {(code, name, credits), ...})
        departments_dict = {}

        # 1) Tüm departman linklerini al
        resp = get_nte_courses()
        soup = BeautifulSoup(resp.text, 'html.parser')
        dept_links = []
        extract_department_links(soup, dept_links)
        logging.info("Bulunan departman link sayısı:", len(dept_links))

        # 2) Her departmandan verileri topla
        for link in dept_links:
            resp = get_department_data(link)
            soup = BeautifulSoup(resp.text, 'html.parser')
            courses = []
            dept_name = extract_courses(soup, courses)
            
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
        write_json(final_output, app_constants.nte_list_json)
        logging.info("Toplam departman sayısı:", len(final_output))
    except Exception as e:
        raise AbortNteListError(f"Failed to process NTE list, error: {str(e)}") from e
