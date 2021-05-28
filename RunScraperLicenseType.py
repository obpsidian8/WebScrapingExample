from CurlScraper.ARMedBoardCurl import ARMedBoard
from SeleniumScraper.ARMedBoard import ARMedboardSeleniumScraper
import json


def scrape_armedboard(method="curl"):
    license_num = "PA-340"

    if method == "curl":
        ar_med_curl = ARMedBoard(cookies_dict=None)
        license_info = ar_med_curl.get_license_info(license_num)
        print(json.dumps(license_info, indent=2))

    elif method == "selenium":
        ar_med_sel = ARMedboardSeleniumScraper()
        license_info2 = ar_med_sel.scrape_page(license_number=license_num)
        print(json.dumps(license_info2, indent=2))


if __name__ == "__main__":
    scrape_armedboard()
