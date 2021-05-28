from CurlScraper.ARMedBoardCurl import ARMedBoard
import json

def scrape_armedboard():
    ar_med_curl = ARMedBoard(cookies_dict=None)

    license_num = "PA-100"

    license_info = ar_med_curl.get_license_info(license_num)
    print(json.dumps(license_info, indent=2))

if __name__ == "__main__":
    scrape_armedboard()
