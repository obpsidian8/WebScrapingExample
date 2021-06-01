import os
import re
import json
import pickle
from CurlScraper.CoreLibrary.PyCurlRequest import CurlRequests


class ORMedBoard:
    """
    Method for transferring data via curl to the AR Med Board site
    """
    SITE_NAME = "ORMedBoard"
    MAIN_PAGE = "https://techmedweb.omb.state.or.us"
    LICENSE_SEARCH_URL = "https://techmedweb.omb.state.or.us/Clients/ORMB/Public/VerificationDetails.aspx?EntityID="

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

    def get_site_request_headers(self):
        """
        Defines and returns curl_headers for AR Med requests.
        :return: dictionary of curl_headers
        """

        headers_dict = {
            "authority": "techmedweb.omb.state.or.us",
            "sec-ch-ua": "'Google Chrome';v='88', 'Not;A Brand';v='99', 'Chromium';v='88'",
            "sec-ch-ua-mobile": "?0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "sec-fetch-user": "?1",
            "Sec-Fetch-Dest": "document",
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
        Gets the page response and then gets the license json from page response
        :param license_number:
        :param curl_proxy:
        :return:
        """

        # Do check to see if license number supplied is an actual license number or an ASMB id
        # Determine query url based on that
        license_page_url = f"{self.LICENSE_SEARCH_URL}{license_number}"

        print(f"\nINFO: GETTING LICENSE INFO")
        if curl_proxy:
            proxy = curl_proxy
        else:
            proxy = self.curl_proxy

        license_info = {}

        page_html_response = self.get_license_page(license_page_url, proxy)
        page_html_response = page_html_response.get('response', str(page_html_response))

        field_names_regex = re.compile(r'<span\s+id="ctl00_ContentPlaceHolder1_(.+?)\W>')
        field_list = field_names_regex.findall(page_html_response)
        group_index = 0

        for field in field_list:
            field_value = self.info_regex_builder(field, page_html_response, license_number)

            field=field.replace("dtgLicense_ctl02_lbl", "")
            field=field.replace("dtgEducation_ctl02_", "")
            field=field.replace("lbl", "")
            license_info[field] = field_value

        address_group_regex = re.compile(r'id="ctl00_ContentPlaceHolder1_VerificationAddress"[\s\S]*?</tr><tr>\s+<td>([\s\S]*?)</table>')
        addresses_regex = re.compile(r'tr>\s+<td>([\s\S]*?)</td>\s+</tr>')

        try:
            address_group = address_group_regex.search(page_html_response).group(1)
        except:
            print(f"ERROR: Could not extract address_group using this regex")
            address_group = None

        if address_group:
            addresses = addresses_regex.findall(page_html_response)
            for idx, address in enumerate(addresses, 1):
                field = f"Address{idx}"
                address = address.strip()
                address = address.replace("</td>", "")
                address = address.replace("<td>", "")
                address = address.replace("  ", "")
                address = address.replace("\n", " ")
                license_info[field] = address

        try:
            license_info.__delitem__("dtgLicense_ctl02_ObjectPK\" class=\"hidden")
        except:
            pass

        return license_info

    def info_regex_builder(self, field_name, page_html_response, license_number):
        """
        Builds the regex expression for getting the license data
        """
        base_license_info_regex_str = fr'<span\s+id="ctl00_ContentPlaceHolder1_{field_name}\W>(.+?)<'
        regex_compiled = re.compile(base_license_info_regex_str)
        try:
            field_value_list = regex_compiled.findall(page_html_response)
            value = field_value_list[0]
        except:
            print(f"ERROR: Could not extract field value of {field_name} from page source")
            value = None

        if value:
            if "/span" in value:
                value = None

        return value