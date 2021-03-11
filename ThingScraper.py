from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import general_config as gconf
import personal_config as pconf
import os
import re
import datetime
import math
import time


# region General manipulation functions

def to_field_format(name) :
    """
    Converts given name into lowercase str and replaces whitespaces with an underscore.
    """
    return name.lower().replace(' ', '_')


def get_parent(element) :
    """
    Returns the parent selenium element of given element.
    """

    return element.find_element_by_xpath('..')


def identifier_from_url(url, regex, group_n=1) :
    """
    Generates an identifier from given url based on regex expression.
    :param url: the url from which to extract the identifier.
    :param regex: regex expression to user to extract identifier. (must contain at least 1 group)
    :param group_n: which group from the regex expression to return (Default = 1)
    :return: str of identifier extracted.
    """
    return re.search(regex, url).group(group_n)


# endregion

# region Web pages classes
# region Parent class
class ScrapedData :
    def __init__(self, url=None, browser=None, properties=None) :
        self.url = url
        self.browser = browser
        self._elements = dict()
        self.properties = dict() if properties is None else properties

    def __getitem__(self, item) :
        """
        Implementation of special function to allow retrieving an object parameter by using squared brackets.
      :param item: key for the requested object property.
      :return: object property.
        """
        return self.properties.get(item)

    def __setitem__(self, key, value) :
        """
        Implementation of special function to allow setting an object parameter by using squared brackets.
      :param key: key for requested object property
      :param value: the value to set for the property
        """
        self.properties[key] = value

    def __add__(self, other) :
        """
        Implementation of special function to allow appending parameters to an object by using '+' sign.
        Appended object must be of type dict.
      :param other: dictionary with keys as properties.
      :return: self
        """

        # verify given parameter to be of type dict
        if isinstance(other, dict) :
            self.properties.update(other)
        else :
            raise TypeError(f"Can only add dictionary, not {type(other)}.")
        return self

    def __str__(self) :
        """
        Implementation of special function to allow str casting of object instance.
      :return: object's url
        """
        return self.url

    def __repr__(self) :
        """
        Implementation of special function to allow representation of an object instance.
      :return: object type and url
        """
        return str(type(self).__name__) + ":" + self.url

    def print_info(self) :
        """
        Prints full information about the object instance.
        """
        output = [self.url]
        for key in self.properties :
            output.append(f"\t{key} = {self.properties[key]}")
        print("\n".join(output))

    def keys(self) :
        """
        Returns all property names held for the thing instance.
        """
        return tuple(self.properties.keys())

    def set_browser(self, browser) :
        """
        Set instance's browser. given 'browser' must of of Browser type.
        """
        if not isinstance(browser, Browser) :
            raise ValueError(f"Parameter 'browser' must be of Browser type and not {type(browser)}.")

        self.browser = browser

    def open_url(self) :
        """
        In case the current url in the opened browser is not refering for the object's url, open it.
        """

        # If the object instance has not browser defined, raise an error
        if not self.browser :
            raise NameError("Object has no browser defined. See '.browser' attribute or '.set_browser()' method.")
        elif self.url is None :
            raise NameError("Object has no URL defined. See '.url' attribute.")
        # if a browser is defined, check the opened url and match it for the thing's url
        elif self.browser.opened_url() != self.url :
            self.browser.get(self.url)

    def clear_elements(self) :
        self._elements.clear()


# endregion

