import re
from SeleniumScraper.SeleniumPageNavigator import get_chrome_driver, SelemiumPageNavigetor
from LoggingModule import set_logging

logger = set_logging()

class DCHealthSeleniumScraper:
    SITE_NAME = "DCHealth"
    MAIN_PAGE = "https://doh.force.com/ver/s/"
    LICENSE_SEARCH_URL = "https://doh.force.com/ver/s/"
    ASMB_ID_SEARCH_URL = "http://www.armedicalboard.org/Public/verify/results.aspx?strPHIDNO="
    DIRECTORY_SEARCH_PAGE = "https://doh.force.com/ver/s/"

    def __init__(self):
        self.driver = get_chrome_driver(dataDirName=self.SITE_NAME)
        self.navigator = SelemiumPageNavigetor(self.driver)

