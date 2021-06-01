from CurlScraper.ARMedBoardCurl import ARMedBoard
from CurlScraper.DCHealthCurl import DCHealth
from CurlScraper.PALicensingCurl import PALS
from CurlScraper.ORMedBoardCurl import ORMedBoard
from SeleniumScraper.PALicensingSel import PALSSeleniumScraper
from SeleniumScraper.ARMedBoardSel import ARMedboardSeleniumScraper
from SeleniumScraper.ORMedBoardSel import ORMedSeleniumScraper
import json


def get_ar_med_dataset(method="c", license_type="PA"):
    """
    Ties a bunch of methods together to get the license details from ARMedBoard
    :param method:
    :return:
    """
    # Need to use selenium and browser to do a search to get all the ASMB Ids
    # After getting Ids, can use either curl or selenium again to get the license details
    ar_med_sel = ARMedboardSeleniumScraper()
    asmb_id_list = ar_med_sel.get_all_license_ids(license_type)
    print(f"INFO: Found {len(asmb_id_list)} licenses of the specified type. Proceeding to get details")
    license_details_list = []

    for license_num in asmb_id_list:
        if method == "c":
            ar_med_curl = ARMedBoard(cookies_dict=None)
            license_info = ar_med_curl.get_license_info(license_num)
            print(f"\n")
            print(json.dumps(license_info, indent=2))

        else:
            ar_med_sel = ARMedboardSeleniumScraper()
            license_info = ar_med_sel.get_license_details(license_number=license_num)
            print(f"\n")
            print(json.dumps(license_info, indent=2))

        license_details_list.append(license_info)

    print("\n")
    print(json.dumps(license_details_list, indent=2))


def get_dchealth_dataset(method="c", license_type="PHYSICAL THERAPIST"):
    """
    Gets dataset of all licenses of supplied type from the site
    :param method: 
    :param license_type: 
    :return: 
    """
    if method == "c":
        dc_med_curl = DCHealth(cookies_dict=None)
        license_details_list = dc_med_curl.get_all_licenses(license_type)
        print(json.dumps(license_details_list, indent=2))


def get_pals_dataset(method="c", board_or_commission="State Board of Pharmacy", license_type="Pharmacist", ):
    """
    Gets dataset of all licenses of supplied type from the site
    :param method:
    :param license_type: license type
    :param board_or_commission: board that license type belongs to
    :return:
    """
    # The license type and board.commission values are supplied
    # These need to be converted to the corresponding codes/Ids
    # This will be done from the browser
    pals_sel = PALSSeleniumScraper()
    info_id = pals_sel.get_board_and_licence_type_codes(board_or_commission=board_or_commission, license_type=license_type)
    professionID = info_id.get("professionID")
    licenseTypeId = info_id.get("licenseTypeId")

    if method == "c":
        pals_curl = PALS(cookies_dict=None)
        license_details_list = pals_curl.get_all_license_details_for_type(professionID=professionID, licenseTypeId=licenseTypeId)
        print(json.dumps(license_details_list, indent=2))


def get_or_med_data_set(method="c", license_type="Podiatrist"):
    """
    Gets dataset of all licenses of type supplied from the site
    :param method:
    :param license_type:
    :return:
    """
    or_med_sel = ORMedSeleniumScraper()
    asmb_id_list = or_med_sel.get_all_license_ids(license_type)
    print(f"INFO: Found {len(asmb_id_list)} licenses of the specified type. Proceeding to get details")
    license_details_list = []

    for license_id in asmb_id_list:
        or_med_curl = ORMedBoard(cookies_dict=None)
        license_info = or_med_curl.get_license_info(license_id)
        print(f"\n")
        print(json.dumps(license_info, indent=2))

        license_details_list.append(license_info)


def scrape_armedboard(method="c", license_num="PA-130"):
    """
    Get details for a single license supplied from AR MED Board
    :param method:
    :param license_num:
    :return:
    """
    if method == "c":
        ar_med_curl = ARMedBoard(cookies_dict=None)
        license_info = ar_med_curl.get_license_info(license_num)
        print(f"\n")
        print(json.dumps(license_info, indent=2))

    elif method == "s":
        ar_med_sel = ARMedboardSeleniumScraper()
        license_info2 = ar_med_sel.get_license_details(license_number=license_num)
        print(f"\n")
        print(json.dumps(license_info2, indent=2))


def scrape_dc_health(method="c", license_num="PT870062"):
    """
    Gets details for a single license from the DC Health site
    :param method:
    :param license_num:
    :return:
    """
    if method == "c":
        dc_med_curl = DCHealth(cookies_dict=None)
        license_info = dc_med_curl.get_license_info(license_num)
        print(f"\n")
        print(json.dumps(license_info, indent=2))


if __name__ == "__main__":
    get_or_med_data_set()
    # get_pals_dataset()
    # get_dchealth_dataset()
    # get_ar_med_dataset()

    # scrape_dc_health("c")
    # scrape_armedboard("c")
    print("Done")