# region child classes
class User(ScrapedData) :
    """
    Hold all relevant information and methods to handle that information for a single user.
    Attributes:
        url         - string. Holds the url for the user's page. Constructed from username.
        properties  - dictionary. Described below.

    Possible properties:
        username    - string
        followers   - number of followers the user has
        following   - number people the user is following
        designs     - number of 'things' the user has posted, remixes included
        collections - number of collection the user has created
        makes       - number of makes (prints of things) the user has posted
        likes       - number of things the user liked
        skill_level - string, one of 3: Novice, Intermidate or Expert
        titles      - list, professional titles a user chose to add to his profile.
    """

    def __init__(self, username=None, **kwargs) :
        """
        Construction of new User instance.
            :param username: user's username. Can be None if 'url' argument is provided.
            :param kwargs: arguments to be passed to ScrapedData object. Recommended to pass 'url' if username is not given
            and 'browser' for browser object to be used for the instance.
        """

        # in case a username is not provided, look up for 'url' argument or
        # 'properties' attribute with a username key.
        if username is None :
            if 'url' in kwargs :
                username = identifier_from_url(url=kwargs['url'],
                                               regex=gconf.UserSettings.USERNAME_REGEX)
                del kwargs['url']
            elif 'properties' in kwargs and 'username' in kwargs['properties'] :
                username = kwargs['properties']['username']

            # if neither provided, raise an error.
            else :
                raise ValueError(
                    "'url', 'username' or properties (dictionary with 'username' key) must be provided in order to create User instance.")

        # format a url based on found username (for normalized appearance)
        url = gconf.UserSettings.BASE_URL.format(username)

        # construction of parent object with url
        super().__init__(url=url, **kwargs)

        # adding found username to instance's properties
        self.properties['username'] = username

    # region Single fetch methods
    def _fetch_action_item(self, name) :
        """
        Fetch action item (left panel) element by given name.
            :param name: followers, following or designs
        """

        # raise error if invalid action item name was given
        if name.lower() not in gconf.UserSettings.PROFILE_ACTION_POSSIBLE_LABELS :
            raise ValueError(f'Name must be followers, following or designs. Given name: {name}')

        # by finding the label of the action item, get the parent html tag as an element
        label_element = self.browser.find_text('span', gconf.UserSettings.PROFILE_ACTION_LABEL, name.title())
        action_item = self.browser.find_parent(label_element)

        # from the parent tag, save the element that holds the action item count
        self._elements[to_field_format(name)] = action_item.find_element_by_class_name(
            gconf.UserSettings.PROFILE_ACTION_COUNT)

    def _fetch_tab_button(self, label) :
        """
        Fetch tab button element (top panel) by given label.
            :param label: favorites, designs, collections, makes or likes
        """

        # in case an invalid label name was given, raise an error
        if label not in gconf.UserSettings.TAB_POSSIBLE_LABELS :
            raise ValueError(
                f'Label must be one of {",".join(gconf.UserSettings.TAB_POSSIBLE_LABELS)}. Given label: {label}')

        # by finding the label of the tab button, get the parent html tag as an element
        label_element = self.browser.find_text('div', gconf.UserSettings.TAB_TITLE, label.title())
        tab_button = self.browser.find_parent(label_element)

        # from the parent tag, save the element that holds the tab button metric
        self._elements[to_field_format(label)] = tab_button.find_element_by_class_name(gconf.UserSettings.TAB_METRIC)

    def _fetch_title(self) :
        """
        Fetch the user's self declared titles.
        """
        self._elements['title'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.UserSettings.ABOUT_WIDGET_TITLE)

    def _fetch_skill(self) :
        """
        Fetch the user's self evaluated skill level.
        """
        self._elements['skill'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.UserSettings.ABOUT_WIDGET_SKILL)

    # endregion

    # region Single parse methods
    def _parse_action_item(self, name) :
        """
        Parse action item (left panel) element by given name.
            :param name: followers, following or designs
        """

        # raise error if invalid action item name was given
        if name.lower() not in gconf.UserSettings.PROFILE_ACTION_POSSIBLE_LABELS :
            raise ValueError(f'Name must be followers, following or designs. Given name: {name}')

        try :
            # convert action item name to field
            name = to_field_format(name)

            # convert found count as int if numeric and add it to properties, add None if not numeric
            found_count = self._elements[name].text
            self[name] = int(found_count) if found_count.strip().isnumeric() else None
        except :
            self[name] = None

    def _parse_tab_button(self, label) :
        """
        Parse tab button element (top panel) by given label.
            :param label: favorites, designs, collections, makes or likes
        """

        # in case an invalid label name was given, raise an error
        if label not in gconf.UserSettings.TAB_POSSIBLE_LABELS :
            raise ValueError(
                f'Label must be one of {",".join(gconf.UserSettings.TAB_POSSIBLE_LABELS)}. Given label: {label}')

        try :
            # convert label to field
            label = to_field_format(label)

            # convert found count as int if numeric and add it to properties, add None if not numeric
            found_count = self._elements[label].text
            self[label] = int(found_count) if found_count.strip().isnumeric() else None
        except :
            self[label] = None

    def _parse_title(self) :
        """
        Parse the user's self declared titles.
        """
        try :
            self['titles'] = self._elements["title"].text.lower().split('\n')
        except :
            self['titles'] = None

    def _parse_skill(self) :
        """
        Parse the user's self evaluated skill level.
        """
        try :
            self['skill_level'] = self._elements['skill'].text.lower()
        except :
            self['skill_level'] = None

    # endregion

    def fetch_all(self) :
        """
        Breaks down the users's url into elements (tags and classes) holding properties.
        """
        # open url
        self.open_url()

        # action items
        for name in gconf.UserSettings.PROFILE_ACTION_POSSIBLE_LABELS :
            self._fetch_action_item(name)

        # tab buttons
        for label in gconf.UserSettings.TAB_POSSIBLE_LABELS :
            self._fetch_tab_button(label)

        # titles
        self._fetch_title()

        # skill level
        self._fetch_skill()

    def parse_all(self, clear_cache=True) :
        """Obtain information from elements previously fetched for the user.

               Parameters:
                clear_cache (bool): Clear previously fetched elements from memory after parsing. (Default: True)
        """

        if not self._elements :
            raise RuntimeError("Elements must be fetched first before being parsed. Use .fetch_all.")

        # Action items
        for item in gconf.UserSettings.PROFILE_ACTION_POSSIBLE_LABELS :
            self._parse_action_item(item)

        # Tab buttons
        for label in gconf.UserSettings.TAB_POSSIBLE_LABELS :
            self._parse_tab_button(label)

        # titles
        self._parse_title()

        # skill level
        self._parse_skill()

        if clear_cache :
            self.clear_elements()

    # region In development (not useable)
    def _obtain_designs(self, design_limit=None) :

        # open web page, if not open
        self.open_url()

        # Handle missing number of designs
        if 'designs' not in self.keys() :
            self._fetch_tab_button('designs')
            self._parse_tab_button('designs')

        n_designs = self.properties['designs'] if design_limit is None else design_limit
        pages_to_scan = math.ceil(n_designs / gconf.THINGS_PER_PAGE)

        designs = []
        for i in range(pages_to_scan) :

            # wait and obtain all available designs elements
            page_designs = []
            while len(page_designs) < min(gconf.THINGS_PER_PAGE, n_designs) :
                page_designs = self.browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)

            # parse elements into list
            for design in page_designs :
                design_url = design.find_element_by_class_name(gconf.ExploreList.CARD_BODY).get_attribute("href")
                item_id = identifier_from_url(design_url, gconf.ThingSettings.ID_REGEX)
                likes = design.find_elements_by_class_name(gconf.ExploreList.THING_LIKES)[1].text
                thing = Thing(thing_id=item_id)
                thing['likes'] = int(likes)
                designs.append((item_id, thing))

        self.properties['designs_list'] = designs

    def _obtain_makes(self, make_limit=None) :

        # open web page, if not open
        self.browser.get(gconf.UserSettings.MAKES_URL.format(self.properties['username']))

        # Handle missing number of makes
        if 'makes' not in self.keys() :
            self._fetch_tab_button('makes')
            self._parse_tab_button('makes')

        n_makes = self.properties['makes'] if make_limit is None else make_limit
        pages_to_scan = math.ceil(n_makes / gconf.THINGS_PER_PAGE)

        makes = []
        for i in range(pages_to_scan) :
            # wait and obtain all available makes elements
            page_makes = []
            while len(page_makes) < min(gconf.THINGS_PER_PAGE, n_makes) :
                page_makes = self.browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)

            # parse elements into list
            for make in page_makes :
                make_url = make.find_element_by_class_name(gconf.ExploreList.CARD_BODY).get_attribute("href")
                item_id = identifier_from_url(make_url, gconf.MakeSettings.ID_REGEX)
                makes.append(item_id)

        self.properties['makes_list'] = makes
    # endregion


