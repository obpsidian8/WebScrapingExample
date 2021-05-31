import os
import re
import json
import pickle
from CurlScraper.CoreLibrary.PyCurlRequest import CurlRequests


class PALS:
    """
    Method for transferring data via curl to the AR Med Board site
    """
    SITE_NAME = "PALicensingSystem"
    MAIN_PAGE = "https://www.pals.pa.gov/"
    BULK_LICENSE_SEARCH_URL = "https://www.pals.pa.gov/api/Search/SearchForPersonOrFacilty"
    LICENSE_DETAILS_URL = "https://www.pals.pa.gov/api/SearchLoggedIn/GetPersonOrFacilityDetails"

    def __init__(self, cookies_dict=None, curl_proxy=None):
        if not cookies_dict:
            self.cookies_dict = {}
        else:
            self.cookies_dict = cookies_dict
        self.curl_proxy = curl_proxy  # http://IPADDRESS:PORTNUMBER
        self.username = self.SITE_NAME

        self.set_cookies_dict()

    def load_cookie_from_disk(self):
        """
        Loads cookies from disk if available, for sending requests
        :return:
        """
        print(f"INFO: LOADING COOKIE FROM DISK")
        cookie = None
        if os.path.exists(f'{self.username}.cookie'):
            print(f"\nINFO: Cookie present on disk! Loading into program.")
            with open(f'{self.username}.cookie', 'rb') as cookie_store:
                cookie = pickle.load(cookie_store)
                if cookie:
                    print("INFO: Cookie loaded from disk")
                    self.cookies_dict = cookie

        return cookie

    def save_cookie_to_disk(self, cookies_dict):
        """
        Saves cookie  file to disk. To be used for sending tracking requests
        :param cookies_dict:
        :return:
        """
        print(f"\nINFO: SAVING COOKIES TO DISK")
        with open(f'{self.username}.cookie', 'wb') as cookie_store:
            pickle.dump(cookies_dict, cookie_store)
            print("INFO: Cookie saved")

    def set_cookies_dict(self, curl_proxy=None):
        """
        Check if cookies are stored on local machine before trying to get a new one
        :return:
        """
        print(f"\nINFO: SETTING COOKIES FOR SESSION")
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        if self.cookies_dict:
            print(f"INFO: Cookies passed in to init. Will merge with ones from disk or new ones from site")

        cookie_dict_from_disk = self.load_cookie_from_disk()
        if cookie_dict_from_disk:
            # Merge cookies from disk to the ones passed
            print(f"INFO: Merging cookies from disk to new cookies")
            cookie_dict_from_disk.update(self.cookies_dict)
            self.cookies_dict = cookie_dict_from_disk
            print(f"\nINFO: Cookies found from disk + merge with passed in ones\n\t{json.dumps(self.cookies_dict, indent=2)}")

        # This process will get cookies from site and add in the new values to the self.cookies dict from init (which may be empty or contain some key-value pairs)
        headers_dict = self._get_site_request_headers()
        curl = CurlRequests(cookies_dict=self.cookies_dict, headers_dict=headers_dict)
        response = curl.send_curl_request(request_url=self.MAIN_PAGE, page_redirects=True, include=True, proxy=proxy)
        self.add_cookies_from_site_response(response)

        return

    def add_cookies_from_site_response(self, response):
        """
        Take a response from a request and saves any cookies received
        :param response:
        :return:
        """
        print(f"\nINFO: ADDING COOKIES FROM SITE RESPONSE")
        cookie_regex = re.compile(r'Set-Cookie:\s(.*?=.*?);', flags=re.IGNORECASE)
        cookies_list = cookie_regex.findall(str(response))

        print(f"INFO: Found cookies to add {cookies_list}")

        cookie_dict_regex = re.compile(r'(.*?)=(.*)')
        for cookie in cookies_list:
            try:
                name = cookie_dict_regex.search(cookie).group(1).strip()
                print(f"INFO: Found cookie: {name}")
            except:
                print(f"ERROR Extracting cookie name")
                name = None

            try:
                value = cookie_dict_regex.search(cookie).group(2).strip()
                print(f"INFO: Found value of cookie {name}: {value}")
            except:
                print(f"ERROR Extracting cookie value")
                value = None

            if name not in self.cookies_dict.keys():
                self.cookies_dict[name] = value

        print(f"\nINFO: Cookies found from site response+ merge with passed in ones\n\t{json.dumps(self.cookies_dict, indent=2)}")
        self.save_cookie_to_disk(self.cookies_dict)

    def _get_site_request_headers(self):
        """
        Defines and returns curl_headers for requests.
        :return: dictionary of curl_headers
        """

        headers_dict = {
            "Connection": "keep-alive",
            "sec-ch-ua": "'Google Chrome';v='88', 'Not;A Brand';v='99', 'Chromium';v='88'",
            "accept": "application/json, text/plain, */*",
            "Request-Id": "|ZnU+M.6jXyf",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.pals.pa.gov",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "referer": "https://www.pals.pa.gov",
            "accept-language": "en-US,en;q=0.9"
        }
        return headers_dict

    def _request_body_data_for_group_requests(self, professionID, licenseTypeId):
        """
        Forms the data portion of the request for getting license info
        :param professionID: Obtained from the "Board/Commission" drp down of the search page
        :param licenseTypeId: Ontained from the "License Type drop down of the search page. This field are only populated after the first drop down is selected"
        :return:
        """
        data = f'\'{{"OptPersonFacility":"Person","ProfessionID":{professionID},"LicenseTypeId":{licenseTypeId},"State":"","Country":"ALL","County":null,"IsFacility":0,"PersonId":null,"PageNo":1}}\''
        return data

    def _data_for_single_license_details(self, personId, licenseNumber, licenseId):
        """
        Gets the data portion of the request for geetting license info
        :param personId:
        :param licenseNumber:
        :param licenseId:
        :return:
        """
        data = f'\'{{"PersonId":"{personId}","LicenseNumber":"{licenseNumber}","IsFacility":"0","LicenseId":"{licenseId}"}}\''
        return data

    def _get_all_licenses_summaries(self, professionID, licenseTypeId, curl_proxy=None):
        """
        Gets all licenses of a specified type from the page
        :param license_type:
        :return:
        """
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        headers_dict = self._get_site_request_headers()

        requester = CurlRequests(self.cookies_dict, headers_dict=headers_dict)
        data = self._request_body_data_for_group_requests(professionID, licenseTypeId)

        licenses_list = requester.send_curl_request(request_url=self.BULK_LICENSE_SEARCH_URL, proxy=proxy, form_data=data, specified_method='POST', shell_needed=True)
        # Returns a list of JSON entries representing each licensed person
        # The responses here don't have all the details, so have to us another method to get the details
        # Each entry has three attributes that are used to get the details (PersonId, LicenseNumber, LicenseId)

        return licenses_list

    def get_all_license_details_for_type(self, professionID, licenseTypeId, curl_proxy=None):
        """
        Returns a list of the license details
        Glue that ties get_all_licenses_summaries and get_license_details together
        First, use methond to get all the license details summary based on the supplied paramaters
        2nd get the details of each one and append to the license_details_list
        :param professionID:
        :param licenseTypeId:
        :param curl_proxy:
        :return:license_details_list: List of detials
        """
        license_details_list = []
        licenses_summaries_list = self._get_all_licenses_summaries(professionID, licenseTypeId, curl_proxy)
        for license_summary in licenses_summaries_list:
            licenseNumber = license_summary.get("LicenseNumber")
            licenseId = license_summary.get("LicenseId")
            personId = license_summary.get("PersonId")

            license_detail = self._get_license_details(personId, licenseNumber, licenseId, curl_proxy)
            license_details_list.append(license_detail)

        return license_details_list

    def _get_license_details(self, personId, licenseNumber, licenseId, curl_proxy=None):
        """
        Get the license details of a particular license
        :param PersonId:
        :param LicenseNumber:
        :param LicenseId:
        :return:
        """
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        headers_dict = self._get_site_request_headers()

        requester = CurlRequests(self.cookies_dict, headers_dict=headers_dict)
        data = self._data_for_single_license_details(personId, licenseNumber, licenseId)
        license_details = requester.send_curl_request(request_url=self.LICENSE_DETAILS_URL, proxy=proxy, form_data=data, specified_method="POST")

        return license_details
