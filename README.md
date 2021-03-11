# ThingScraper

The Thingiverse Popular 3D Printing Models Web Scrapper

---

## 1. Description

ThingScraper was created as part of Israeli Tech Challenge <itc> Data Science fellows program.

The main of the above is to scrape different infomation related to most liked 3D printable models from the popular site [Thingiverse](https://www.thingiverse.com/).

## 2. Installation

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

## 3. Usage

To print out details about models obtained by order from the [top models in the last 30 days page](https://www.thingiverse.com/search?type=things&q=&sort=popular&posted_after=now-30d), simply run:

```
python main.py
```

### 3.1. Usable objects

Includes the usage of the following:

* **a `Browser` object**: handles browser of choice for requesting and obtaining web information.

* **a `Thing, User and Make` objects**: recieves and holds infromation about a single thing (model) ,user or a make. Uses a Browser object for some of its functionality.



### 3.2. Basic usage (signle thing scraping)

```python
from ThingScraper import Browser, Thing, User, Make

# Define a new browser instance
# Browser(browser_name, browser_webdriver_path)
browser = Browser('chrome', 'chromedriver')

# Define a new thing instance
# by giving 'thing_id' or 'url' arguments
thing = Thing(thing_id='4734271')

# Attach browser to thing instance
thing.set_browser(browser)

# Open up thing page in attached browser and break it down to elements
thing.fetch_all()

# Convert found elements into useful information
thing.parse_all()


# Print out obtained information
thing.print_info()
```

```
https://www.thingiverse.com/thing:4734271
	thing_id = 4734271
	model_name = stackable crate
	username = brainchecker
	uploaded = 2021-01-23T00:00:00
	thing_files = 3
	comments = 47
	makes = 17
	remixes = 11
	tags = ['box', 'container', 'crate', 'stackable']
	print_settings = {'printer_brand': None, 'printer_model': None, 'rafts': 'no', 'supports': 'yes', 'resolution': '0.2', 'infill': '5', 'filament_brand': 'esun, bq', 'filament_color': 'orange, grass green', 'filament_material': 'pla'}
	license = Creative Commons - Attribution
	remix = None
	category = Containers
```

## 4. Configurations

# 

- <u>browser</u>: str representation for browser to use (One of: chrome, firefox, iexplorer, safari). Default: chrome.

- <u>driver_path</u>: either a relative or absolute path for the webdriver file location for the provided vrowser. Default: chromedriver.

- <u>get_wait_timeout</u>: the time to wait in secods for web element to be available.  Default: 10.

## Command Line Interface

When running the program through a CLI, 1st positional argument is the type of object we want to scrap, 
should be: {Thing, User, Make, Remix}

```
python main.py Thing
```

```
python main.py -h
python main.py --help
```

Can be used to view the help menu.

### Tags

The following tags are can be added:

```
-S, --pre-search (int)
```

Used when mining for non thing objects. 
When its value is greater than 0 it will mine Things from the search page, 
and use them as the source from which to mine the desired data.

The value provided indicates how many pages to mine

```
-n, --num-items (int)
```

Used to indicate how many items to mine.

When used with a Thing object it indicates how many pages to scrape

When used with a non Thing object it indicates how many items to scrape.
In such a case a negative number can be provided to indicate scraping for 
all values.

```
-N, --Name (str)
```

The name of the file. Used when exporting to json.

```
-B, --Browser (str)
```

The name of the browser. Used to configure selenium simulation.

```
-D, --Driver (str)
```

Driver path - browser. Used to configure selenium simulation.

```
-J, --save-json (bool)
```

Save a copy of the data in a json file at the end of the run.

```
-j, --load-json (bool)
```

Open save from json file at the start of the run

```
--q, --quiet (bool)
```

Output minimal text to command line

```
-v, --verbose (bool)
```

Output as much information as possible to the command line

### Reserved tags

The following tags are reserved for future use, but not yet implemented:

```
-I, --Interactive (bool)
```

Used to open interactive mode at the end of the run

```
d, --load-db (bool)
```

Open save from SQL database at the start of the run

```
-O, --Order-parameter (str)
```

Used when mining for Things. 
Indicates how to sort the items on the search page.

```
-u, --update (bool)
```

When saving to database replace existing values with new values mined.

```
-a, --append (bool)
```

When saving to database skip existing values.

```
-p, --print (bool)
```

Don't save to database, print results to command line only

```
--replace (bool)
```

Clear SQL database and save anew. 

## License & Contributing

Created by Konstantin Krivokon and Shlomi Abuchatzera Green.

Creative common usage 2021.
