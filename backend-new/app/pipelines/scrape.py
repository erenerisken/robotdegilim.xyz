from app.core.logging import get_logger
from app.core.settings import get_setting

def run_scrape():
   try:
    logger=get_logger("scrape")
    error=get_logger("error")

    logger.info("Scraping process started.")

    data_dir=get_setting("DATA_DIR")
    raw_data_dir=data_dir / "raw"
    staged_data_dir=data_dir / "staged"
    published_data_dir=data_dir / "published"
    
    return None,None
   except Exception as e:
      pass