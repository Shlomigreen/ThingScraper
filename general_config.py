# General settings
MAIN_URL = "https://www.thingiverse.com/"  # Url of the main domain
THINGS_PER_PAGE = 20  # Number of things found in each explore page
PAGES_TO_SCAN = 30  # Default value for number of pages to scan
PLACE_HOLDER = '%%'


class ThingSettings :
    BASE_URL = f"https://www.thingiverse.com/thing:{PLACE_HOLDER}"

    # Classes
    MODEL_NAME = "ThingPage__modelName--3CMsV"
    CREATED_BY = "ThingPage__createdBy--1fVAy"
    TAB_BUTTON = "MetricButton__tabButton--2rvo1"
    TAB_TITLE = "MetricButton__tabTitle--2Xau7"
    METRIC = "MetricButton__metric--FqxBi"
    TAG_LIST = "Tags__widgetBody--19Uop"
    TAG_SINGLE = "Tags__tag--2Rr15"
    PRINT_SETTINGS = "ThingPage__preHistory--312bi"
    PRINT_SETTING = "ThingPage__description--14TtH"
    REMIX_SECTION = "RemixedFromSection__title--1Wb7x"
    REMIX_CARD = "ThingCardBody__cardBodyWrapper--ba5pu"
    CATEGORY_SECTION = "ThingsMoreSection__showMoreHeading--u2OAR"
    CATEGORY_NAME = "ThingsMoreSection__categoryName--3RWut"

    # HTML paths
    LICENSE_PATH = r"//a[@class='License__link--NFT8l' and not(@class='License__creator--4riPo')]"


class ExploreList:
    THING_CARD = "ThingCard__thingCard--1IcHY"
    CARD_BODY = "ThingCardBody__cardBodyWrapper--ba5pu"
    THING_LIKES = "CardActionItem__textWrapper--2wTM-"


class UserSettings:
    BASE_URL = f"https://www.thingiverse.com/{PLACE_HOLDER}/designs"
    USERNAME_REGEX = r"thingiverse.com/(.*)/"  # Regex string to search for username out of url. Group 1 is taken from this.


class MakeSettings:
    BASE_URL = f"https://www.thingiverse.com/make:{PLACE_HOLDER}"
    ID_REGEX = r"make:(\d*)"
