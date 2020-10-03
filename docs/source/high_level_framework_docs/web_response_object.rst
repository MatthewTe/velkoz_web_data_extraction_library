WebPageResponse Objects
=======================
WebPageResponse are objects that, when initialized, send an HTTP GET request to the specified url via the `python requests library <https://requests.readthedocs.io/en/master/>`_. The WebPageResponse Object stores the data contained in the HTTP Response received from the url. The format in which this Response data is stored is dependent on the object itself.

In the Base WebPageResponse Object there is no parsing of the HTTP response received from the url. The response HTML is converted into bytes and is stored within the parameter **_html_body**. In custom WebPageResponse Objects the HTML response content may be parsed by internal methods and stored in various other internal parameters. WebObjects that are written to extract very specific information typically heavily parse incoming HTML content and only store specific data from said content. Data can either be parsed within the WebResponse Object or within the Data Ingestion Engine. The WebResponse Object, in addition to containing the HTML content, also contains metadata associated with said content such as the **time initialized** for example.


Conceptually the WebPageResponse object is an object that is meant to represent a web page indicated by an input url.

**************************
BaseWebPageResponse Object
**************************
All other WebPageResponse Objects inherit from the BaseWebPageResponse Object. This base class performs basic content extraction of the web page indicated by the url as well as basic metadata.

.. autoclass:: velkoz_web_packages.objects_base.web_objects_base.BaseWebPageResponse
   :show-inheritance:
   :members:
   :private-members:
   :undoc-members:

This base object extracts HTML data from the url in its most basic format. The data is stored as a large byte object and no parsing occurs. Theoretically it is possible to use the BaseWebResponse Object for many complex data extraction purposes and simply perform the necessary parsing within the Ingestion Engine, however it is assumed that the BaseWebResponse Object is used as a Base Object for more complex and specific Web Response Objects that overwrite or extend the basic functionality of the Object.
