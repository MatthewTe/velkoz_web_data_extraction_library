Web Scraping Tools by Category
=======================================
The velkoz library contains various packages for extracting specific data from websites in various custom formats. As such, new WebPageResponse objects and their associated Data Ingestion Engine object are written to extract data with a specific purpose in mind. Below is a list of all custom WebPageResponse Objects and Ingestion Engines sorted by their category/design purpose.

WebPageResponse and Ingestion Engines Objects can be built by extending other, existing custom objects. This can allow very niche and complex object to be written on top of eachother, but it is important to remember that the root node for custom WebPageResponse and Ingestion Engines Objects are the BaseWebPageResponse and BaseWebPageIngestionEngine objects respectively.

.. toctree::
   :maxdepth: 2
   :caption: Velkoz Library Categories:

   finance_categories/finance_objects
