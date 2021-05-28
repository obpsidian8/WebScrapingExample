import os
import re
import json
import pickle
from CurlScraper.CoreLibrary.PyCurlRequest import CurlRequests


class ARMedBoard:
    """
    Method for transferring data via curl to the AR Med Board site
    """
    SITE_NAME = "ARMedBoard"
    MAIN_PAGE = "http://www.armedicalboard.org/Default.aspx"
    LICENSE_SEARCH_URL = "http://www.armedicalboard.org/Public/verify/lookup.aspx?LicNum="

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

    def extract_json_from_site_response(self, response):
        """
        Extracts JSON from complete response information from server
        Use only when the response from the server is the response headers and JSON (Not when response is html with embedded JSON)
        :param response:
        :return:
        """
        print(f"\nINFO: EXTRACTING JSON FROM SITE RESPONSE")
        response = str(response)
        json_payload_regex = re.compile(r'({[\s\S]*?"\w+[\s\S]+)')
        try:
            json_response = json_payload_regex.search(response).group(1)
            json_response = json.loads(json_response)
            print(f"INFO: JSON response found")
        except Exception as e:
            json_response = {}
            print(f"ERROR: Could not get JSON response. DETAILS: {e}")
        print(json.dumps(json_response, indent=2))

        return json_response

    def extract_embeded_json_from_html(self, response, tag_id_name):
        """
        Used to extract json embeded in script tags in html
        :param response:
        :return:
        """
        print(f"\nINFO: EXTRACTING JSON ENCLOSED WITHIN ID TAG {tag_id_name}")
        info_json_regex = re.compile(fr'<script\s+id="{tag_id_name}".+?type="application/json">([\s\S]*?)</script>')
        try:
            info_json = info_json_regex.search(str(response)).group(1)
            info_json = info_json.replace('\\"', '')
            info_json = info_json.replace('\\', '')
            info_json = json.loads(info_json)
            print(f"\nINFO: JSON found for {tag_id_name}")
        except Exception as e:
            print(f"ERROR: Could not extract info JSON. DETAILS {e}")
            info_json = {}

        return info_json

    def get_site_request_headers(self):
        """
        Defines and returns curl_headers for AR Med requests.
        :return: dictionary of curl_headers
        """

        headers_dict = {
            "Connection": "keep-alive",
            # "sec-ch-ua": "'Google Chrome';v='88', 'Not;A Brand';v='99', 'Chromium';v='88'",
            "Cache-Control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "referer": "http://www.armedicalboard.org/public/verify/default.aspx",
            "accept-language": "en-US,en;q=0.9"
        }
        return headers_dict

    def get_license_page(self, license_page_url, curl_proxy=None):
        """
        Gets details license page as html response
        :return:
        """
        print(f"\nINFO: GETTING LICENSE PAGE FROM SERVER")
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy


        headers_dict = self.get_site_request_headers()

        requester = CurlRequests(self.cookies_dict, headers_dict=headers_dict)
        response = requester.send_curl_request(license_page_url, proxy=proxy, page_redirects=True)

        return response

    def get_license_info(self, license_number, curl_proxy=None):
        """
        Gets the page response and then gets the item json from page response
        :param license_number:
        :param curl_proxy:
        :return:
        """
        print(f"\nINFO: GETTING ITEM INFO")
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        license_page_url = f"{self.LICENSE_SEARCH_URL}{license_number}"

        license_info = {}

        page_html_response = self.get_license_page(license_page_url, proxy)
        page_html_response = page_html_response.get('response', str(page_html_response))
