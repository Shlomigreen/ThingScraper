# General settings
MAIN_URL = "https://www.thingiverse.com/"  # Url of the main domain
THINGS_PER_PAGE = 20  # Number of things found in each explore page


class ExploreList:
    THING_CARD = "ThingCard__thingCard--1IcHY"
    CARD_BODY = "ThingCardBody__cardBodyWrapper--ba5pu"
    THING_LIKES = "CardActionItem__textWrapper--2wTM-"


class UserSettings:
    class Elements:
        FOLLOWERS = 'followers'
        FOLLOWING = 'following'
        DESIGNS = 'designs'
        FAVORITES = 'favorites'
        COLLECTIONS = 'collections'
        MAKES = 'makes'
        LIKES = 'likes'
        TITLE = 'title'
        SKILL_LEVEL = 'skill'

    class Properties:
        USERNAME = 'username'
        FOLLOWERS = 'followers'
        FOLLOWING = 'following'
        DESIGNS = 'designs'
        FAVORITES = 'favorites'
        COLLECTIONS = 'collections'
        MAKES = 'makes'
        LIKES = 'likes'
        TITLES = 'titles'
        SKILL_LEVEL = 'skill_level'


    # Urls
    BASE_URL = "https://www.thingiverse.com/{}/designs"
    MAKES_URL = "https://www.thingiverse.com/{}/makes"

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


class MakeSettings():
    class Elements:
        SOURCE = 'source'
        PAGE_INFO = 'page_info'
        LIKES = 'like'
        COMMENTS = 'comments'  # as appear in thingiverse
        SHARES = 'share'  # as appear in thingiverse
        VIEWS = 'views'  # as appear in thingiverse
        CATEGORY = 'category'
        PRINT_SETTINGS = 'print_settings'

    class Properties:
        MAKE_ID = 'make_id'
        THING_ID = 'thingiverse_id'
        USERNAME = 'username'
        UPLOADED = 'uploaded'
        LIKES = 'like'  # must be the same as in elements
        COMMENTS = 'comments'   # must be the same as in elements
        SHARES = 'share'   # must be the same as in elements
        VIEWS = 'views'
        CATEGORY = 'category'
        PRINT_SETTINGS = 'print_settings'

    BASE_URL = "https://www.thingiverse.com/make:{}"
    ID_REGEX = r"make:(\d*)"

    # Code in ThingScraper is using indices of the following list, thus - ORDER MATTERS
    POSSIBLE_PRINT_SETTINGS = ["Printer Brand",
                               "Printer Model",
                               "Rafts",
                               "Supports",
                               "Resolution",
                               "Infill",
                               "Filament Brand"]

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


class ThingSettings:
    class Elements:
        MODEL_NAME = 'model_name'
        CREATOR = 'created_by'
        TABS = 'tab_buttons'
        TAGS = 'tags'
        PRINT_SETTINGS = 'print_settings'
        LICENSE = 'license'
        REMIX = 'remix'
        CATEGORY = 'category'

    class Properties:
        THING_ID = 'thing_id'
        MODEL_NAME = 'model_name'
        USERNAME = 'username'
        UPLOADED = 'uploaded'
        FILES = 'thing_files'
        COMMENTS = 'comments'   # as appear in thingiverse, lowercase
        MAKES = 'makes'   # as appear in thingiverse, lowercase
        REMIXES = 'remixes'  # as appear in thingiverse, lowercase
        TAGS = 'tags'
        LICENSE = 'license'
        REMIX = 'remix'
        CATEGORY = 'category'
        LIKES = 'likes'
        PRINT_SETTINGS = 'print_settings'

    BASE_URL = r"https://www.thingiverse.com/thing:{}"
    MAKES_URL = BASE_URL + r'/makes'
    REMIXES_URL = BASE_URL + r'/remixes'
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
    FIND_SETTING_REGEX = r"(.*):<div>(.*)</div>"

    # Classes
    CARD_TITLE = "ThingCardHeader__cardNameWrapper--3xgAZ"
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
    BLOCK_TITLE = "ThingPage__blockTitle--3ZdLu"

    # HTML paths
    LICENSE_PATH = r"//a[@class='License__link--NFT8l' and not(@class='License__creator--4riPo')]"


class Logger:
    FORMAT = '(%(asctime)s)  |  %(levelname)s  |  FILE:%(filename)s   FUNC:%(funcName)s   LINE:%(lineno)d :  %(' \
             'message)s '
    NAME = 'thingscraper'
    LOG_DIR = 'Log'


class Errors:
    DB_ERROR1 = "Could not find JSON file at given path"
    DB_ERROR2 = "Connection to mysql server failed"
    CONSTRUCTION_ERROR = "'url', '{0}' or `properties` (dictionary with '{0}' key) " \
                         "must be provided in order to create User instance."


class DB_builder:
    DB_NAME = 'thingiverse'
    SQL_CONSTRUCTION = "thingiverse.sql"
