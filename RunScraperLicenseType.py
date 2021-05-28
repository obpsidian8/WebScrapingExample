from CurlScraper.ARMedBoardCurl import ARMedBoard


def scrape_armedboard():
    ar_med_curl = ARMedBoard(cookies_dict=None)

    license_num = "PA-340"

    ar_med_curl.get_license_info(license_num)


if __name__ == "__main__":
    scrape_armedboard()
