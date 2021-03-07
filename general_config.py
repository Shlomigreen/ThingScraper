# General settings
MAIN_URL = "https://www.thingiverse.com/"  # Url of the main domain
THINGS_PER_PAGE = 20  # Number of things found in each explore page
PAGES_TO_SCAN = 30  # Default value for number of pages to scan
PLACE_HOLDER = '%%'


class ExploreList :
    THING_CARD = "ThingCard__thingCard--1IcHY"
    CARD_BODY = "ThingCardBody__cardBodyWrapper--ba5pu"
    THING_LIKES = "CardActionItem__textWrapper--2wTM-"


class UserSettings :
    # Urls
    BASE_URL = f"https://www.thingiverse.com/{PLACE_HOLDER}/designs"

    # Regex
    USERNAME_REGEX = r"thingiverse.com/(.*)/"  # Regex string to search for username out of url. Group 1 is taken from this.

    # Classes
    PROFILE_ACTION_POSSIBLE_LABELS = ['followers', 'following', 'designs']
    PROFILE_ACTION_ITEM = "ProfileActionItem__container--1fTdX"
    PROFILE_ACTION_COUNT = "ProfileActionItem__count--1MaXx"
    PROFILE_ACTION_LABEL = "ProfileActionItem__label--2OlG9"

    TAB_POSSIBLE_LABELS = ['favorites', 'designs', 'collections', 'makes', 'likes']
    TAB_BUTTON = "MetricButton__tabButton--2rvo1"
    TAB_TITLE = "MetricButton__tabTitle--2Xau7"
    TAB_METRIC = "MetricButton__metric--FqxBi"

    ABOUT_WIDGET_TITLE = "UserAboutWidget__typesWrapper--1r1kj"
    ABOUT_WIDGET_SKILL = "UserAboutWidget__skillLevelWrapper--3eHjx"


class MakeSettings :
    BASE_URL = f"https://www.thingiverse.com/make:{PLACE_HOLDER}"
    ID_REGEX = r"make:(\d*)"

    POSSIBLE_PRINT_SETTINGS = ["Printer Brand",
                                "Printer Model",
                                "Rafts",
                                "Supports",
                                "Resolution",
                                "Infill",
                                "Filament"]


    # Classes
    SOURCE = "card-img-holder"
    PAGE_INFO = "item-page-info"  ## Made by <username>, uploaded <time>
    INFO_CONTENT = "thing-info-content"  ## Print settings section
    SINGLE_PRINT_SETTING = "detail-setting"

    # LIKES, COMMENTS and SHARES
    POSSIBLE_ICONS = ['like', 'comment', 'share']
    METRIC_ITEM_PATH = "//div[@class='item-list-interactions' and @data-make-id='{make_id}']//a[@title='{icon_title}']"

    # VIEWS AND CATEGORY
    MAKE_INFO = "//h2[@class='section-header']"
    VIEWS = 'icon-views'
    VIEWS_REGEX = r'(\d*) Views'
    CATEGORY = 'icon-category'
    CATEGORY_REGEX = r"Found in (.*)"


class ThingSettings :
    BASE_URL = f"https://www.thingiverse.com/thing:{PLACE_HOLDER}"
    ID_REGEX = r"thing:(\d*)"

    POSSIBLE_PRINT_SETTINGS = ["Printer Brand",
                                "Printer Model",
                                "Rafts",
                                "Supports",
                                "Resolution",
                                "Infill",
                                "Filament Brand",
                                "Filament Color",
                                "Filament Material"]

    # Classes
    MODEL_NAME = "ThingPage__modelName--3CMsV"
    CREATED_BY = "ThingPage__createdBy--1fVAy"
    TAB_BUTTON = "MetricButton__tabButton--2rvo1"
    TAB_TITLE = "MetricButton__tabTitle--2Xau7"
    METRIC = "MetricButton__metric--FqxBi"
    TAG_LIST = "Tags__widgetBody--19Uop"
    TAG_SINGLE = "Tags__tag--2Rr15"
    REMIX_SECTION = "RemixedFromSection__title--1Wb7x"
    REMIX_CARD = "ThingCardBody__cardBodyWrapper--ba5pu"
    CATEGORY_SECTION = "ThingsMoreSection__showMoreHeading--u2OAR"
    CATEGORY_NAME = "ThingsMoreSection__categoryName--3RWut"
    PRINT_SETTINGS = "ThingPage__preHistory--312bi"
    PRINT_SETTING = "ThingPage__description--14TtH"

    # HTML paths
    LICENSE_PATH = r"//a[@class='License__link--NFT8l' and not(@class='License__creator--4riPo')]"