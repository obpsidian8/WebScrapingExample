from CurlScraper.ARMedBoardCurl import ARMedBoard
from CurlScraper.DCHealthCurl import DCHealth
from SeleniumScraper.ARMedBoard import ARMedboardSeleniumScraper
import json


def scrape_armedboard(method="c"):
    license_num = "PA-340"

    if method == "c":
        ar_med_curl = ARMedBoard(cookies_dict=None)
        license_info = ar_med_curl.get_license_info(license_num)
        print(f"\n")
        print(json.dumps(license_info, indent=2))

    elif method == "s":
        ar_med_sel = ARMedboardSeleniumScraper()
        license_info2 = ar_med_sel.scrape_page(license_number=license_num)
        print(f"\n")
        print(json.dumps(license_info2, indent=2))


def scrape_dc_health(method="c"):
    license_num = "PT870060"
    if method == "c":
        dc_med_curl = DCHealth(cookies_dict=None)
        license_info = dc_med_curl.get_license_info(license_num)
        print(f"\n")
        print(json.dumps(license_info, indent=2))


if __name__ == "__main__":
    scrape_dc_health("c")
    # scrape_armedboard("c")
    print("Done")
