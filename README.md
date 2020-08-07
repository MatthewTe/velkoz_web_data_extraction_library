# velkoz Web Data Extraction Library
A series of APIs for extracting data from various websites either directly through supported API endpoints where possible or through web-scraping where APIs are not available.

## Table of Contents
* ### [Instillation Instructions](placeholder)
* ### [Web Objects](placeholder)


## Web Objects
The library is built out of web objects. These objects are essentially abstraction layers around the requests and BeautifulSoup methods that are traditionally used to extract data via the web in python. All web objects inherit from the base object `BaseWebResponse`. The DAG below shows the relationships between all web objects:
[!IMAGE NOT FOUND](placeholder)


### `BaseWebResponse`
This is the core of all web scraping objects/methods in the library. It is an abstraction layer around two core external methods: `requests.Response` and `BeautifulSoup`.
