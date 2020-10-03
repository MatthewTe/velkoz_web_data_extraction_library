Data Ingestion Engine Objects
=============================
The IngestionEngine Object is initialized by configuration parameters that point it to the database it is to connect to as well as how it is supposed to ingest WebObjects. The actual parameters required to initialize the object vary based on the Ingestion Engine being used however they will always involve a database URI. The traditional Ingestion Engine object connects to the specified database by creating a SQLAlchemy engine object and database session, which is used to create a que of database actions and allows these writes to be controlled incrementally.

Once an Ingestion Engine object is initialized, WebResponse Objects can be passed into it as arguments and are stored in a list. This list of WebResponse arguments is at the center of all Ingestion Engine operations. The Ingestion Engine contains methods to add WebResponse Objects after it has been initialized as well as purge the list of existing WebResponse Objects. These methods exist because unlike WebResponse Objects, which are initialized, passed into another method and then removed, Ingestion Engine objects are designed for long term operation. They serve as a fixed point within a data pipeline as other objects are initialized and removed around them.

Here is an example of the BaseDataIngestionEngine being used in a data pipeline:

.. code-block:: python

  # Example of various BaseWebResponse Objects to be written to the database:
  google = BaseWebPageResponse('https://www.google.com/')
  stack_overflow = BaseWebPageResponse('https://stackoverflow.com/')
  bing = BaseWebPageResponse('https://www.bing.com/')
  wikipedia = BaseWebPageResponse('https://www.wikipedia.org/')

  # Creating a data ingestion engine connected to an in-memory sqlite database:
  Example_Engine = BaseWebPageIngestionEngine("sqlite:///:memory:", google, stack_overflow)

  # Example of adding web objects to the Ingestion Engine that has already been initialized:
  Example_Engine._insert_web_obj(bing)
  Example_Engine._insert_web_obj(wikipedia)

  # Writing all data stored in the Ingestion Engine to the database:
  Example_Engine._write_web_objects()



Importantly, **almost all WebResponse Objects have their own associated Data Ingestion Engine.** Most WebPageResponse Objects are designed to extract specific data from a url. This means that data extracted via said custom Objects needs to be written to databases in a very specific manner with a very specific schema. This means that Data Ingestion Engines and WebPageResponse Objects are typically written in tandem. Due to the fact that all WebPageResponse and Data Ingestion Objects inherit from a base classes that were written to interact their may be some intercompatibility between WebPageResponse Objects and Ingestion Engines that were not designed to however this will most likely create conflicts within database schema and should be avoided.
When designing custom Data Ingestion Engines it is crucial that they perform custom validation on every WebPageResponse Object passed into it in order to confirm that it is a supported WebPageResponse Object type.

**********************************
BaseWebPageIngestionEngine Object
**********************************
Every custom Data Ingestion Engine inherits, at least at base level, from the BaseWebPageIngestionEngine Class:

The BaseWebPageIngestionEngine Object contains several internal methods that are crucial for its operation. When extending the Ingestion Engine object, the methods that perform these operations should be extended or overwritten depending on the needs of the extended Ingestion Engine.

The functionality that should be preserved is:

* The ability to modify the list of WebPageResponse Objects (remove, add, clear). --> **_insert_web_obj(), _purge_web_obj_que()**
* The ability to validate all objects that are passed into the Ingestion Engine to ensure type consistency (or any other form of validation necessary). --> **_validate_args()**
* The ability to write data from ingested WebPageResponse Objects to the connected database. --> **_write_web_objects**

The methods that perform this functionality are described below within the Data Ingestion Engine Documentation:

.. autoclass:: velkoz_web_packages.objects_base.ingestion_engines_base.BaseWebPageIngestionEngine
   :members:
   :private-members:
   :undoc-members:
