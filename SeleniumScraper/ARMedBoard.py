import re
from SeleniumScraper.SeleniumPageNavigator import get_chrome_driver, SelemiumPageNavigetor


class ARMedboardSeleniumScraper:
    SITE_NAME = "ARMedBoard"
    MAIN_PAGE = "http://www.armedicalboard.org/Default.aspx"
    LICENSE_SEARCH_URL = "http://www.armedicalboard.org/Public/verify/lookup.aspx?LicNum="

    def __init__(self):
        self.driver = get_chrome_driver(dataDirName=self.SITE_NAME)
        self.navigator = SelemiumPageNavigetor(self.driver)

    def get_page(self, license_number):
        """
        Gets the page for scraping
        """
        license_page_url = f"{self.LICENSE_SEARCH_URL}{license_number}"
        self.navigator.get_page(url=license_page_url)

    def scrape_page(self, license_number):
        """
        Scrapes the page using xpath
        """
        self.get_page(license_number)
        license_info = {}

        page_source = self.navigator.get_page_source()
        field_names_regex = re.compile(r'<li>(.+?):\s*<span\s+id="ctl00_MainContentPlaceHolder_lvResults')
        field_list = field_names_regex.findall(page_source)

        group_index = None

        for field in field_list:
            results = self.xpath_builder(field, license_number, group_index)
            field_value = results[0]
            group_index = results[1]
            license_info[field] = field_value

        return license_info

    def xpath_builder(self, field_name, license_number, group_index):
        """
        Builds the xpath for the field names
        """
        value = None
        xpath_string_original = f"(//li[contains(text(),'{field_name}')]/span)"
        num_elements = self.navigator.get_number_of_elements(xpath=xpath_string_original, time_delay=0.0005)
        if num_elements == 1:
            value = self.navigator.get_element_text(xpath=xpath_string_original, time_delay=1)
        elif num_elements == 0:
            value = None
        else:
            if group_index:
                xpath_string_group = f"{xpath_string_original}[{group_index}]"
                value = self.navigator.get_element_text(xpath=xpath_string_group)
            else:
                for idx in range(1, num_elements + 1):
                    xpath_string_group = f"{xpath_string_original}[{idx}]"
                    value = self.navigator.get_element_text(xpath=xpath_string_group)
                    if field_name == "License Number" and value == license_number:
                        group_index = idx

        return value, group_index
