from ThingScraper import Browser, Thing
import config as conf

URL = "https://www.thingiverse.com/thing:4734271"


def main():
    browser = Browser(conf.browser, conf.driver_path)
    try:
        thing = Thing(URL)
        thing.fetch_all(browser)
        print("Model Name:", thing.elements['model_name'].text)
        print("Created", thing.elements['created_by'].text)
    finally:
        browser.close()


if __name__ == '__main__':
    main()