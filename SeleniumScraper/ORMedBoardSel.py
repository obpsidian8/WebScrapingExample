import re
import pickle
from SeleniumScraper.SeleniumPageNavigator import get_chrome_driver, SelemiumPageNavigetor


class ORMedSeleniumScraper:
    SITE_NAME = "ORMedBoard"
    MAIN_PAGE = "https://techmedweb.omb.state.or.us"
    DIRECTORY_SEARCH_PAGE = "https://techmedweb.omb.state.or.us/search"

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


    def get_all_license_ids(self, license_type, page_limit=None):
        """
        Gets all Entity Ids of a specified type from the page
        :param license_type:
        :return:
        """
        or_med_id_list = []
        self.navigator.get_page(url=self.DIRECTORY_SEARCH_PAGE)
        license_selector_xpath = "(//button[contains(@ng-click,'c.onFilter')])[1]"
        page_loaded = self.navigator.check_page_loaded(page_load_xpath=license_selector_xpath)
        if page_loaded:
            self.navigator.click_element(xpath=license_selector_xpath)

            filter_xpath = "(//alx-filter[contains(@on-filter,'c.toggleFilter()')])[1]"
            filter_loaded = self.navigator.check_page_loaded(page_load_xpath=filter_xpath)
            if filter_loaded:
                license_type_xpath = "(//*[contains(@ng-click,'c.togglePanel(item.value)') and contains(text(), 'License Type')])"
                self.navigator.click_element(xpath=license_type_xpath, pause_after_action=0.5)

                license_type_xpath = f"(//*[contains(@class,'filter-item') and contains(text(), '{license_type}')])"
                self.navigator.click_element(xpath=license_type_xpath)

                search_btn_xpath = "(//button[contains(@ng-click,'c.search()')])"
                self.navigator.click_element(xpath=search_btn_xpath)

                results_loaded_xpath = "(//alx-list[contains(@results,'c.data.searchResults')])"
                if results_loaded_xpath:
                    print(f"INFO: Results Loaded")
                    pages_visited = []
                    next_view = True

                    ormed_id_regex = re.compile(r'EntityID=(\d+)')

                    base_xpath_for_result = "(//a[contains(@href, '.aspx?EntityID')])"
                    xpath_for_page_nums = "(//li[contains(@ng-click, 'c.search(page.number)')]/a[@href])"

                    while next_view:
                        # Get all pages in current view
                        num_pages_current_view = self.navigator.get_number_of_elements(xpath=xpath_for_page_nums, time_delay=0.5)
                        for page in range(num_pages_current_view + 1):
                            xpath_current_page = f"{xpath_for_page_nums}[{page}]"
                            self.navigator.click_element(xpath=xpath_current_page)

                            num_results = self.navigator.get_number_of_elements(xpath=base_xpath_for_result, time_delay=0.5)

                            for idx in range(1, num_results + 1):
                                current_result_xpath = f"{base_xpath_for_result}[{idx}]"
                                ele = self.navigator.getElementAttributeAsText(xpath=current_result_xpath, attribute_name="href")
                                try:
                                    asmb_id = ormed_id_regex.search(ele).group(1)
                                    print(f"INFO: Found Entity Id: {asmb_id}")
                                    or_med_id_list.append(asmb_id)
                                except:
                                    print("ERROR: Could not get Entity Id from element")

                            print(f"INFO: Number of results found after scraping current page (page {page + 1}) {len(or_med_id_list)}")

                        # Click on next view
                        print(f"INFO: {len(or_med_id_list)} OR Med ids found so far after scraping all {or_med_id_list} pages in current view."
                              f"\n\t{or_med_id_list}. Going to next view (set of pages)")

                        next_view_xpath = "(//li[contains(@ng-click, 'c.increaseMaxPage()')])"

                        res_count_regex = re.compile('Showing.+?-.+?(\d+).+?of.+?(\d+)')
                        results_count_xpath = "(//span[contains(@ng-show, 'c.results')])"
                        results_count_text = self.navigator.get_element_text(xpath=results_count_xpath)
                        try:
                            current_count = int(res_count_regex.search(results_count_text).group(1))
                            print(f"INFO:Current count is {current_count}")
                            total_count = int(res_count_regex.search(results_count_text).group(2))
                            print(f"INFO: Total count is {total_count}")
                        except:
                            current_count = 1
                            total_count = 1

                        if total_count > current_count:
                            next_view = True
                        else:
                            next_view = False

                        if next_view:
                            self.navigator.click_element(xpath=next_view_xpath)
                            self.navigator.check_page_loaded(page_load_xpath=results_loaded_xpath)


        cookies_dict = self.navigator.get_curl_formatted_cookies_from_browser()
        self.save_cookie_to_disk(cookies_dict)

        return or_med_id_list
