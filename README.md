# ThingScraper

The Thingiverse Popular 3D Printing Models Web Scrapper

 

---

## Description

ThingScraper was created as part of Israeli Tech Challenge <itc> Data Science fellows program.

The main of the above is to scrape different infomation related to most liked 3D printable models from the popular site [Thingiverse](https://www.thingiverse.com/).

## Installation

Clone the git repo to local machine:

```bash
git clone https://github.com/Shlomigreen/ThingScrape
```

The code mainly relays on [Selenium webdriver](https://www.selenium.dev/) and python.  Thus the selenium module is required.

```
pip install -r requirements.txt 
```

In addition, a webdriver for you browser of choice is required as well. Download one of the following that matches your explorer's version:

- [Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)

- [Firefox](https://github.com/mozilla/geckodriver/releases)

- For additional browsers please refer to [selenium download page ](https://www.selenium.dev/downloads/)
  
  > Note that Browser object in our code only supports chrome, firefox, internet explorer and safari. 

## Usage

To print out details about models obtained by order from the [top models in the last 30 days page](https://www.thingiverse.com/search?type=things&q=&sort=popular&posted_after=now-30d), simply run:

```
python main.py
```

### Single thing scrapping

Includes the usage of the following:

* **a `Browser` object**: handles browser of choice for requesting and obtaining web information.

* **a `Thing` object**: recieves and holds infromation about a single thing (model). Uses a Browser object for some of its functionality.

```python
from ThingScraper import Browser, Thing

# Define a new browser instance
# Browser(browser_name, browser_webdriver_path)
browser = Browser('chrome', 'chromedriver')

# Define a new thing instance
# Thing(url) or Thing(thing_id)
thing = Thing(id='4734271')

# Open up thing page in browser and break it down to elements
thing.fetch_all(browser)

# Convert found elements into useful information
thing.parse_all()


# Print out obtained information
thing.print_info()
```

```
Thing number 4734271
https://www.thingiverse.com/thing:4734271
	model_name = stackable crate
	creator_username = brainchecker
	creator_url = https://www.thingiverse.com/brainchecker
	upload_date = 2021-01-23 00:00:00
	thing_files = 3
	comments = 43
	makes = 17
	remixes = 7
	tags = ['box', 'container', 'crate', 'stackable']
	printer_brand = None
	printer_model = None
	rafts = No
	supports = Yes
	resolution = 0.2
	infill = 5
	filament_brand = Esun, BQ
	filament_color = orange, grass green
	filament_material = PLA
	printer = HEVO
	license = Creative Commons - Attribution
```



### Configurations in `config.py`

- <u>browser</u>: str representation for browser to use (One of: chrome, firefox, iexplorer, safari). Default: chrome.

- <u>driver_path</u>: either a relative or absolute path for the webdriver file location for the provided vrowser. Default: chromedriver.

- <u>get_wait_timeout</u>: the time to wait in secods for web element to be available.  Default: 10.



## License & Contributing

Created by Konstantin Krivokon and Shlomi Abuchatzera Green.



Creative common usage 2021.