class Make(ScrapedData) :
    """
    Hold all relevant information and methods to handle that information for a single make.
    Attributes:
        url         - string. Holds the url for the make's page. Constructed from make id.
        properties  - dictionary. Described below.

    Possible properties:
        make_id         - string, make id as provided from thigiverse
        thingiverse_id  - string, if for the source thing from which the make was created
        username        - string, the creators username
        uploaded        - datetime, the date and time the make was uploaded in ISO8601
        comments        - int, number of comments for the make
        likes           - int, number of likes for the make
        views           - int, number of views for the make
        category        - int, string, the category the make was uploaded to
        print_settings  - dictionary, holds all print settings (if any) for the make
    """

    def __init__(self, make_id=None, **kwargs) :
        """
        Construction of new Make instance.
            :param make_id: make id as provided from thingiverse. Can be None if 'url' argument is provided.
            :param kwargs: arguments to be passed to ScrapedData object. Recommended to pass 'url' if make_id is not given
            and 'browser' for browser object to be used for the instance.
        """

        #  in case a make_id is not provided, look up for 'url' argument or
        # 'properties' attribute with a make_id key.
        if make_id is None :
            if 'url' in kwargs :
                make_id = identifier_from_url(url=kwargs['url'],
                                              regex=gconf.MakeSettings.ID_REGEX)
                del kwargs['url']
            elif 'properties' in kwargs and 'make_id' in kwargs['properties'] :
                make_id = kwargs['properties']['make_id']

            # if neither provided, raise an error.
            else :
                raise ValueError(
                    "'url', 'make_id' or properties (dictionary with 'make_id' key) must be provided in order to create Make instance.")

        # format a url based on found make_id (for normalized appearance)
        url = gconf.MakeSettings.BASE_URL.format(make_id)

        # construction of parent object with url
        super().__init__(url=url, **kwargs)

        # add make_id to instance's properties
        self['make_id'] = make_id

    # region Single fetch methods
    def _fetch_source(self) :
        """
        Fetches source thing.
        """
        self._elements['source'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.MakeSettings.SOURCE)

    def _fetch_creator(self) :
        """
        Fetches creator text line. Includes the upload date.        """
        self._elements['page_info'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.MakeSettings.PAGE_INFO)

    def _fetch_metric(self, title) :
        """
        Fetch a metric for the make by given metric title.
            :param title: the metric to be fetch. can be : like, comment or share
        """

        # search for metric element by given title
        search_path = gconf.MakeSettings.METRIC_ITEM_PATH.format(make_id=self.properties['make_id'],
                                                                 icon_title=title.title())

        # insert found metric to instance elements
        self._elements[title] = self.browser.driver.find_element_by_xpath(search_path)

    def _fetch_views_and_category(self) :
        """
        Fetch the elements of views and category.
        """
        make_info_element = self.browser.driver.find_element_by_xpath(gconf.MakeSettings.MAKE_INFO)
        make_info_element_parent = self.browser.find_parent(make_info_element)

        try:
            self._elements['views'] = make_info_element_parent.find_element_by_class_name(gconf.MakeSettings.VIEWS)
        except:
            self._elements['views'] = None

        # TODO: fix exception
        # selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":".icon-category"}
        try:
            self._elements['category'] = make_info_element_parent.find_element_by_class_name(gconf.MakeSettings.CATEGORY)
        except:
            self._elements['category'] = None

    def _fetch_print_settings(self) :
        """
        Fetch the print settings.
        """
        self._elements['print_settings'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.MakeSettings.INFO_CONTENT)

    # endregion

    def fetch_all(self) :
        """
        Open the make's url (if not already opened) and fetch elements.
        """
        self.open_url()

        self._fetch_source()
        self._fetch_creator()
        self._fetch_metric('like')
        self._fetch_metric('comments')
        self._fetch_metric('share')
        self._fetch_views_and_category()
        self._fetch_print_settings()

    # region Single parse methods
    def _parse_source(self) :
        """
        Parse source thing id as provided by thingiverse.
        :return:
        """
        self['thingiverse_id'] = identifier_from_url(self._elements['source'].get_attribute('href'),
                                                     gconf.ThingSettings.ID_REGEX)

    def _parse_creator_username(self) :
        self['username'] = self._elements['page_info'].find_element_by_tag_name(
            'span').find_element_by_tag_name('a').text

    def _parse_upload_time(self) :
        """
        Parse upload time as ISO8601 datetime into instance's properties.
        """
        upload_time = self._elements['page_info'].find_element_by_tag_name('span').find_element_by_tag_name(
            'time').get_attribute('datetime')
        self.properties['uploaded'] = datetime.datetime.strptime(upload_time, "%Y-%m-%d %H:%M:%S %Z").isoformat()

    def _parse_metric(self, name) :
        """
        Parse a metric for the make by given metric title (Converts metric into an integer).
            :param name: the metric to be fetch. can be : like, comment or share
        """
        metric = self._elements[name].text
        # convert metric to int if numeric, None if failed
        self[name] = int(metric) if metric.strip().isnumeric() else None

    def _parse_views(self) :
        """
        Parse views as int.
        """
        views = self._elements['views'].text.replace(" Views", "")
        # convert views to int if numeric, None if failed
        self['views'] = int(views) if views.strip().isnumeric() else None

    def _parse_category(self) :
        """
        Parse category.
        """
        try :
            self.properties['category'] = self._elements['category'].text.replace("Found in ", "").lower()
        except :
            self['category'] = None

    def _parse_print_settings(self) :
        """
        Parse print settings into a dictionary that holds all information.
        """
        try :
            # get whole text of print settings element
            content_line = self._elements["print_settings"].text

            # Define a lambda function to that returns group 1 based on regex pattern or None of pattern not found
            regex_result = (
                lambda regex : None if (re.search(regex, content_line)) is None else re.search(regex,
                                                                                               content_line).group(
                    1))

            print_settings = dict()

            # For each of the settings, find its value using regex
            # done manually due to difference in field names
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[0])] = regex_result(
                "Printer Brand:\\n(.*?)\\n")
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[1])] = regex_result(
                "Printer:\\n(.*?)\\n")
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[2])] = regex_result(
                "Rafts:\\n(.*?)\\n")
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[3])] = regex_result(
                "Supports:\\n(.*?)\\n")
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[4])] = regex_result(
                "Resolution:\\n(.*?)\\n")
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[5])] = regex_result(
                "Infill:\\n(.*?)\\n")
            print_settings[to_field_format(gconf.MakeSettings.POSSIBLE_PRINT_SETTINGS[6])] = regex_result(
                "Filament: (.*)")

            # add all settings to properties
            self['print_settings'] = print_settings
        except :
            self['print_settings'] = None

    # endregion

    def parse_all(self, clear_cache=True) :
        """
        Parse all properties for make instance.
            :param clear_cache: if true, elements attribute will be cleared upon parsing.
        """
        self._parse_source()
        self._parse_creator_username()
        self._parse_upload_time()
        self._parse_metric('like')
        self._parse_metric('comments')
        self._parse_metric('share')
        self._parse_views()
        self._parse_category()
        self._parse_print_settings()

        if clear_cache :
            self.clear_elements()


class Thing(ScrapedData) :
    """
    Holds all relevant information and methods to handle that information for a signle Thing (model).
    Attributes:
        url         - string. Holds the url for the make's page. Constructed from make id.
        properties  - dictionary. Described below.

    Possible properties:
        thing_id            - string, thing id as provided from thigiverse
        username            - string, creator's username
        model_name          - string, the title given for the model
        uploaded            - datetime, the date and time the make was uploaded in ISO8601
        files               - int, number of files for the thing
        comments            - int, number of comments the thing has
        makes               - int, number of makes the thing has
        likes               - int, number of likes the thing has
        tags                - list, string, all the given tags for the thing
        print_settings      - dictionary, holds all provided print settings (if any)
        license             - string, usage licenses provided by the user
        remix               - string, if the thing is a remix, includes the source thing id as provided from thingiverse
        category            - string, the category the thing was uploaded to
    """

    def __init__(self, thing_id=None, **kwargs) :
        """
        Construction of new Thing instance.
            :param thing_id: thing id as provided from thingiverse. Can be None if 'url' argument is provided.
            :param kwargs: arguments to be passed to ScrapedData object. Recommended to pass 'url' if thing_id is not given
            and 'browser' for browser object to be used for the instance.
        """
        #  in case a thing_id is not provided, look up for 'url' argument or
        # 'properties' attribute with a thing_id key.
        if thing_id is None :
            if 'url' in kwargs :
                thing_id = identifier_from_url(url=kwargs['url'],
                                               regex=gconf.ThingSettings.ID_REGEX)
                del kwargs['url']
            elif 'properties' in kwargs and 'thing_id' in kwargs['properties'] :
                thing_id = kwargs['properties']['thing_id']
            else :
                raise ValueError(
                    "'url', 'thing_id' or properties (dictionary with 'thing_id' key) must be provided in order to create Thing instance.")

        # format a url based on found thing_id (for normalized appearance)
        url = gconf.ThingSettings.BASE_URL.format(thing_id)

        # construction of parent object with url
        super().__init__(url=url, **kwargs)

        # add thing_id to instance's properties
        self['thing_id'] = thing_id

    # region Single fetch methods
    def _fetch_category(self) :
        category_box = get_parent(self.browser.wait_and_find(By.CLASS_NAME, gconf.ThingSettings.CATEGORY_SECTION))
        self._elements['category'] = category_box.find_element(By.CLASS_NAME, gconf.ThingSettings.CATEGORY_NAME)

    def _fetch_remix(self) :
        try :
            remix_box = self.browser.find_parent(by=By.CLASS_NAME, name=gconf.ThingSettings.REMIX_SECTION)
            self._elements['remix'] = remix_box.find_element(By.CLASS_NAME, gconf.ThingSettings.REMIX_CARD)
        except NoSuchElementException :
            self._elements['remix'] = None

    def _fetch_license(self) :
        self._elements['license'] = self.browser.driver.find_element_by_xpath(gconf.ThingSettings.LICENSE_PATH)

    def _fetch_print_settings(self) :
        # obtain print settings element
        # this is an optional information the creator can provide, so some models may not have this information.
        try :
            settings_header = self.browser.find_text(tag='div', class_name=gconf.ThingSettings.BLOCK_TITLE,
                                                     text='Print Settings')
            print_settings = self.browser.find_parent(settings_header)
            self._elements['print_settings'] = print_settings.find_elements_by_class_name(
                gconf.ThingSettings.PRINT_SETTING)
        except NoSuchElementException :
            self._elements['print_settings'] = None

    def _fetch_tags(self) :
        # obtain all tag elements into a list
        all_tags = self.browser.wait_and_find(By.CLASS_NAME, gconf.ThingSettings.TAG_LIST)
        try :
            self._elements['tags'] = [tag for tag in
                                      all_tags.find_elements_by_class_name(gconf.ThingSettings.TAG_SINGLE)]
        except NoSuchElementException :
            self._elements['tags'] = None

    def _fetch_tab_buttons(self) :
        # obtain tab buttons holding metric information: files, comments, makes and remixes
        all_metrics = self.browser.wait_and_find(By.CLASS_NAME, gconf.ThingSettings.TAB_BUTTON, find_all=True)
        self._elements['tab_buttons'] = {
            metric.find_element_by_class_name(gconf.ThingSettings.TAB_TITLE) : metric.find_element_by_class_name(
                gconf.ThingSettings.METRIC)
            for metric in all_metrics}

    def _fetch_created_by(self) :
        # obtain element holding both the creator name and the uploaded date
        self._elements['created_by'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.ThingSettings.CREATED_BY)

    def _fetch_model_name(self) :
        # obtain element holding the model (thing) name
        self._elements['model_name'] = self.browser.wait_and_find(By.CLASS_NAME, gconf.ThingSettings.MODEL_NAME)

    # endregion

    # region Single parse methods
    def _parse_category(self) :
        try :
            self.properties['category'] = self._elements['category'].text
        except :
            self['category'] = None

    def _parse_remix(self) :
        try :
            self.properties['remix'] = self._elements['remix'].get_attribute('href').split(sep=":")[-1]
        except :
            self.properties['remix'] = None

    def _parse_license(self) :
        try :
            self.properties['license'] = self._elements['license'].text
        except :
            self.properties['license'] = None

    def _parse_print_settings(self) :
        # add empty print settings to properties (as some models may not have any print settings information
        print_settings = {to_field_format(key) : None for key in gconf.ThingSettings.POSSIBLE_PRINT_SETTINGS}

        try :
            for setting in self._elements['print_settings'] :
                # using regex to obtain setting name and value into two groups
                regex_result = re.search(gconf.ThingSettings.FIND_SETTING_REGEX, setting.get_attribute('innerHTML'))

                if regex_result is not None :
                    provided_property = to_field_format(regex_result.group(1))
                    property_value = regex_result.group(2).lower()

                    if provided_property in print_settings.keys() :
                        print_settings[provided_property] = property_value
        except :
            pass
        finally :
            self['print_settings'] = print_settings

    def _parse_tags(self) :
        try :
            # Obtain text from each tag element add add them all as a list to properties
            self.properties['tags'] = [tag.text for tag in self._elements['tags']]
        except :
            self.properties['tags'] = None

    def _parse_metrics(self) :
        # set tab buttons to be ignore (hold not useful information)
        ignore_buttons = ('Thing Details', 'Apps')
        # for each tab button element, add it's name (converted using to_field_format function) and value to properties
        for key, value in self._elements['tab_buttons'].items() :
            if key.text not in ignore_buttons :
                # using tab button names as field names. lowering case and replacing spaces with underscore
                # cast metric as int
                self.properties[to_field_format(key.text)] = int(value.text)

    def _parse_upload_date(self) :
        # use created by html to obtain uploaded date text (uploaded date appears after a end tag)
        date_text = self._elements['created_by'].get_attribute('innerHTML').split(sep='</a> ')[1]
        # convert string date into actual date using datetime package. Date saved in epoch format.
        self.properties['uploaded'] = datetime.datetime.strptime(date_text, "%B %d, %Y").isoformat()

    def _parse_creator_username(self) :
        self.properties['username'] = self._elements['created_by'].find_element_by_tag_name('a').get_attribute(
            'text')

    def _parse_model_name(self) :
        self.properties['model_name'] = self._elements['model_name'].text

    # endregion

    def fetch_all(self, browser=None) :
        """
        Breaks down the thing's url into elements (tags and classes) holding properties.
      :param browser: Browser object the be used for accessing the thing's url.
        """

        # define instance's browser to preserve old usage
        if browser :
            self.browser = browser

        # open url
        self.open_url()

        self._fetch_model_name()

        self._fetch_created_by()

        self._fetch_tab_buttons()

        self._fetch_tags()

        self._fetch_print_settings()

        self._fetch_license()

        self._fetch_remix()

        self._fetch_category()

    def parse_all(self, clear_cache=True) :
        """Obtain information from elements previously fetched for the thing.

               Parameters:
                clear_cache (bool): Clear previously fetched elements from memory after parsing. (Default: True)
        """

        if not self._elements :
            raise RuntimeError("Elements must be fetched first before being parsed. Use Thing.fetch_all.")

        # model name
        self._parse_model_name()

        # get username found inside a tag text
        self._parse_creator_username()

        # upload time
        self._parse_upload_date()

        # Metric information
        self._parse_metrics()

        # Tags into list
        self._parse_tags()

        # Print settings
        self._parse_print_settings()

        # License
        self._parse_license()

        # Remix
        self._parse_remix()

        # Category
        self._parse_category()

        # Clearing cache
        if clear_cache :
            self.clear_elements()

    def get_makes(self, max_makes=pconf.MAX_MAKES_TO_SCAN) :
        """
        Get makes ids related with the thing.
            :param max_makes: the maximum number of makes to obtain.
            :return: a set holding make ids related to the thing instance.
        """
        # open web page,
        self.browser.get(gconf.ThingSettings.MAKES_URL.format(self.properties['thing_id']))

        # sleep for defined seconds to get javascript loaded
        time.sleep(pconf.IMPLICITLY_WAIT)

        # Handle missing number of makes
        if 'makes' not in self.keys() :
            self._fetch_tab_buttons()
            self._parse_metrics()

        # Determine the maximum number of makes to scan
        # (lowest between configuration max and real number of makes for thing)
        n_makes = min(self.properties['makes'], max_makes)

        thing_cards = []
        # while not all n_makes are found
        while len(thing_cards) < n_makes :
            # scroll down to the bottom of the page
            self.browser.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # get all found elements
            thing_cards = self.browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)

        # Construct make id list from thing card list
        makes_list = []
        for card in thing_cards[:n_makes] :
            make_url = card.find_element_by_class_name(gconf.ExploreList.CARD_BODY).get_attribute('href')
            make_id = identifier_from_url(make_url, gconf.MakeSettings.ID_REGEX)
            makes_list.append(make_id)

        return set(makes_list)

    def get_remixes(self, max_remixes=pconf.MAX_REMIXES_TO_SCAN) :
        """
        Get remixes related to the thing instance.
            :param max_remixes: maximum number of remixes to obtain.
            :return: a list of tuples with (thing_id, likes) for each remix.
        """
        # open web page,
        self.browser.get(gconf.ThingSettings.REMIXES_URL.format(self.properties['thing_id']))

        # sleep for defined seconds to get javascript loaded
        time.sleep(pconf.IMPLICITLY_WAIT)

        # Handle missing number of remixes
        if 'remixes' not in self.keys() :
            self._fetch_tab_buttons()
            self._parse_metrics()

        # Determine the maximum number of remixes to scan
        # (lowest between configuration max and real number)
        n_remixes = min(self.properties['remixes'], max_remixes)

        thing_cards = []
        # while not all n_remixes are found
        while len(thing_cards) < n_remixes :
            # scroll down to the bottom of the page
            self.browser.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # get all found elements
            thing_cards = self.browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)

        # Construct thing list that holds thing_id and number of likes per remix
        thing_list = []
        for card in thing_cards[:n_remixes] :
            thing_url = card.find_element_by_class_name(gconf.ExploreList.CARD_BODY).get_attribute('href')
            thing_likes = card.find_elements_by_class_name(gconf.ExploreList.THING_LIKES)[1].text

            thing_id = identifier_from_url(thing_url, gconf.ThingSettings.ID_REGEX)
            thing_likes_int = int(thing_likes) if thing_likes.strip().isnumeric() else 0

            thing_list.append((thing_id, thing_likes_int))

        return thing_list


