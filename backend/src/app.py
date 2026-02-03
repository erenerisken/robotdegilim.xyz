
# Initialize Flask app (serve static assets from src/public under /static)
app = Flask(
    __name__,
    static_folder=app_constants.static_folder,
    static_url_path='/'
)

class RunScrape(Resource):
    def get(self):
        try:

            # Run NTE list scraping and processing after successful scrape
            nte_metrics = None
            try:
                _, nte_metrics = nte_available()
                if nte_metrics:
                    _logger.info(
                        "nte_available completed",
                        extra={"nte_matched": nte_metrics.get("matched"), "nte_missed": nte_metrics.get("missed")},
                    )
            except Exception as e:
                _logger.error(f"NTE available process failed, error: {str(e)}")
                # Do not fail the whole scrape if NTE fails

            # If a musts run was queued during busy period, run it now
            if st.get("queued_musts"):
                _logger.info("musts run was queued; running after scrape completion (same busy window)")
                try:
                    run_musts()  # already busy from earlier
                    set_status(queued_musts=False)
                    return {"status": "Scraping and NTE completed; musts completed successfully"}, 200
                except Exception as e:
                    _logger.error(f"queued musts run failed, error: {str(e)}")
                    return {"status": "Scraping and NTE completed; musts failed", "code": "ERROR"}, 500
            return {"status": "Scraping and NTE completed successfully"}, 200
        except Exception as e:
            _logger.error(str(e))
            return {"error": "Error running scrape process", "code": "ERROR"}, 500
        finally:
            try:
                # Always attempt to mark idle unless another request changed state
                set_idle()
            except Exception as e:
                _logger.error(f"failed to set idle after scrape, error: {str(e)}")


class RunMusts(Resource):
    def get(self):
        st = get_status()
        # If departments data is not ready yet, queue and exit
        if not st.get("depts_ready"):
            if not st.get("queued_musts"):
                set_status(queued_musts=True)
                return {
                    "status": "Departments data unavailable; musts queued to run after scrape",
                    "code": "QUEUED",
                }, 202
            return {
                "status": "Musts already queued; waiting for scrape to produce data",
                "code": "QUEUED",
            }, 202

        # If system currently busy (e.g., scrape in progress), queue
        if st.get("status") == "busy":
            if not st.get("queued_musts"):
                set_status(queued_musts=True)
                return {
                    "status": "System busy; musts queued to run after scrape",
                    "code": "QUEUED",
                }, 202
            return {"status": "System busy; musts already queued", "code": "QUEUED"}, 202

        try:
            set_busy()
            run_musts()
            set_status(queued_musts=False)

            # Run NTE list scraping and processing after successful scrape
            try:
                nte_path = nte_list()
                _logger.info("nte_list completed", extra={"nte_list_path": nte_path})
            except Exception as e:
                _logger.error(f"NTE list process failed, error: {str(e)}")
                # Do not fail the whole scrape if NTE fails

            return {"status": "Get musts completed successfully", "code": "OK"}, 200
        except Exception as e:
            _logger.error(str(e))
            if app_constants.noDeptsErrMsg in str(e):
                set_status(depts_ready=False, queued_musts=True)
                _logger.info("departments data missing; queued musts until after scrape")
                return {
                    "status": "Departments data missing; musts queued to run after next scrape",
                    "code": "QUEUED",
                }, 202
            return {"error": "Error running get musts process", "code": "ERROR"}, 500
        finally:
            try:
                set_idle()
            except Exception as ie:
                _logger.error(f"failed to set idle after musts, error: {str(ie)}")