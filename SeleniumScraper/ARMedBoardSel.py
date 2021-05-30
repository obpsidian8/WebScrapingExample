import re
from SeleniumScraper.SeleniumPageNavigator import get_chrome_driver, SelemiumPageNavigetor


class ARMedboardSeleniumScraper:
    SITE_NAME = "ARMedBoard"
    MAIN_PAGE = "http://www.armedicalboard.org/Default.aspx"
    LICENSE_SEARCH_URL = "http://www.armedicalboard.org/Public/verify/lookup.aspx?LicNum="
    ASMB_ID_SEARCH_URL = "http://www.armedicalboard.org/Public/verify/results.aspx?strPHIDNO="
    DIRECTORY_SEARCH_PAGE = "http://www.armedicalboard.org/public/directory/AdvancedDirectorySearch.aspx"

    def __init__(self):
        self.driver = get_chrome_driver(dataDirName=self.SITE_NAME)
        self.navigator = SelemiumPageNavigetor(self.driver)

    def get_license_details(self, license_number):
        """
        Scrapes the page using xpath
        """

        if "ASMB" in license_number:
            license_page_url = f"{self.ASMB_ID_SEARCH_URL}{license_number}"
        else:
            license_page_url = f"{self.LICENSE_SEARCH_URL}{license_number}"

        self.navigator.get_page(url=license_page_url)

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

        license_info["Board Minutes"] = self.navigator.get_element_text(xpath="//span[contains(@id, 'ctl00_MainContentPlaceHolder_lblBoardMin')]")
        license_info["Board Orders"] = self.navigator.get_element_text(xpath="//span[contains(@id, 'ctl00_MainContentPlaceHolder_lblBoardAction')]")

        self.driver.close()
        self.driver.quit()
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

    def get_all_licenses(self, license_type, page_limit=None):
        """
        Gets all ASMB Ids of a specified type from the page
        :param license_type:
        :return:
        """
        license_type_xpath = f"//option[@value='{license_type}']"
        search_button_xpath = "(//input[contains(@name,'DirSearch') and @value='Search'])"

        self.navigator.get_page(url=self.DIRECTORY_SEARCH_PAGE)
        self.navigator.check_page_loaded(page_load_xpath="(//h2[contains(text(),'Advanced Directory Search')])")
        self.navigator.click_element(xpath=license_type_xpath)  # Click on the license type

        # Check if search button is loaded
        self.navigator.check_page_loaded(page_load_xpath=search_button_xpath)
        self.navigator.click_element(xpath=search_button_xpath)  # Click on the search button, after verifying that its loaded.

        results_loaded_xpath = "(//table[contains(@id, 'ctl00_MainContentPlaceHolder_gvLookup')])"
        self.navigator.check_page_loaded(page_load_xpath=results_loaded_xpath)

        # Start navigating through the pages

        next_view = True
        current_view = 1
        asmb_id_regex = re.compile(r'PHIDNO=(ASMB\d+)')
        asmb_id_list = []

        base_xpath_for_result = "(//a[contains(@href, '.aspx?PHIDNO')])"
        xpath_for_page_nums = "( //a[contains(@href, 'ctl00$MainContentPlaceHolder$gvLookup') and not(contains(text(), '..'))])"  # Xpath for each page within the current view(when combined with [])

        while next_view:
            # Get all pages in current view
            numpages = self.navigator.get_number_of_elements(xpath=xpath_for_page_nums, time_delay=0.5)
            for page in range(numpages + 1):
                xpath_current_page = f"{xpath_for_page_nums}[{page}]"
                self.navigator.click_element(xpath=xpath_current_page)
                self.navigator.check_page_loaded(page_load_xpath=results_loaded_xpath)
                # Find number of results in current page
                num_results = self.navigator.get_number_of_elements(xpath=base_xpath_for_result, time_delay=0.5)
                for idx in range(1, num_results + 1):
                    current_result_xpath = f"{base_xpath_for_result}[{idx}]"
                    ele = self.navigator.getElementAttributeAsText(xpath=current_result_xpath, attribute_name="href")
                    try:
                        asmb_id = asmb_id_regex.search(ele).group(1)
                        print(f"INFO: Found ASMB Id: {asmb_id}")
                        asmb_id_list.append(asmb_id)
                    except:
                        print("ERROR: Could not get ASMB Id from element")

                print(f"INFO: Number of results found after scraping current page (page {page + 1}) {len(asmb_id_list)}")

            # Click on next view
            print(f"INFO: {len(asmb_id_list)} ASMB ids found so far after scraping all {numpages} pages in current view."
                  f"\n\t{asmb_id_list}. Going to next view (set of pages)")

            next_view_xpath_base = "(//a[contains(@href, 'ctl00$MainContentPlaceHolder$gvLookup') and contains(text(), '...')])"
            num_view_buttons = self.navigator.get_number_of_elements(xpath=next_view_xpath_base)

            if current_view == 1:
                next_view_xpath = f"{next_view_xpath_base}[{1}]"
                # THis condition is met only on the first set of pages. There is only one next view button to click here

            else:
                next_view_xpath = f"{next_view_xpath_base}[{2}]"
                # This condition is met on all views other than the first one

            next_view = self.navigator.find_presence_of_element(xpath=next_view_xpath)  # True or False
            if next_view:
                self.navigator.click_element(xpath=next_view_xpath)
                self.navigator.check_page_loaded(page_load_xpath=results_loaded_xpath)

            current_view = current_view + 1


        self.driver.close()
        self.driver.quit()
        return asmb_id_list
