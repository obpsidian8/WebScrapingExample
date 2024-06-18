import os
import re
import json
import pickle
from urllib.parse import quote_plus
from CurlScraper.CoreLibrary.PyCurlRequest import CurlRequests
from LoggingModule import set_logging

logger = set_logging()

class DCHealth:
    """
    Method for transferring data via curl to the DC health site
    """
    SITE_NAME = "DCHealth"
    MAIN_PAGE = "https://doh.force.com/ver/s/"
    LICENSE_SEARCH_URL = "https://doh.force.com/ver/s/sfsites/aura?r=5&other.SearchComponent.searchRecords=1&other.SearchComponent.searchRecordsCount=1"
    DIRECTORY_SEARCH_PAGE = "https://doh.force.com/ver/s/sfsites/aura?r=1&other.SearchComponent.searchRemainingRecords=1"

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
        logger.info(f"INFO: LOADING COOKIE FROM DISK")
        cookie = None
        if os.path.exists(f'{self.username}.cookie'):
            logger.info(f"\nINFO: Cookie present on disk! Loading into program.")
            with open(f'{self.username}.cookie', 'rb') as cookie_store:
                cookie = pickle.load(cookie_store)
                if cookie:
                    logger.info("INFO: Cookie loaded from disk")
                    self.cookies_dict = cookie

        return cookie

    def save_cookie_to_disk(self, cookies_dict):
        """
        Saves cookie  file to disk. To be used for sending tracking requests
        :param cookies_dict:
        :return:
        """
        logger.info(f"\nINFO: SAVING COOKIES TO DISK")
        with open(f'{self.username}.cookie', 'wb') as cookie_store:
            pickle.dump(cookies_dict, cookie_store)
            logger.info("INFO: Cookie saved")

    def set_cookies_dict(self, curl_proxy=None):
        """
        Check if cookies are stored on local machine before trying to get a new one
        :return:
        """
        logger.info(f"\nINFO: SETTING COOKIES FOR SESSION")
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        if self.cookies_dict:
            logger.info(f"INFO: Cookies passed in to init. Will merge with ones from disk or new ones from site")

        cookie_dict_from_disk = self.load_cookie_from_disk()
        if cookie_dict_from_disk:
            # Merge cookies from disk to the ones passed
            logger.info(f"INFO: Merging cookies from disk to new cookies")
            cookie_dict_from_disk.update(self.cookies_dict)
            self.cookies_dict = cookie_dict_from_disk
            logger.info(f"\nINFO: Cookies found from disk + merge with passed in ones\n\t{json.dumps(self.cookies_dict, indent=2)}")

        # This process will get cookies from site and add in the new values to the self.cookies dict from init (which may be empty or contain some key-value pairs)
        headers_dict = self.get_site_request_headers()
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
        logger.info(f"\nINFO: ADDING COOKIES FROM SITE RESPONSE")
        cookie_regex = re.compile(r'Set-Cookie:\s(.*?=.*?);', flags=re.IGNORECASE)
        cookies_list = cookie_regex.findall(str(response))

        logger.info(f"INFO: Found cookies to add {cookies_list}")

        cookie_dict_regex = re.compile(r'(.*?)=(.*)')
        for cookie in cookies_list:
            try:
                name = cookie_dict_regex.search(cookie).group(1).strip()
                logger.info(f"INFO: Found cookie: {name}")
            except:
                logger.info(f"ERROR Extracting cookie name")
                name = None

            try:
                value = cookie_dict_regex.search(cookie).group(2).strip()
                logger.info(f"INFO: Found value of cookie {name}: {value}")
            except:
                logger.info(f"ERROR Extracting cookie value")
                value = None

            if name not in self.cookies_dict.keys():
                self.cookies_dict[name] = value

        logger.info(f"\nINFO: Cookies found from site response+ merge with passed in ones\n\t{json.dumps(self.cookies_dict, indent=2)}")
        self.save_cookie_to_disk(self.cookies_dict)

    def get_site_request_headers(self):
        """
        Defines and returns curl_headers for DC Health requests.
        :return: dictionary of curl_headers
        """

        headers_dict = {
            "Connection": "keep-alive",
            "sec-ch-ua": "'Google Chrome';v='88', 'Not;A Brand';v='99', 'Chromium';v='88'",
            "sec-ch-ua-mobile": "?0",
            "X-SFDC-Page-Scope-Id": "d60d7bee-0377-4642-8c07-526a71a8f78d",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "X-SFDC-Request-Id": "13477278000046d01d",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "accept": "*/*",
            "Origin": "https://doh.force.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "referer": "https://doh.force.com/ver/s/",
            "accept-language": "en-US,en;q=0.9"
        }
        return headers_dict

    def get_license_info(self, license_number, curl_proxy=None):
        """
        Gets details license for license specified
        :return:
        """
        license_info = {}

        logger.info(f"\nINFO: GETTING LICENSE PAGE FROM SERVER")
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        headers_dict = self.get_site_request_headers()
        data = self.get_request_data(license_number)

        requester = CurlRequests(self.cookies_dict, headers_dict=headers_dict)
        response = requester.send_curl_request(self.LICENSE_SEARCH_URL, proxy=proxy, page_redirects=True, form_data=data)

        actions = response.get("actions")
        if actions:
            if len(actions) > 0:
                user_info = actions[1]
                state = user_info.get("state")
                logger.info(f"INFO: Request state: {state}")
                if state == "ERROR":
                    errors = user_info.get("error")
                    if len(errors) > 0:
                        error = errors[0]
                        logger.info(f"ERROR: Request did not complete. DETAILS: {error}")
                        return license_info

                returnValue = user_info.get("returnValue")
                if len(returnValue) > 0:
                    for key, value in returnValue[0].items():
                        key = key.replace("__c", "")
                        license_info[key] = value

        return license_info

    def get_request_data(self, license_number):
        """
        Forms the url encoded request data needed for the request
        :param license_number:
        :return:
        """
        data = f"message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22138%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2FSearchComponentController%2FACTION%24searchRecordsCount%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3ASearchComponent%22%2C%22params%22%3A%7B%22Profession%22%3A%220%22%2C%22LicenseType%22%3A%220%22%2C%22FirstName%22%3A%22%22%2C%22LastName%22%3A%22%22%2C%22LicenseNumber%22%3A%22{license_number}%22%2C%22SSN%22%3A%22%22%2C%22Status%22%3A%220%22%7D%7D%2C%7B%22id%22%3A%22139%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2FSearchComponentController%2FACTION%24searchRecords%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3ASearchComponent%22%2C%22params%22%3A%7B%22Profession%22%3A%220%22%2C%22LicenseType%22%3A%220%22%2C%22FirstName%22%3A%22%22%2C%22LastName%22%3A%22%22%2C%22LicenseNumber%22%3A%22{license_number}%22%2C%22SSN%22%3A%22%22%2C%22Status%22%3A%220%22%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22Q8onN6EmJyGRC51_NSPc2A%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%22zaAlQavgK5QD4CF76KJj6A%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fver%2Fs%2F&aura.token=undefined"
        return data

    def get_search_data(self, license_type, offsetCnt):
        """
        Forms data portion of request for querying all records in the website
        :param license_type:
        :param offsetCnt:
        :return:
        """
        license_type = quote_plus(license_type)
        data = f'message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22187%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2FSearchComponentController%2FACTION%24searchRemainingRecords%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3APageCount%22%2C%22params%22%3A%7B%22Profession%22%3A%220%22%2C%22LicenseType%22%3A%22{license_type}%22%2C%22FirstName%22%3A%22%22%2C%22LastName%22%3A%22%22%2C%22LicenseNumber%22%3A%22%22%2C%22SSN%22%3A%22%22%2C%22Status%22%3A%220%22%2C%22offsetCnt%22%3A%22{offsetCnt}%22%7D%2C%22version%22%3Anull%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22Q8onN6EmJyGRC51_NSPc2A%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%22zaAlQavgK5QD4CF76KJj6A%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fver%2Fs%2F&aura.token=undefined'
        return data

    def get_all_licenses(self, license_type, curl_proxy=None, page_limit=None):
        """
        Gets all the licenses available on the site
        :param license_type:
        :param page_limit:
        :return:
        """
        licenses_list = []
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        headers_dict = self.get_site_request_headers()

        error_state = False

        offsetCnt = 0
        while error_state is False:
            requester = CurlRequests(self.cookies_dict, headers_dict=headers_dict)
            data = self.get_search_data(license_type, offsetCnt)

            response = requester.send_curl_request(self.DIRECTORY_SEARCH_PAGE, proxy=proxy, page_redirects=True, form_data=data)
            actions = response.get("actions")
            if actions:
                if len(actions) > 0:
                    user_info = actions[0]
                    state = user_info.get("state")
                    logger.info(f"INFO: Request state: {state}")
                    if state == "ERROR":
                        errors = user_info.get("error")
                        if len(errors) > 0:
                            error = errors[0]
                            logger.info(f"ERROR: Request did not complete. DETAILS: {error}")
                            error_state = True
                    else:
                        logger.info(f"INFO: STATE: {state}")  # Success state
                        returnValue = user_info.get("returnValue")  # List of the results of the query
                        if len(returnValue) > 0:
                            # Iterate through all the return values on this case
                            for record in returnValue:
                                # Cleaning up the records before adding to the main list
                                license_info = {}
                                for key, value in record.items():
                                    key = key.replace("__c", "")
                                    license_info[key] = value
                                licenses_list.append(license_info)
                                logger.info(json.dumps(license_info, indent=2))

            logger.info(f"INFO: Number of results found after scraping current offset ({offsetCnt}) {len(licenses_list)}")
            offsetCnt = offsetCnt + 25

        logger.info(f"\nINFO: Total number of results {offsetCnt}")
        return licenses_list
