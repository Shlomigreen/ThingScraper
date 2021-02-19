from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import config as conf
import os
import re


class Thing:
    """
    Thing class is design to hold single thing page information.
    Once an instance is created by providing thing url, fetch_all() function is need to be used in order to obtain
    all possible elements from the page.
    After fetching, parse_all() will generate a dictionary holding all information about the thing (model).
    Information can be accessed by using squared brackets on the thing instance.
    """
    def __init__(self, url):
        self.url = url
        self.thing_id = url.split(sep=":")[-1]

        # Declaring empty dictionaries to hold page elements and properties (parsed elements)
        self.elements = dict()
        self.properties = dict()

    def __getitem__(self, item):
        if item in self.properties.keys():
            return self.properties[item]
        else:
            return None

    def __setitem__(self, key, value):
        self.properties[key] = value

    def keys(self):
        return self.properties.keys()

    def fetch_all(self, browser):
        # open thing url
        browser.get(self.url)

        # thing model_name
        self.elements['model_name'] = browser.wait_and_find(By.CLASS_NAME, "ThingPage__modelName--3CMsV")

        # created by
        self.elements['created_by'] = browser.wait_and_find(By.CLASS_NAME, "ThingPage__createdBy--1fVAy")

        # tab buttons
        all_metrics = browser.wait_and_find(By.CLASS_NAME, "MetricButton__tabButton--2rvo1", find_all=True)
        self.elements['tab_buttons'] = {
            metric.find_element_by_class_name("MetricButton__tabTitle--2Xau7"): metric.find_element_by_class_name(
                "MetricButton__metric--FqxBi")
            for metric in all_metrics}

        # tags
        all_tags = browser.wait_and_find(By.CLASS_NAME, "Tags__widgetBody--19Uop", find_all=True)
        try:
            self.elements['tags'] = [tag.find_element_by_class_name("Tags__tag--2Rr15") for tag in all_tags]
        except NoSuchElementException:
            self.elements['tags'] = None

        # print settings
        # TODO: Not all models has this, check what happens in a model without print settings
        try:
            print_settings = browser.driver.find_element_by_xpath('//div[@class="ThingPage__blockTitle--3ZdLu" and text()="Print Settings"]')
            print_settings_parent = browser.driver.find_element_by_xpath('..')
            self.elements['print_settings'] = print_settings_parent.find_elements_by_tag_name('p')
        except NoSuchElementException:
            self.elements['print_settings'] = None

        # License
        self.elements['license'] = browser.driver.find_element_by_xpath(
            "//a[@class='License__link--NFT8l' and not(@class='License__creator--4riPo')]")


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

    def wait_and_find(self, by, name, timeout=conf.get_wait_timeout, find_all=False, regex=False):
        """Wait for given element in the opened page on the browser and return the searched result.

               Parameters:
                by (selenium.webdriver.common.by): html tag attribute to search for
                name (str): the 'by' value to search for
                timeout (int): time limit in seconds to wait for find values 'by' and 'name' to appear on page. Defualt: get_wait_timout on config.py
                find_all (bool): if true, returned value will be a list of all found elements. Default: False
                regex (bool): if true, regex search patterns are enabled for 'name'.

               Returns:
                (webdriver.remote.webelement.WebElement) : the found element(s)
        """
        # change the search name to re.compile of regex is enabled
        if regex:
            name = re.compile(name)

        # wait for given element to be available and then retrieve it
        # usage: wait_and_find(driver, By.CLASS_NAME, 'class_name')
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, name))
        )

        # return found element(s) depends
        if find_all:
            return self.driver.find_elements(by, name)
        else:
            return self.driver.find_element(by, name)



