from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException

import config as conf
import os
import re
import datetime
import webpage_elements as elm

# Url of the main domain
URL = "https://www.thingiverse.com/"


def to_field_format(name):
    """
    Converts given name into lowercase str and replaces whitespaces with an underscore.
    """
    return name.lower().replace(' ', '_')


def get_parent(element):
    """
    Returns the parent selenium element of given element.
    """

    return element.find_element_by_xpath('..')


class Thing:
    """
    Thing class is design to hold single thing page information.
    Once an instance is created by providing thing url, fetch_all(browser) function is need to be used in order to obtain
    all possible elements from the page.
    After fetching, parse_all() will generate a dictionary holding all information about the thing (model).
    Information can be accessed by using squared brackets on the thing instance.
    """

    def __init__(self, **kwargs):
        """
        Creating a new thing instance. Must provide either thing id or url as arguments.
        """
        # Validating construction arguments and adding them as instance arguments
        if kwargs.get('url') is not None:
            self.url = kwargs['url']
            self.thing_id = kwargs['url'].split(sep=":")[-1]
        elif kwargs.get('id') is not None:
            self.thing_id = kwargs['id']
            self.url = URL + "thing:" + kwargs['id']

        # in case no neither id or url were given, raise a value error.
        else:
            raise ValueError(
                "Construction arguments for thing object must include either an id, url or properties (as dictionary). Given arguments:", kwargs.keys())

        # Declaring empty dictionaries to hold page elements and properties (parsed elements)
        self._elements = dict()
        prop_value = kwargs.get('properties')
        self.properties = prop_value if prop_value is not None else dict()

    def __getitem__(self, item):
        """
        Implementation of special function to allow retrieving a thing parameter by using squared brackets.
       :param item: key for the requested thing property.
       :return: thing property.
        """
        return self.properties.get(item)

    def __setitem__(self, key, value):
        """
        Implementation of special function to allow setting a thing parameter by using squared brackets.
       :param key: key for requested thing property
       :param value: the value to set for the property
        """
        self.properties[key] = value

    def __add__(self, other):
        """
        Implementation of special function to allow appending parameters to a thing by using '+' sign.
        Appended object must be of type dict.
       :param other: dictionary with keys as properties.
       :return: self
        """

        # verify given parameter to be of type dict
        if isinstance(other, dict):
            self.properties.update(other)
        else:
            raise TypeError(f"Can only add dictionary, not {type(other)}.")
        return self

    def __str__(self):
        """
        Implementation of special function to allow str casting of thing instance.
       :return: thing's url
        """
        return self.url

    def __repr__(self):
        """
        Implementation of special function to allow representation of a thing instance.
       :return: thing's url
        """
        return self.url

    def print_info(self):
        """
        Prints full information about the thing instance.
        """
        output = [f"Thing number {self.thing_id}",
                  self.url]
        for key in self.properties:
            output.append(f"\t{key} = {self.properties[key]}")
        print("\n".join(output))

    def keys(self):
        """
        Returns all property names held for the thing instance.
        """
        return tuple(self.properties.keys())

    def _open_url(self, browser):
        browser.get(self.url)

    def fetch_all(self, browser):
        """
        Breaks down the thing's url into elements (tags and classes) holding properties.
       :param browser: Browser object the be used for accessing the thing's url.
        """
        # open thing url
        self._open_url(browser)

        self._fetch_model_name(browser)

        self._fetch_created_by(browser)

        self._fetch_tab_buttons(browser)

        self._fetch_tags(browser)

        self._fetch_print_settings(browser)

        self._fetch_license(browser)

        self._fetch_remix(browser)

        self._fetch_category(browser)

    def _fetch_category(self, browser) :
        category_box = get_parent(browser.wait_and_find(By.CLASS_NAME, elm.ThingClasses.CATEGORY_SECTION))
        self._elements['category'] = category_box.find_element(By.CLASS_NAME, elm.ThingClasses.CATEGORY_NAME)

    def _fetch_remix(self, browser) :
        # remix
        try :
            remix_box = browser.find_parent(By.CLASS_NAME, elm.ThingClasses.REMIX_SECTION)
            self._elements['remix'] = remix_box.find_element(By.CLASS_NAME, elm.ThingClasses.REMIX_CARD)
        except NoSuchElementException :
            self._elements['remix'] = None

    def _fetch_license(self, browser) :
        # Model License
        self._elements['license'] = browser.driver.find_element_by_xpath(elm.ThingClasses.LICENSE_PATH)

    def _fetch_print_settings(self, browser) :
        # obtain print settings element
        # this is an optional information the creator can provide, so some models may not have this information.
        try :
            print_settings = browser.wait_and_find(By.CLASS_NAME, elm.ThingClasses.PRINT_SETTINGS)
            self._elements['print_settings'] = print_settings.find_elements_by_class_name(
                elm.ThingClasses.PRINT_SETTING)
        except NoSuchElementException :
            self._elements['print_settings'] = None

    def _fetch_tags(self, browser) :
        # obtain all tag elements into a list
        all_tags = browser.wait_and_find(By.CLASS_NAME, elm.ThingClasses.TAG_LIST)
        try :
            self._elements['tags'] = [tag for tag in all_tags.find_elements_by_class_name(elm.ThingClasses.TAG_SINGLE)]
        except NoSuchElementException :
            self._elements['tags'] = None

    def _fetch_tab_buttons(self, browser) :
        # obtain tab buttons holding metric information: files, comments, makes and remixes
        all_metrics = browser.wait_and_find(By.CLASS_NAME, elm.ThingClasses.TAB_BUTTON, find_all=True)
        self._elements['tab_buttons'] = {
            metric.find_element_by_class_name(elm.ThingClasses.TAB_TITLE) : metric.find_element_by_class_name(
                elm.ThingClasses.METRIC)
            for metric in all_metrics}

    def _fetch_created_by(self, browser) :
        # obtain element holding both the creator name and the uploaded date
        self._elements['created_by'] = browser.wait_and_find(By.CLASS_NAME, elm.ThingClasses.CREATED_BY)

    def _fetch_model_name(self, browser) :
        # obtain element holding the model (thing) name
        self._elements['model_name'] = browser.wait_and_find(By.CLASS_NAME, elm.ThingClasses.MODEL_NAME)

    def parse_all(self, clear_cache=True):
        """Obtain information from elements previously fetched for the thing.

               Parameters:
                clear_cache (bool): Clear previously fetched elements from memory after parsing. (Default: True)
        """

        if not self._elements:
            raise RuntimeError("Elements must be fetched first before being parsed. See Thing.fetch_all.")

        # model name
        self._parse_model_name()

        # get username found inside a tag text
        self._parse_creator_username()
        # get username profile url provided as a tag href
        self._parse_creator_url()

        self._parse_upload_date()

        # Metric information
        self._parse_metrics()

        self._parse_tags()

        # print settings
        self._parse_print_settings()

        # license
        self._parse_license()

        # remix
        self._parse_remix()

        # category
        self._parse_category()

        # clearing cache
        if clear_cache:
            self._elements.clear()

    def _parse_category(self) :
        self.properties['category'] = self._elements['category'].text

    def _parse_remix(self) :
        if self._elements['remix'] is not None :
            self.properties['remix'] = self._elements['remix'].get_attribute('href').split(sep=":")[-1]
        else :
            self.properties['remix'] = None

    def _parse_license(self) :
        self.properties['license'] = self._elements['license'].text

    def _parse_print_settings(self) :
        # listing all possible fields for print settings provided by thingiverse
        possible_print_settings = ["Printer Brand",
                                   "Printer Model",
                                   "Rafts",
                                   "Supports",
                                   "Resolution",
                                   "Infill",
                                   "Filament Brand",
                                   "Filament Color",
                                   "Filament Material"]
        # add empty print settings to properties (as some models may not have any print settings information
        self.properties.update({to_field_format(key) : None for key in possible_print_settings})
        if self._elements['print_settings'] is not None :
            # define regex search patter to obtain setting and its value
            pattern = r"(.*):<div>(.*)</div>"
            for setting in self._elements['print_settings'] :
                # using regex to obtain setting name and value into two groups
                regex_result = re.search(pattern, setting.get_attribute('innerHTML'))

                if regex_result is not None :
                    # updating print settings (group 1 or regex results) with its value (group 2 of regex results) into the properties
                    self.properties.update({to_field_format(regex_result.group(1)) : regex_result.group(2)})

    def _parse_tags(self) :
        # Obtain text from each tag element add add them all as a list to properties
        self.properties['tags'] = [tag.text for tag in self._elements['tags']]

    def _parse_metrics(self) :
        # set tab buttons to be ignore (hold not useful information)
        ignore_buttons = ('Thing Details', 'Apps')
        # for each tab button element, add it's name (converted using to_field_format function) and value to properties
        for key, value in self._elements['tab_buttons'].items() :
            if key.text not in ignore_buttons :
                # using tab button names as field names. lowering case and replacing spaces with underscore
                # cast matric ast int
                self.properties[to_field_format(key.text)] = int(value.text)

    def _parse_upload_date(self) :
        # use created by html to obtain uploaded date text (uploaded date appears after a end tag)
        date_text = self._elements['created_by'].get_attribute('innerHTML').split(sep='</a> ')[1]
        # convert string date into actual date using datetime package. Date saved in epoch format.
        self.properties['upload_date'] = datetime.datetime.strptime(date_text, "%B %d, %Y").timestamp()

    def _parse_creator_url(self) :
        self.properties['creator_url'] = self._elements['created_by'].find_element_by_tag_name('a').get_attribute(
            'href')

    def _parse_creator_username(self) :
        self.properties['creator_username'] = self._elements['created_by'].find_element_by_tag_name('a').get_attribute(
            'text')

    def _parse_model_name(self) :
        self.properties['model_name'] = self._elements['model_name'].text

    def get_json(self):
        """
        Returns a single dictionary holding all information about the thing.
        """
        result = {'thing_id': self.thing_id, 'url': self.url}
        result.update(self.properties)
        return result


