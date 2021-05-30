from CurlScraper.ARMedBoardCurl import ARMedBoard
from CurlScraper.DCHealthCurl import DCHealth
from SeleniumScraper.ARMedBoardSel import ARMedboardSeleniumScraper
import json


def get_ar_med_dataset():
    ar_med_sel = ARMedboardSeleniumScraper()
    ar_med_sel.get_all_licenses("PA")
    print("")


def scrape_armedboard(method="c"):
    license_num = "PA-130"

    if method == "c":
        ar_med_curl = ARMedBoard(cookies_dict=None)
        license_info = ar_med_curl.get_license_info(license_num)
        print(f"\n")
        print(json.dumps(license_info, indent=2))

    elif method == "s":
        ar_med_sel = ARMedboardSeleniumScraper()
        license_info2 = ar_med_sel.get_license_details(license_number=license_num)
        print(f"\n")
        print(json.dumps(license_info2, indent=2))


def scrape_dc_health(method="c"):
    license_num = "PT870062"
    if method == "c":
        dc_med_curl = DCHealth(cookies_dict=None)
        license_info = dc_med_curl.get_license_info(license_num)
        print(f"\n")
        print(json.dumps(license_info, indent=2))


if __name__ == "__main__":
    get_ar_med_dataset()
    # scrape_dc_health("c")
    # scrape_armedboard("c")
    print("Done")
