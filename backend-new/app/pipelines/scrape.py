from urllib import response
from app.core.logging import get_logger
from app.scrape.fetch import get_main_page
from app.scrape.parse import extract_current_semester, extract_departments
from app.scrape.io import load_local_dept_prefixes
from app.utils.cache import CacheStore
from bs4 import BeautifulSoup

def run_scrape():
   try:
     logger=get_logger("scrape")
     cache=CacheStore()
     
     logger.info("Scraping process started.")
     
     cache_key, html_hash, response = get_main_page()
     parsed=cache.get(cache_key, html_hash)
     
     current_semester=None
     dept_codes=None
     dept_names=None
     if parsed:
      current_semester=parsed["current_semester"]
      dept_codes=parsed["dept_codes"]
      dept_names=parsed["dept_names"]
     else:
       main_soup = BeautifulSoup(response.text, "html.parser")
       extract_departments(main_soup, dept_codes, dept_names)
       current_semester = extract_current_semester(main_soup)
     
     department_prefixes = load_local_dept_prefixes()
     data={}
     # further logic

     return None,None
   except Exception as e:
      pass