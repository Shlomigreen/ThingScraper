from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import config as conf
import os
import re
import datetime

# Url of the main domain
URL = "https://www.thingiverse.com/"


def field_it(name):
    """
    Converts given name into lowercase str and replaces whitespaces with an underscroe.
    """
    return name.lower().replace(' ', '_')


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
        # in case neither id nor url were given, raise a value error.
        else:
            raise ValueError(
                "Construction arguments for thing object must include either an id or a url. Given arguments:",
                **kwargs)

        # Declaring empty dictionaries to hold page elements and properties (parsed elements)
        self._elements = dict()
        self.properties = kwargs.get('properties') if not None else dict()
        # self.properties = dict()

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

    def fetch_all(self, browser):
        """
        Breaks down the thing's url into elements (tags and classes) holding properties.
       :param browser: Browser object the be used for accessing the thing's url.
        """

        # open thing url
        browser.get(self.url)

        # obtain element holding the model (thing) name
        self._elements['model_name'] = browser.wait_and_find(By.CLASS_NAME, "ThingPage__modelName--3CMsV")

        # obtain element holding both the creator name and the uploaded date
        self._elements['created_by'] = browser.wait_and_find(By.CLASS_NAME, "ThingPage__createdBy--1fVAy")

        # obtain tab buttons holding metric information: files, comments, makes and remixes
        all_metrics = browser.wait_and_find(By.CLASS_NAME, "MetricButton__tabButton--2rvo1", find_all=True)
        self._elements['tab_buttons'] = {
            metric.find_element_by_class_name("MetricButton__tabTitle--2Xau7"): metric.find_element_by_class_name(
                "MetricButton__metric--FqxBi")
            for metric in all_metrics}

        # obtain all tag elements into a list
        all_tags = browser.wait_and_find(By.CLASS_NAME, "Tags__widgetBody--19Uop")
        try:
            self._elements['tags'] = [tag for tag in all_tags.find_elements_by_tag_name('a')]
        except NoSuchElementException:
            self._elements['tags'] = None

        # obtain print settings element
        # this is an optional information the creator can provide, so some models may not have this information.
        try:
            # wait for element to be available
            browser.wait(By.CLASS_NAME, "ThingPage__blockTitle--3ZdLu")
            # search for a div tag with certain class that hold the text for print settings
            print_settings = browser.driver.find_element_by_xpath(
                '//div[@class="ThingPage__blockTitle--3ZdLu" and text()="Print Settings"]')
            # obtain parent tag in order to access actual print settings
            print_settings_parent = print_settings.find_element_by_xpath('..')
            # each provided setting appears in a new p tag so save all of them into elements
            self._elements['print_settings'] = print_settings_parent.find_elements_by_tag_name('p')
        except NoSuchElementException:
            self._elements['print_settings'] = None

        # Model License
        self._elements['license'] = browser.driver.find_element_by_xpath(
            "//a[@class='License__link--NFT8l' and not(@class='License__creator--4riPo')]")

    def parse_all(self, clear_cache=True):
        """Obtain information from elements previously fetched for the thing.

               Parameters:
                clear_cache (bool): Clear previously fetched elements from memory after parsing. (Default: True)
        """
        # model name
        self.properties['model_name'] = self._elements['model_name'].text

        # get username found inside a tag text
        self.properties['creator_username'] = self._elements['created_by'].find_element_by_tag_name('a').get_attribute(
            'text')
        # get username profile url provided as a tag href
        self.properties['creator_url'] = self._elements['created_by'].find_element_by_tag_name('a').get_attribute(
            'href')

        # use created by html to obtain uploaded date text (uploaded date appears after a end tag)
        date_text = self._elements['created_by'].get_attribute('innerHTML').split(sep='</a> ')[1]
        # convert string date into actual date using datetime package
        # TODO: Handle datetime
        #self.properties['upload_date'] = datetime.datetime.strptime(date_text, "%B %d, %Y")
        # self.properties['upload_date'] = date_text
        self.properties['upload_date'] = datetime.datetime.strptime(date_text, "%B %d, %Y")

        # Metric information
        # set tab buttons to be ignore (hold not useful information)
        ignore_buttons = ('Thing Details', 'Apps')
        # for each tab button element, add it's name (converted using field_it function) and value to properties
        for key, value in self._elements['tab_buttons'].items():
            if key.text not in ignore_buttons:
                # using tab button names as field names. lowering case and replacing spaces with underscore
                self.properties[field_it(key.text)] = value.text

        # Obtain text from each tag element add add them all as a list to properties
        self.properties['tags'] = [tag.text for tag in self._elements['tags']]

        # print settings
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
        self.properties.update({field_it(key): None for key in possible_print_settings})

        if self._elements['print_settings'] is not None:
            # define regex search patter to obtain setting and its value
            pattern = r"(.*):<div>(.*)</div>"
            for setting in self._elements['print_settings']:
                # using regex to obtain setting name and value into two groups
                regex_result = re.search(pattern, setting.get_attribute('innerHTML'))

                if regex_result is not None:
                    # updating print settings (group 1 or regex resutls) with its value (group 2 of regex results) into the properties
                    self.properties.update({field_it(regex_result.group(1)): regex_result.group(2)})

        # license
        self.properties['license'] = self._elements['license'].text

        if clear_cache:
            self._elements.clear()


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
            EC.presence_of_element_located((by, name))
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
                find_all (bool): if true, returned value will be a list of all found elements. Default: False
                regex (bool): if true, regex search patterns are enabled for 'name'.

               Returns:
                (webdriver.remote.webelement.WebElement): the found element(s)
        """
        self.wait(by, name, timeout, regex)
        return self.find(by, name, find_all)


def main():
    with Browser(conf.browser, conf.driver_path) as browser:
        thing = Thing(id='5')
        thing.fetch_all(browser)
        thing.parse_all()
        thing.print_info()


if __name__ == '__main__':
    main()
