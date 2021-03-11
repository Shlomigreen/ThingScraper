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

### 3.3. Obtaining thing's makes and remixes

```python
# Get a set of make ids for a thing instance
makes_set = thing.get_makes(max_makes=MAX_MAKES_TO_SCAN)

# Get a dictionary of remixes (thing) ids for a thing instance
# where the keys are the ids and values are thing object with 'likes' properties
remix_dict = thing.get_remixes(max_remixes=MAX_REMIXES_TO_SCAN)
```

## 4. Configurations

#### 4.1. Personal configurations (personal_config.py)

- <u>browser</u>: str representation for browser to use (One of: chrome, firefox, iexplorer, safari). Default: chrome.

- <u>driver_path</u>: either a relative or absolute path for the webdriver file location for the provided vrowser. Default: chromedriver.

- <u>def_save_name</u>: the name of the exported file from CLI. Default: save.

- <u>wait_timeout_:</u> the time to wait in secods for web element to be available. 

- <u>pages_to_scan</u>: the number of pages to scan from the explore url.

- <u>max_makes_to_scan</u>: the maximum number of makes to scan per thing.

- <u>max_remixes_to_scan</u>: the maximum number of remixes to scan per thing.

- <u>implicitly_wait</u>: the number of seconds to wait in some javascript heavy pages (makes and remixes i.e.).

## 5. Command Line Interface

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

## 6. Database

Once a JSON file was created after scraping some things, an sqlite database can be created using the `build_database` function from `Database\build_db.py` file.__

```python
from Database.build_db import build_database

build_database(json_path, db_path=['thingiverse.db'])
# json_path: the path to the JSON file created from CLI
# db_path: the path to save the created database. Default: 'thingiverse.db'
```

### 6.1. ERD