# endregion
# endregion

# Browser managing class
class Browser :
    """
    Browser class manages the browser to be opened and it's driver.
    Once an instance is created, WebDriver methods and attributes can be passed to the 'Browser.driver' attribute.
    Additional methods like get(url) and close can be directly applied to the Browser instance.
    """

    # Dictionary that defines browsers and their relevant webdriver class
    available_browsers = {'chrome' : webdriver.Chrome, 'firefox' : webdriver.Firefox, 'iexplorer' : webdriver.Ie,
                          'safari' : webdriver.Safari}

    def __init__(self, name, path) :
        """Construction of a new browser instance

               Parameters:
                name (string): browser's name. can only be one of the available browsers. More info: Browsers.available_browsers.keys()
                path (string): the path (either relative or absolute) to the browser of choice webdriver.
        """
        self.name = name
        self.driver_path = os.path.abspath(path)

        if self.name in Browser.available_browsers :
            self.driver = Browser.available_browsers[name](self.driver_path)
        else :
            raise ValueError(
                f"Requested browser '{name}' not available. Usable browsers:\n {list(Browser.available_browsers.keys())}")

        # minimise the opened browser
        # self.driver.minimize_window()

    def __enter__(self) :
        """
        Allows to open browser connection using 'with' statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) :
        """
        Allows to close browser connection using 'with' statment
        """
        self.close()

    def get(self, url) :
        """
        Equivalent to Browser.driver.get method
        """

        self.driver.get(url)

    def close(self) :
        """
        Equivalent to Browser.driver.close method
        """
        self.driver.close()

    def opened_url(self) :
        """
        Returns the currently opened url.
        """
        return self.driver.current_url

    def wait(self, by, name, timeout=pconf.WAIT_TIMEOUT, regex=False, find_all=False) :
        """
        Wait for specific element to be present in browser.
            Parameters:
                by (selenium.webdriver.common.by): html tag attribute to search for
                name (str): the 'by' value to search for
                timeout (int): time limit in seconds to wait for find values 'by' and 'name' to appear on page. Defualt: get_wait_timout on personal_config.py
                regex (bool): if true, regex search patterns are enabled for 'name'.
                find_all (bool): if true, wait for all elements of search criteria to be found.
        """
        # change the search name to re.compile of regex is enabled
        if regex :
            name = re.compile(name)

        # wait for given element to be available. raise error if timeout has been reached.
        WebDriverWait(self.driver, timeout).until(
            ec.presence_of_all_elements_located((by, name)) if find_all else ec.presence_of_element_located((by, name))
        )

    def find(self, by, name, find_all=False) :
        """
        Find specific element in browser.
        Equivalent to Browser.driver.find_element / Browser.driver.find_elements

            Parameters:
                by (selenium.webdriver.common.by): html tag attribute to search for
                name (str): the 'by' value to search for
                find_all (bool): if true, returned value will be a list of all found elements. Default: False

            Returns:
                (webdriver.remote.webelement.WebElement): the found element(s)
        """
        # return found element(s) depends
        if find_all :
            return self.driver.find_elements(by, name)
        else :
            return self.driver.find_element(by, name)

    def wait_and_find(self, by, name, timeout=pconf.WAIT_TIMEOUT, find_all=False, regex=False) :
        """Wait for given element in the opened page on the browser and return the searched result.
           Combination of Browser.wait and Browser.find methods.
            Parameters:
                by (selenium.webdriver.common.by): html tag attribute to search for
                name (str): the 'by' value to search for
                timeout (int): time limit in seconds to wait for find values 'by' and 'name' to appear on page. Defualt: get_wait_timout on personal_config.py
                find_all (bool): if true, a list of all found elements is returned. Default: False.
                regex (bool): if true, regex search patterns are enabled for 'name'.
               Returns:
                (webdriver.remote.webelement.WebElement): the found element(s) or None if nothing was found.
        """
        try :
            self.wait(by, name, timeout, regex, find_all)
            return self.find(by, name, find_all)
        except TimeoutException :
            return None

    def find_parent(self, element=None, *args, **kwargs) :
        if element is None :
            element = self.find(*args, **kwargs)
        return element.find_element_by_xpath('..')

    def find_text(self, tag, class_name, text, wait=True) :
        if wait :
            self.wait(By.CLASS_NAME, class_name)

        return self.driver.find_element_by_xpath(f"//{tag}[contains(@class,'{class_name}') and text()='{text}']")