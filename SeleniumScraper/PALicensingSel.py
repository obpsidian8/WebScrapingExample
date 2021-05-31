import re
import pickle
from SeleniumScraper.SeleniumPageNavigator import get_chrome_driver, SelemiumPageNavigetor


class PALSSeleniumScraper:
    SITE_NAME = "PALicensingSystem"
    MAIN_PAGE = "https://www.pals.pa.gov/#/page/default"
    LICENSE_SEARCH_URL = "https://www.pals.pa.gov/#/page/search"

    def __init__(self):
        self.driver = get_chrome_driver(dataDirName=self.SITE_NAME)
        self.navigator = SelemiumPageNavigetor(self.driver)
        self.username = self.SITE_NAME

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

    def get_board_and_licence_type_codes(self, board_or_commission, license_type):
        """
        Gets from the search page the corresponding codes for the board and license type supplied
        :param board_or_commission:
        :param license_type:
        :return:
        """
        professionID = None
        licenseTypeID = None
        info_id = {}

        self.navigator.get_page(self.LICENSE_SEARCH_URL)

        form_xpath = "(//form[contains(@name, 'SerachFilter')])"
        form_page_load = self.navigator.check_page_loaded(page_load_xpath=form_xpath)

        if form_page_load:
            profession_type_dropdown_xpath = "(//select[contains(@name, 'ProfessionType')])"
            self.navigator.click_element(xpath=profession_type_dropdown_xpath)

            profession_selector_xpath = f"(//option[text()='{board_or_commission}'])"
            self.navigator.click_element(xpath=profession_selector_xpath)
            professionID_value = self.navigator.getElementAttributeAsText(xpath=profession_selector_xpath, attribute_name="value")

            value_regex = re.compile(r'number:(\d+)')
            try:
                professionID = value_regex.search(professionID_value).group(1)
                print(f"INFO: Profession Id found for {board_or_commission}: {professionID}")
            except Exception as e:
                print(f"ERROR: Could not get profession id for {board_or_commission}. DETAILS: {e}")

            license_type_dropdown_xpath = "(//select[contains(@name, 'LicenseType')])"
            license_type_selector_xpath = f"(//option[text()='{license_type}'])"

            # Check if the license type dropdown values have been set first before clicking on the dropdown
            license_select_page_load = self.navigator.check_page_loaded(page_load_xpath=license_type_selector_xpath)
            if license_select_page_load:
                self.navigator.click_element(xpath=license_type_dropdown_xpath)
                self.navigator.click_element(xpath=license_type_selector_xpath)
                licenseTypeId_value = self.navigator.getElementAttributeAsText(xpath=license_type_selector_xpath, attribute_name="value")

                try:
                    licenseTypeID = value_regex.search(licenseTypeId_value).group(1)
                    print(f"INFO: License type Id found for {license_type}: {licenseTypeID}")
                except Exception as e:
                    print(f"ERROR: License type Id for {license_type}. DETAILS: {e}")

        info_id["professionID"] = professionID
        info_id["licenseTypeID"] = licenseTypeID

        cookies_dict = self.navigator.get_curl_formatted_cookies_from_browser()
        self.save_cookie_to_disk(cookies_dict)

        self.navigator.driver.close()
        self.navigator.driver.quit()
        return info_id
