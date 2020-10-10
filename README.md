# All the Headlines

Gathering all the headlines from around the world.

## Scraper

Scrape the top headline of newspapers from around the world when `main.py` script is executed
and write the results as a CSV file. 
The CSV file is also uploaded to Google Cloud Storage to be consumed by the web app.
New newspapers are added by setting up the config file [config.yaml](config.yaml).

### Methodology

* For each country, a quick google search on which English newspaper has the highest circulation count.
  This is usually a wikipedia result.
* For countries where English is not the native language, this will not reflect the newspaper with
  the highest circulation. In future the headline should be translated.
* The "top headline" is considered the article that appears in the most upper lefthand corner
  of the webpage when it is opened. 

### Current list of countries

* United Kingdom
* Hong Kong
* Singapore
* ~United States~
* Australia
* South Africa
* ~Nigeria~
* Brazil
* Russia
* Qatar (Al-Jazeera)


### Scraping

The scraper is deployed as a Google Cloud Function triggered by HTTP.
This is defined in `main.py` with the entrypoint `scrape`, and can be tested locally by invoking `python main.py`.

### To do list

* add refresh button to page that scrapes data
* Add cloud function to scrape data daily
* How to best to store data 
  - decide on a schema and move to big query
* integrate Cloud Logging
* save a copy of the web page if failed to find headline
* use smart_open to write directly to gcs 
  - cloud function is read-only, so cannot write a local file and then upload


### Useful links

Setting up Jupyter on GCP
https://tudip.com/blog-post/run-jupyter-notebook-on-google-cloud-platform/

Start here:
http://jonathansoma.com/lede/foundations-2017/classes/adv-scraping/scraping-bbc/

## App

[app](app)
Run a web app to display the results.