class Browser:
    """
    Browser class manages the browser to be opened and it's driver.
    Once an instance is created, WebDriver methods and attributes can be passed to the 'Browser.driver' attribute.
    Additional methods like get(url) and close can be directly applied to the Browser instance.
    """

    # Dictionary that defines browsers and their relevant webdriver class
    available_browsers = {'chrome': webdriver.Chrome, 'firefox': webdriver.Firefox, 'iexplorer': webdriver.Ie,
                          'safari': webdriver.Safari}

    def __init__(self, name, path):
        """Construction of a new browser instance

               Parameters:
                name (string): browser's name. can only be one of the available browsers. More info: Browsers.available_browsers.keys()
                path (string): the path (either relative or absolute) to the browser of choice webdriver.
        """
        self.name = name
        self.driver_path = os.path.abspath(path)

        if self.name in Browser.available_browsers:
            self.driver = Browser.available_browsers[name](self.driver_path)
        else:
            raise ValueError(
                f"Requested browser '{name}' not available. Usable browsers:\n {list(Browser.available_browsers.keys())}")

        # minimise the opened browser
        self.driver.minimize_window()

    def __enter__(self):
        """
        Allows to open browser connection using 'with' statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Allows to close browser connection using 'with' statment
        """
        self.close()

    def get(self, url):
        """
        Equivalent to Browser.driver.get method
        """

        self.driver.get(url)

    def close(self):
        """
        Equivalent to Browser.driver.close method
        """
        self.driver.close()

    def wait(self, by, name, timeout=conf.get_wait_timeout, regex=False):
        """
        Wait for specific element to be present in browser.
            Parameters:
                by (selenium.webdriver.common.by): html tag attribute to search for
                name (str): the 'by' value to search for
                timeout (int): time limit in seconds to wait for find values 'by' and 'name' to appear on page. Defualt: get_wait_timout on config.py
                regex (bool): if true, regex search patterns are enabled for 'name'.
        """
        # change the search name to re.compile of regex is enabled
        if regex:
            name = re.compile(name)

        # wait for given element to be available. raise error if timeout has been reached.
        WebDriverWait(self.driver, timeout).until(
            ec.presence_of_element_located((by, name))
        )

    def find(self, by, name, find_all=False):
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
        if find_all:
            return self.driver.find_elements(by, name)
        else:
            return self.driver.find_element(by, name)

    def wait_and_find(self, by, name, timeout=conf.get_wait_timeout, find_all=False, regex=False):
        """Wait for given element in the opened page on the browser and return the searched result.
           Combination of Browser.wait and Browser.find methods.
            Parameters:
                by (selenium.webdriver.common.by): html tag attribute to search for
                name (str): the 'by' value to search for
                timeout (int): time limit in seconds to wait for find values 'by' and 'name' to appear on page. Defualt: get_wait_timout on config.py
                find_all (bool): if true, a list of all found elements is returned. Default: False.
                regex (bool): if true, regex search patterns are enabled for 'name'.
               Returns:
                (webdriver.remote.webelement.WebElement): the found element(s)
        """
        self.wait(by, name, timeout, regex)
        return self.find(by, name, find_all)

    def find_parent(self, *args, **kwargs):
        found_element = self.find(*args, **kwargs)
        return found_element.find_element_by_xpath('..')


def main():
    with Browser(conf.browser, conf.driver_path) as browser:
        thing = Thing(id='4734271')
        thing.fetch_all(browser)
        thing.parse_all()

        # testing several properties
        assert thing.properties['creator_username'] == 'brainchecker'
        assert thing.properties['makes'] == 17
        assert thing.properties['tags'] == ['box', 'container', 'crate', 'stackable']
        assert thing.properties['filament_material'] == 'PLA'

        # printing thing information
        thing.print_info()


if __name__ == '__main__':
    main()
