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
- In order to build database out of scrapped data, [PyMySQL](https://pypi.org/project/PyMySQL/) is also required.

```
pip install -r requirements.txt 
```

3. WebDriver:
In order to preform scrapping using selenium, a webdriver for your browser of choice is required. Download one of the following that matches your browser's version:

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

* **a `Thing, User and Make` objects**: receives and holds information about a single thing (model) ,user or a make. Uses a Browser object for some of its functionality.

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
should be: {Thing, User, Make, Remix, API, All}

We can give several arguments of this type, and they will be executed in the order given.


```
python main.py Thing
python main.py Thing API User
```
The 'All' option is a shorthand, the following are identical:

```
python main.py All
python main.py Thing Remix Make API User
```
To quickly scrape for all datatype and save, we can use:

```
python main.py All -n items_per_page --google-app-name "PERSONAL-KEY" -J  
```
To open the help menu use:

```
python main.py -h
python main.py --help
```

#### Tags

The following tags are can be added:

```
-n, --num-items (int)
```
Used to indicate how many items to mine.

When we provide many search arguments, we should also provide a 
'num-items' for each search argument:
```
python main.py Thing User API Make -n 5 1 4 2 
```
Note that in the example above the 'User' argument doesn't take a 
'num-items' argument by default, but due to the order of the
type commands that we provided we have to give it any argument
to reach the other parameters.

In this example the 'User' argument is ignored.

We can also provide a non-matching number of arguments, for example 
the following arguments are identical:
```
python main.py Thing User API -n 5 4 4
python main.py Thing User API -n 5 4
python main.py Thing User API -n 5 4 4 5 6 7 8   
```

When not enough arguments are provided the last argument is used as 
a substitute.

When too many arguments are provided, the extras are ignored.

If we are using a shorthand command (like 'All') we have to give it 
a 'num-items' corresponding to each action it represents, 
for example the following are identical:

```
python main.py All -n 1 2
python main.py All -n 1 2 2 2
python main.py Thing Remix Make API User -n 1 2
python main.py Thing Remix Make API User -n 1 2 2 2
```
Because 'All' is a shorthand for 5 commands, it requires 5 parameters, 
but since the last parameter usually doesn't require an argument we 
can ignore it, and if the last parameter are identical we can  
omit them as well. 

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
-v, --volume (int)
```
Set how much text to output to the command line:

 - 10 = quite

 - 20 = normal

 - 30 = debug

 - 40 = verbose

If the provided level is not in the list, it will be set to the nearest value above.

Normal by default.

```
--google-app-name (str)
```
google developer code used to access google APIs, default values is
provided in the personal configuration file.

```
--headleess (bool)
```
runs the scraper in headless mode (no visible browser)

```
-d --database (bool)
```
If indicated, a database will be created over the MySQL server
(specified in parameters, or by default in the Database/config.py 
file)

```
--not-all-users (bool)
```
search only for the exact number of users specified in the 
'num-items' tag

```
--mysql-host (str)
```
set the host name of the mySQL server. 
default in the Database/config.py file

```
--mysql-user (str)
```
set the username of the mySQL server. 
default in the Database/config.py file

```
--mysql-password (str)
```
set the password of the mySQL server. 
default in the Database/config.py file

## 4. Configurations

### 4.1. Personal configurations (personal_config.py)

- <u>browser</u>: str representation for browser to use (One of: chrome, firefox, iexplorer, safari). Default: chrome.

- <u>driver_path</u>: either a relative or absolute path for the webdriver file location for the provided browser. Default: chromedriver.

- <u>def_save_name</u>: the name of the exported file from CLI. Default: save.

- <u>wait_timeout_:</u> the time to wait in seconds for web element to be available. 

- <u>pages_to_scan</u>: the number of pages to scan from the explore url.

- <u>max_makes_to_scan</u>: the maximum number of makes to scan per thing.

- <u>max_remixes_to_scan</u>: the maximum number of remixes to scan per thing.

- <u>implicitly_wait</u>: the number of seconds to wait in some javascript heavy pages (makes and remixes i.e.).

- <u>google_ktree_API_key</u>: A token to use Google's APIs: Knowledge Graph Search API.


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
| user_id     |automatically incremented id inside the database|
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
| thing_id         |automatically incremented id inside the database|
| thingiverse_id    |the thing (or remix) id as provided by thingiverse|
| user_id          |foreign key for a creator user as exist in Users table (can be null if user was not scrapped)|
| model_name       |the model name given by the creator|
| uploaded         |the date  the thing was uploaded in ISO8601|
| files            |the number of files posted for the model|
| comments         |the number of comments the model has|
| makes            |the number of makes (prints) the model has|
| remixes          |the number of remixes (modifications) the model has|
| likes            |the number of likes the model has|
| setting_id       |foreign key for print settings found in Print_settings table (can be null if no print settings were provided)|
| license          |usage license as provided by the user|
| remix_id         |if the thing is a remix, this is a thing_id of another scrapped thing (can be null of remix source was not scrapped)|
| thingiverse_remix | the source thing for this remix in thingiverse id (can be null if has no original)|
| category         | the category to which the thing was posted to by the user|

#### Makes
Holds the information for all scraped makes
| Column        | Description |
|---------------|-------------|
| make_id       |automatically incremented id inside the database|
| thingiverse_id |the make id as provided by thingiverse|
| thing_id      |foreign key for thing id found in Things. the thing it was made from|
| user_id       |foreign key for user id found in Users. the creator who posted the make|
| uploaded      | the date and time the make was uploaded in ISO8601 format|
| comments      |number of comments for the make|
| likes         |number of likes for the make|
| views         |number of views the make has|
| category      |the category to which the thing was posted to by the user|
| setting_id    |foreign key for print settings found in Print_settings table (can be null if nu print settings were provided)|

#### Print settings
Information of print 'settings' creator's used to print a model (either posted as thing, remix or make).

| Column            | Description |
|-------------------|-------------|
| setting_id        |automatically incremented id inside the database|
| printer_brand     |the brand of the printer used to print the model|
| printer_model     |the specific model of the printer used to print the model|
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
| tag_id        |automatically incremented id inside the database|
| tag     |text of tag used in thing or remix post|

Since a thing can have multiple tags and tags can be related to multiple things, a many-to-many table `tag_thing` is existing.

#### Titles
| Column            | Description |
|-------------------|-------------|
| title_id        |automatically incremented id inside the database|
| title     |text of titled used in user profile|

Since a user can have multiple titles and titles can be related to multiple uses, a many-to-many table `title_user` is existing.


## 6. License & Contributing

Created by Konstantin Krivokon and Shlomi Abuchatzera Green.

Creative common usage 2021.
