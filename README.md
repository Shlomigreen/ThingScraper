# ThingScraper

The Thingiverse Popular 3D Printing Models Web Scrapper

---

## 1. Description

ThingScraper was created as part of **Israeli Tech Challenge \<itc\>** Data Science fellows program.
The purpose of this project is to scrape different information related to 3D printable models from the popular website [Thingiverse](https://www.thingiverse.com/).

## 2. Installation

1. Clone the git repo to local machine:

```bash
git clone https://github.com/Shlomigreen/ThingScrape
```

2. Project requirements: 
- The code mainly relays on [Selenium webdriver](https://www.selenium.dev/) and python. 
- In order to build database out of scrpped data, [PyMySQL](https://pypi.org/project/PyMySQL/) is also required.

```
pip install -r requirements.txt 
```

3. WebDriver:
In order to preforme scrapping using selenium, a webdriver for you browser of choice is required. Download one of the following that matches your browser's version:

- [Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)

- [Firefox](https://github.com/mozilla/geckodriver/releases)

- For additional browsers please refer to [selenium download page ](https://www.selenium.dev/downloads/)
  
  > Note that Browser object in our code only supports chrome, firefox, internet explorer and safari.

You will need to provide the webdriver's path inside the personal configuration file: `personal_config.py`.

## 3. Usage

- **Direct usage:** import ThingScraper objects into python project
- **Command line interface:** run `python main.py` from command line with acceptable tags

### 3.1. Direct usage objects

Direct usage is possible by importing several classes from `ThingScraper.py` :

* **a `Browser` object**: handles browser of choice for requesting and obtaining web information.

* **a `Thing, User and Make` objects**: recieves and holds infromation about a single thing (model) ,user or a make. Uses a Browser object for some of its functionality.

#### Basic usage

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

# Close browser
browser.close()

```

Expected output:
```
https://www.thingiverse.com/thing:4734271
	thing_id = 4734271
	model_name = stackable crate
	username = brainchecker
	uploaded = 2021-01-23T00:00:00
	thing_files = 3
	comments = 47
	makes = 17
	remixes = 12
	tags = ['box', 'container', 'crate', 'stackable']
	print_settings = {'printer_brand': None, 'printer_model': None, 'rafts': 'no', 'supports': 'yes', 'resolution': '0.2', 'infill': '5', 'filament_brand': 'esun, bq', 'filament_color': 'orange, grass green', 'filament_material': 'pla'}
	license = Creative Commons - Attribution
	remix = None
	category = Containers
```

#### Obtain thing's makes and remixes
```python
# Get a set of make ids for a thing instance
makes_set = thing.get_makes(max_makes=MAX_MAKES_TO_SCAN)

# Get a list of tuples of remixes ids and likes for a thing instance. 
# where the keys are the ids and values are thing object with 'likes' properties
remix_dict = thing.get_remixes(max_remixes=MAX_REMIXES_TO_SCAN)
```

### 3.2 Command line interface (CLI)

When running the program through a CLI, 1st positional argument is the type of object we want to scrap, 
should be: {Thing, User, Make, Remix, All}

```
python main.py Thing
```

To quickly scrape for all datatype can use:


```
python main.py All -n items_per_page -S pages_to_scrape  
```


To open the help menu use:


```
python main.py -h
python main.py --help
```

#### Tags

The following tags are can be added:

```
-S, --pre-search (int)
```

Used when mining for non thing objects, or when mining for all types. 

When mining for a non Thing obj, and its value is greater than 0 
it will mine Things from the search page, and use them as the source 
from which to mine the desired data.
The value provided indicates how many pages to mine

When mining all it indicates how many front pages to scrape for things.


```
-n, --num-items (int)
```

Used to indicate how many items to mine.

When used with a Thing object it indicates how many pages to scrape

When used with a non Thing object it indicates how many items to scrape.
In such a case a negative number can be provided to indicate scraping for 
all values.

When used with all, it indicates how many Makes and Remixes to pull per thing.


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

#### Reserved tags

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

## 4. Configurations

### 4.1. Personal configurations (personal_config.py)

- <u>browser</u>: str representation for browser to use (One of: chrome, firefox, iexplorer, safari). Default: chrome.

- <u>driver_path</u>: either a relative or absolute path for the webdriver file location for the provided vrowser. Default: chromedriver.

- <u>def_save_name</u>: the name of the exported file from CLI. Default: save.

- <u>wait_timeout_:</u> the time to wait in secods for web element to be available. 

- <u>pages_to_scan</u>: the number of pages to scan from the explore url.

- <u>max_makes_to_scan</u>: the maximum number of makes to scan per thing.

- <u>max_remixes_to_scan</u>: the maximum number of remixes to scan per thing.

- <u>implicitly_wait</u>: the number of seconds to wait in some javascript heavy pages (makes and remixes i.e.).


## 5. Database

Once a JSON file was created after scraping some things, a MySQL database can be created using the `build_database` function from `Database\build_db.py`.

```python
from Database.build_db import build_database

build_database(json_path, db_name=['thingiverse.db'], drop_existing=[True])
# json_path: the path to the JSON file created from CLI
# db_path: the path to save the created database. Default: 'thingiverse.db'
# drop_existing: if true, drop database first if existing. Default: True.
```

### 5.1. ERD

![ThingScraper-ERD](https://user-images.githubusercontent.com/31320788/113002582-9bbfad80-917a-11eb-9d5b-9e6129b4cec2.png)


### 5.2 Tables and fields

#### Users
Holds the information for all scrapped users
| Column      | Description |
|-------------|-------------|
| user_id     |automaticaly incremented id inside the database|
| username    |the username for each user|
| followers   |the number of followers the user has|
| following   |the number of users the user follows|
| designs     |the number of designs (things) posted by the user|
| collections |the number of collections created by the user|
| makes       |the number of makes the user has posted for different designs|
| likes       |the number of likes the user has on his profile|
| skill_level | the self estimated skill level the user set for itself (can be null)|

#### Things
Holds scrapped information of things and remixes
| Column           | Description |
|------------------|-------------|
| thing_id         |automaticaly incremented id inside the database|
| thigiverse_id    |the thing (or remix) id as provided by thingiverse|
| user_id          |foreign key for a creator user as exist in Users table (can be null if user was not scrapped)|
| model_name       |the model name given by the creator|
| uploaded         |the date  the thing was uploaded in ISO8601|
| files            |the number of files posted for the model|
| comments         |the number of comments the model has|
| makes            |the number of makes (prints) the model has|
| remixes          |the number of remixes (modifications) the model has|
| likes            |the number of likes the model has|
| setting_id       |foregin key for print settings found in Print_settings table (can be null if no print settings were provided)|
| license          |usage license as provided by the user|
| remix_id         |if the thing is a remix, this is a thing_id of another scrapped thing (can be null of remix source was not scrapped)|
| thigiverse_remix | the source thing for this remix in thingiverse id (can be null if has no original)|
| category         | the category to which the thing was posted to by the user|

#### Makes
Holds the information for all scraped makes
| Column        | Description |
|---------------|-------------|
| make_id       |automaticaly incremented id inside the database|
| thigiverse_id |the make id as provided by thingiverse|
| thing_id      |foregin key for thing id found in Things. the thing it was made from|
| user_id       |foregin key for user id found in Users. the creator who posted the make|
| uploaded      | the date and time the make was uploaded in ISO8601 format|
| comments      |number of comments for the make|
| likes         |number of likes for the make|
| views         |number of views the make has|
| category      |the category to which the thing was posted to by the user|
| setting_id    |foregin key for print settings found in Print_settings table (can be null if nu print settings were provided)|

#### Print settings
Information of print settings creator's used to print a model (either posted as thing, remix or make).

| Column            | Description |
|-------------------|-------------|
| setting_id        |automaticaly incremented id inside the database|
| printer_brand     |the brand of the printer used to print the model|
| printer_model     |the spesifc model of the printer used to print the model|
| rafts             |indicates if rafts were used when printing: 0 - no, 1 -yes, -1 = doesn't matter or NULL = wasn't indicated|
| supports          |indicates if supports were used when printing: 0 - no, 1 -yes, -1 = doesn't matter or NULL = wasn't indicated|
| resolution        |the printing resolution used|
| infill            |percentage of infill used for printing|
| filament_brand    |brand of filament used for printing. Note: for makes, this field also hold the color and material used.|
| filament_color    |color of the filament used for printing|
| filament_material |type of material used for printing|

#### Tags
| Column            | Description |
|-------------------|-------------|
| tag_id        |automaticaly incremented id inside the database|
| tag     |text of tag used in thing or remix post|

Since a thing can have multiple tags and tags can be related to multiple things, a many-to-many table `tag_thing` is exsiting.

#### Titles
| Column            | Description |
|-------------------|-------------|
| title_id        |automaticaly incremented id inside the database|
| title     |text of titled used in user profile|

Since a user can have multiple titles and titles can be related to multiple uses, a many-to-many table `title_user` is exsiting.


## 6. License & Contributing

Created by Konstantin Krivokon and Shlomi Abuchatzera Green.

Creative common usage 2021.