[Click to view the ERD in diagrams.net]([Flowchart Maker &amp; Online Diagram Software](https://app.diagrams.net/?title=ThingScraper.drawio#R7V3vd6I4F%2F5res6%2BH9ojIIof%2B3NmdtuZbtvd6X7qiRCVEcTF2Or%2B9W9AQG2iEoVwg3bnbEuIEO9zkye5ubn3zLj2Z19CNB48BA72zvSGMzszbs503dQ79P9RwXxRYLXbi4J%2B6DqLIm1Z8Oz%2Bh5PCRlI6dR08WZQlRSQIPOKOJ2uftoPRCNtkrQyFYfCxXq0XeOtvHaM%2BZgqebeSxpT9dhwySUq3RWN74it3%2BIHm1ZSY3usge9sNgOkred6Ybd%2FHP4raP0mcl9ScD5AQfa0V4Ru6CEUm%2BwSMOfTTCI0LvPKBwiMMz83ZASCSIyzOdPveuF9W%2B6AdB38No7E4u7MCnxfaEVrnrId%2F1IhRWHnSVPIi%2Bzrg9M67DICCLv%2FzZNfYiJFOUFm2623A3E1MYPTfHB67P3%2Bf3wwYZff0w%2FiYPD%2F3HdvdcNxaPeUfeNJH%2Fy8Ad9SeJiMg8hYVKaxz9SVA3KrqaEBSSRHuMBi2g%2BkCQO6LfzbjR4mvPQ%2BOJG1dflAxcz7lH82BK0gelV1c9d4adp4XyRHWpHt3Th0WX0cMjOT8njYluI8%2Ftj%2BjfNv3y0RuvQjyhbblHE5LU6Lmedx14QRg333AQtnp23O4wGOKVOy3bwt0evcMKNJHxOw4Jnq0UJQL%2BggMfk3BOqyR3jUZz8ZGk79GCxfXHUpPpGxdlgxUlblpJRZToXj979hJS%2BkeCqgjCTQbhjdjS705c5D3Rbo1G%2FRjmdRQjKJwwGL%2BgsI9JUjAO3AiE23e86DmNT9IfBSOcVou%2FnXlF%2F9Hve924MM9M2oBreq0tr%2Bm%2FqHpIroMRhYsqVfQqTLH9wBG%2BVyQYJ%2B%2FxcC9tRphIM%2Fq7GxBCO%2BJCE1hct3eF3WjPU7TzgWuUhq3JYPv4hwi6Af2yPS8eBAeu4%2BDRoh9H4zpaIs4Bk4tAJvXPcHzuvXkRaeZGZAWCVNpyEGgxCJBo%2FHyjn7rWzy4bANFIx85F3avJGNm0xfeLT7Y%2BwWWWAtfsbFMH0holdaD%2FkDG4%2FuOG6K8%2FrMb33tuv8Pd%2FzzsMet%2B%2Bv6gOWaNMyLR0gFvDTGqXax8zoYmAK0xorcoJzToIW0m9Ma%2F827nlXxl9sQMgpa%2B%2BS5s8wRGHwRP%2BzqGweHSgsFW6QlefrkrDSCo98UFiu5RkeqJr2p5lY9uukqOYZXbXMptmqezVkcheXOh1tn%2FeQVyOsQhs12QQ%2FMWXuMZIfDrBYW2Y61BcoDBXOgbWkbkKwggAc7GdSTJz1XZhpelVc5PG9kCA3S9v78pvmK%2BKmTR2Y8WPdureRsjHACVf2MC3x55JxeSksTskf18%2BXX%2B9fPpNbzT%2BdwILFEsZ5omUCiIls2pSSl8GqnPl7DupHgLmIIO1lE%2FHXoAcXOflkQAwUBjIYM3eL7evdV4fiYMEgHm0E%2FMUxDxW5cyj8OrHgL%2F6MdjVD5UO3uxVVoMRTb2Fj8EufOptlRPHqHrWSffATqxzKOtkHs7VbRBZADtXzr4Dy5uB30R269UOfD%2FWc3hyL2pQU9CRIX3w0RCPio4M6QB7Ip6DiadZOfE0AXauvH0nv7wrIx7WD99Hw1ovdwRQgcI6HF%2F9mrOOMEZSWWfcDwf4ny%2FmzPzzr%2B7lUO%2B%2B2%2B%2Fnx2ljYxDKzUObSactkXS4UMI1se0Q92bFrIRyuM1hDWwh9t2ZypxTICoVUA63eTUzsBWPUPXLHPM4GaeU47BVL3NMuJSzc7Jmwt%2FVMVnS8dx6L3MEUIGyzDFrRjolYFQ96zRl7%2BpEh4J6PR3YoSCn1W2ZIgfCxElJZpAGPtSsc4%2FKp4Ka8PeBmuw%2B0AQTEoW1qffJIAFswLDVsW0FiWMEgK1OW0FF0ZHMEAt8LBXeCmrC3wpqsltBnmvj0aTOh34EcIHCO012Myg99KPV%2B9CPOFjVE5DRORFQQQRUeZSEJjvjU3k9lKomZE5iD3bHm0X1XgwJAAOGlHQGqHovhsQxqt5D4TjPn5bgodCUGRSBCyXc46f77LSalbEOtzns4dM4MmoSWy4mIIDiL3EnfAM%2BUHwVWDO10txTPEJyQ5%2B%2Btge%2F3%2Fz749L6ifSPn9%2B6z%2FY0i9dwZNxTwjKoKTP2AR9LHWDf4sh7mx7CWPPwm8j6KtiI4H6QPBuW3PcJmHkgMBXQDr%2FJm6PvmHWxwxWElVQCepp5fwx%2F%2BU9D83V2%2F3z%2B53l3%2FI2z9sFOH6eBx%2BmwPwj6wQh5t8vSqzgjC3YS6S3r3Aex2KN8AL8wIfMklwiakoAWDYjvJXepGMP5a%2FL5%2BOKf6OLCTC9vZqs3b%2BZnqbcB1ZHLKCMNLbh98tHI%2BRHjHd%2B4c6OvnnzM4VWjxSuVBKloEkxDG2%2BrmOg9Sfn4bMcaOZL0Vi0JsYcInV6vzXl4KpB89DFi9aV2ZVuxCUVmMTrSRyxamnxqqUhUdGi%2BUi2ZLGx%2Bj9Zee0%2ByY3KXt3rD%2FKTGiwYslToTyf6GGNZgFmfFebZDOvqE9M75md5CPtXfq1F3Mo7Vo3GD6DiDoo2exg2eRIPE585C%2BzlZ1%2B11j5hkPOIMUZ8GnWjMcG3kXSbFPh3v4s72MXAJfqZDUvTGD9papgPGmQKStD16cn2XJiq6DnzXpm1%2BRiOKYOPhmav4wgNXc12zOOewtUaTM46ZpRnaGHwzPL1Ivi6xs4I%2BWcDrUHjpL98dUU2IJBIG%2BJdNwIKcgfoVe%2B84etI6%2BrRfFQKu2VpHl3PY0dQ54Oplgas12D3YF1S%2FlFa9Hm7Z3JRWTrvTbfBJS3yCqK3Dywvdw4O3Ux687NatyDRR8WUxP3%2FSjo5wUEorHrol5jhg7YaK5rTaob0g1s4b2sjaAgnqK7pduDub1cFAbV5LW3JxYx1fFbXh7s5nVRRoGm82qkmFjZPX5YgITQheYULj%2BVvKJbQDw%2BrD8nZZ6ipg%2BuLEuqf0BVDoxcXxzo8KFK7iGOiXUddrYvctCiwAHMU5VRibxN5etvQsVRfWZvQfb2Hdin%2BSd6yUL34KsqdY6wtujRc9Su6K22QNKpInKKvmjsqW3SJ2lh29SKEFucmaW0D66%2B67ZDDhB%2FLXTI4zVS0W5CUBtWVzW3LnqY1XlTzUeHlJ2nJRY%2B0o8vnOQdjqwTqu37It3O2VynfVr9fTFkDnu9wYwD%2BgorVYG0nsLKwow5UADRhGa7HGFUUZrTyUqmewFmtd%2BWuCw%2FrtgaeJrkXyTR%2Fqv5J7DzyLiFYCwDwXlqPZMxDZcG3tEciu8jkIa3Cp1SZ4K%2F%2B8sLo5CWv3UDi3%2BL674AJIbZ6idOQCxxpLFJ2h7LvmFgeNl6BacvbxFmsqOSJGE4JXmNEArKoPM6kAW1NnugqYv9qsHSPir7rnHxeABgphtVnrR%2B2OQBUFVvVEZZwy8hXGS7xgRFJ5yVA5JZ%2BhQE4%2Bg5OUr0e7RPCxzRql%2FtAmgg0QHspCJau%2FcCoPJAj8c4rGWhT%2F8NCUTUAKx2M1FMjNZ3CS8y0IKD7GCU70xY1tRQRllUtAR5ehbw%2BQABCQdorGWhgB8eIQSSagBsAOlrf%2FpKoImoBY844Tx4eo9fpHABkw9KMfG%2F2IgwSAfoxTFLzC6Ce%2FJ0tpaCq8D5SpImT6MTiR8GifoBJzg3pTkAA6UCjIOLbkfXuABIGCjjMIeBkUxIsGJpuC4MYBz9F%2F4B9fMwzWI8tH9U4cK4ILGPKpzWG18kCCQD4n81th5JP3bH15aKYtANXBcvcfBcxvnOxHdc9aLoILFPI5vtxHeyQ%2Fqp58pCcurzH5tKsnH5W93xTIRG7wUpEPqYDePPyOPYDCL2x0KyQXuVwK4uQiX%2BaErbMf9h5gVU9FOifM38NWq4KiZ5wdE1tO84xzxtnSu0aLj7OwVdX6lP5Bz%2B2ZUCLC7NbFEc0%2BBA7ULvuCOoecdU7mnzodcl5qL9z5ia6xzpGRZfa4DjmLILUtbZZc5GrjK7nnKec9UNMkTjHHvASTx2m53ZGKcxujbaQvmSeauVCm25ag%2BloueW%2FWzEqIiS%2FdDQHBkuzBatJT4ehUQEZ8tGpmuy0eIpnMs2E8ZffgJZNRPWJa7rHUqvyUs66xO%2Fsqx7RcKjPkpRVr%2Bj2CmJYi0IBZS6WdsS78VQZK1TMY5xyNfAbLAk7CYbAtkS6LYrDqz0nrKdh1oTABC31lFKaz9neFQyCWgAwcBju2cwN7oASAwY7T%2FlcKI1V%2BcDp7Mqj%2Blbv7wPfc1A12wjcdewGK8pzDk3xxI1sRzpuS%2BSc9xbmaHu72td4EJO6%2BWTkBGSfvzcIIqPKj07qhsPdmpoqgCYg14dmB78e6Dk%2FyhY1sAtCAIaD0GM3xLIDEUaqef5qnc9NF8U%2F156b1psLnpjNVhMw%2FTXbPtu5H10RwgUM%2Bx3Zweg%2BUZJLP9Wt78PvNvz8urZ9I%2F%2Fj5rftsT89PUXMLox6Zp6a5WKoRM3ebGsKgHW4LWZfwdxd%2F1IR0DsSkAsrhtrg2zt9lIVQ53ZwsbYXRjcxz0lws1bCzbVNDwHTDsbEhgvtB8mhYUi9qPANtYeO2ODU31DlJVTFQATCzyfYziBzjej0dmGOc0%2Bq2TCGvSGFuyjI8V2eF40QtUNoxLguZAYKyNsic9UyYYELo%2BDKpuXOcADpgzHOmzqBVm9VSUShVT1ottk89hpQS3p6TnrURMEXjemSMKUJcwl6PZrp6ShmL5zjX5CFdItRsh5Q8YVElrkcrP95b4npw4S0PXdZrvFZxPTLtBTxBabH%2B4IpPUPaN7SGA1pYJiyYXPdYEr%2BiEZd%2FYHuKoaZxNKcnzzBZrlT8iWhOCV5jWePE%2BJNPaYQfoga2yM12FTGKsW8U4jDvAWzdEIyVprAR84NAWa8qvnYm4KLQA0FVbyIvixE6CET7kslNbyLMWGBmlmgiZjNrs5C4lIz9wah3LWQQfMGTUZqdrR0JG4mhBICMhH4sTGYkG65DMRkIb0NDYyMot8crYKD18uDK6hahX72NpAriAYSGL3dT69v3lN63eBCQMFAACsk62usIIKPcWY3loCp32AEZAqSqCJiDOBtN0HGlnrTlIABo4HMTdTao5B4kDBYCDUjPSiYMO5yBeeA65HNTRAHawvBJPVREyB3XSPr6yCMKTwJsSNxgBlH1hg5sAOGBYqMN6BR2JPU4cLQBUZAnFdjhRkWikDsnLIaHTiMCoyFLAVcFiXRXcUSQhgHIvbo6toI%2BCdbQ%2BCuJoAaChzslHoTAa4kXtkLwiUtlJoaOAk0KHdVKg8kFRxML6u8wJAASGjjpH66UgjhYEOjp5KRRGR7yoHpLpSGUvhQ58L4XscDyPjuxYSPDkX9wAp567gtFg3RWOhY4U9FkwGvqJjgo7Nls1HRkNhX0WMlUETUesz0JGRz6iek9FDBCCosY4EYzgMBLrvHAcjLQHWlIZ6Wnm%2FTH85T8NzdfZ%2FfP5n%2Bfd8bdzdscbO32cHgCmNDAI%2BsEIebfL0qswmI6ijD4L8S3r3Aex3KOT%2Bb8wIfMksAeakoAWDYjvJXepHMP5a%2FL5%2BOKf6OLCTC9vZqs3b%2BbZlXMZhrFC3D5RqF%2BCBzSaL27cRab7RbU4qsiyoo9Gzo9YL%2BIbKxVZYFNxBNPQxluw1hqJ3YakZLyxppn0h0iuW3UixB4i7jtea0nhgLOUdQJ8HfDr8%2Ff5%2FbBBRl8%2FjL%2FJw0P%2Fsd09T9P15cC7Awpvdh9RJt6aGN6fgFxF%2FDOUa6qxRHxdMQ7o4J28eKeBO4rDO%2F4o%2FXJovlIhmcEvn%2FwYFSypJDtgkE6PDXNVd3bX181PurZowVLzsq%2ByvzKyxjjAg0%2FuUaVkVUxzSuxUxSwGR8WqaLbWVctsb1fFz%2FWNjgRVZC2JMlRx5pJME%2BnfK4pIr5Z6GF1AU8MsRF0VenjYHJd10q3dsLN5ciRhzpMlpwc28OiiA48MDtSqXXJJmZEl6%2FB1RUwHv3QgzDP4HTBcpTWVmcFpjc9TMnO7%2BjIfsJKRLu%2BcT7S%2BnP7Buh0zHSY1Grk%2BiiC7in9fTsbYzow66UUcE5QWREYZ16Y9BnWx9xhM3Njl3LhJzUJZhcvEHBQbka6SN9wMCBlTHC%2BjL6%2FfOfrEsz%2BMoTtu%2FesPL2wvmDq9MBiRixFVNfqtUTjEUew%2B%2BveYPoCifmcPaHehv3HonE%2FmfjfwotLbp5vz7wFBUWsuHr9%2F2abz%2Be1KVvMTcDxTeWLBWDUzaVbrQm8fTsPjwcut9XZ5dYdmt2%2Fj4Ue38%2BSnpqYVXP%2Ba4PDtxSXelgRpqoaKtWzMDxXbtcymGb2jHyLHpc9bDzBLf4rRgU8q0Mob97xTgKmRi%2F8p1h4D6tZ%2BclAA2bIi2nNbzLpEKRLPfquegtgX47aQdV2fRiOpmmFiC0elgij23BazfuuKhoQtCyGZEez5I%2B3p9G4xDMSL9SqVgTR2cqkyBWWpm%2BByUJZ5ZylxEs3k681CAsBAoSHOerrePCSOUeVE1GQ7U02WxSxmhy5k27zDuVIXsk0BC1X95hF8VLertTpL2SbrcahoKpTtqgt3YtFk%2FQdVnljszoJyKFBQJhrN2qS43p0DpSDMqp94HJYiQ3EqE8FWmMoqXxM3WTMhwM6YV%2F6g0mLzm8ga%2FGLiAij0opZaAqhAYSlO8t3aHU8oCKvK2clko08AdtyqxFl960Rk1fVlq6lEvqMeH282hBlQp0ylnPu2ez3tVJKWJB2hl2EQkFVvohCNBw9xrhbj9v8%3D))

### 6.2 Tables and fields

**Users**: hold the information for all scrapped users

* <u>user_id</u>: automaticaly created id inside the database

* <u>username</u>: the username for each user

* <u>followers</u>: the number of followers the user has

* <u>following</u>: the number of users the user follows

* <u>designs</u>: the number of designs (things) posted by the user

* <u>collections</u>: the number of collections created by the user

* <u>makes</u>: the number of makes the user has posted for different designs

* <u>likes</u>: the number of likes the user has on his profile

* <u>skill_level</u>: the self estimated skill level the user set for itself (can be null).

* <u>user_titles</u>: table that holds the titles each user added for itself (can have none).
  
  * <u>title_id</u>: foregin key for a title found in **Titles** table
  
  * <u>user_id</u>: foregin key that match the database user id.



**Things**: holds the information for all scraped things and remixes

- <u>thing_id</u>: automaticaly created id inside the database

- <u>thingiverse_id</u>: the thing (or remix) id as provided by thingiverse

- <u>user_id</u>: foreign key for a user found in Users table (can be null if user was not scrapped)

- <u>model_name</u>:  the model name given by the user

- <u>uploaded</u>: the date  the thing was uploaded in ISO8601

- <u>files</u>: the number of files posted for the thing

- <u>comments</u>: the number of comments the thing has

- <u>makes</u>: the number of makes (prints) the model has

- <u>remixes</u>: the number of remixes (modifications) the model has

- <u>likes</u>: the number of likes the model has

- <u>settings_id</u>: foregin key for print settings found in Print_settings table (can be null if nu print settings were provided)_

- <u>license</u>: usage license as provided by the user

- <u>remix_id</u>: if the thing is a remix, this is a thing_id of another scrapped thing (can be null of remix source was not scrapped)_

- <u>thingiverse_remix</u>: the source thing for this remix in thingiverse id (can be null if has no original)

- <u>category</u>: the category to which the thing was posted to by the user 

- <u>thing_tags</u>: tags related to the thing and added by the user
  
  - <u>tag_id</u>: foregin key for tag found in **Tags** table.
  
  - <u>thing_id</u>: forgein key that mtaches the database thing id.___



**Makes**: holds the information for all makes

- <u>make_id</u>: automaticaly created id inside the database

- <u>thingiverse_id</u>: the make id as provided by thingiverse

- <u>thing_id</u>: foregin key for thing id found in Things. the thing it was made from

- <u>user_id</u>: foregin key for user id found in Users. the creator who posted the make

- <u>uploaded</u>: the date and time the make was uploaded in ISO8601 format

- <u>comments</u>: number of comments for the make

- <u>likes</u>: number of likes for the make

- <u>views</u>: number of views the make has

- <u>category</u>: the category to which the thing was posted to by the user

- <u>settings_id</u>: foregin key for print settings found in Print_settings table (can be null if nu print settings were provided)_



**Print Setting**s: holds print settings for things and makes, when provided. Each and all can be nulls.

- <u>printer_brand</u>: the brand of the printer used for printing

- <u>printer_model</u>: the model of the printer used for printing

- <u>rafts</u>: states if rafts were used in printing. can be 1 if yes, 0 if no and -1 if not provided.

- <u>supports</u>: supports if rafts were used in printing. can be 1 if yes, 0 if no and -1 if not provided.

- <u>resolution</u>: the printing resolution used for printing

- <u>infill</u>: the amount of infill used for printing

- <u>filament_brand</u>: the filament brand used for printing (for makes, this also holds the color and material)

- <u>filament_color</u>: the filament color used for printing

- <u>filament_material</u>: the filament material used for printing



## 7. License & Contributing

Created by Konstantin Krivokon and Shlomi Abuchatzera Green.

Creative common usage 2021.
