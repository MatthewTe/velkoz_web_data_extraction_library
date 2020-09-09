# Importing testing frameworks:
import unittest

# Importing 3rd party packages:
import bs4

# Importing Base Objects for testing:
from velkoz_web_packages.objects_base.web_objects_base import BaseWebPageResponse
from velkoz_web_packages.objects_base.ingestion_engines_base import BaseWebPageIngestionEngine

class BaseWebPageResponseTest(unittest.TestCase):

    # Method that tests the Base WebPageResponseObj requests.get:
    def test_base_web_object_response_obj(self):
        """
        The UnitTest Method that tests the BaseWebPageResponse.___http_response
        paramer.

        Tests the requests.get response object when a url is passed into the
        BaseWebPageResponse() object. The test asserts that the response from
        the GET request is an integer (requests.get.status_code). It is not
        concerned with the status of the response (200, 404, etc.). The test only
        assers if a response was recieved, meaning the GET request was sent out correctly.

        Note: The status code is assumed to be 200 due to the url's used being
            very concistent. As such an IsEqual value is asserted in addition to
            an integer type check.

        """
        # Declaring a list of known active urls:
        active_urls = [
            'https://www.google.com/',
            'https://stackoverflow.com/',
            'https://www.bing.com/',
            'https://www.wikipedia.org/'
        ]

        # Passing known active urls into BaseWebPageResponse objects:
        web_objects = [
            BaseWebPageResponse(url)._http_response.status_code for url in active_urls
            ]

        # Iterating through the list of Web Objects Status Codes and asserting 200:
        assert_equal_lst = [
            self.assertEqual(status_code, 200) for status_code in web_objects
        ]

        # Iterating through the list of web objects testing for integer type:
        assert_type_lst = [
            self.assertIs(type(status_code), int) for status_code in web_objects
        ]

    # Method that tests the Base WebPageResponseObj's BeautifulSoup conctent:
    def test_base_web_object_bs4(self):
        """
        The UnitTest Method performs a test for sucessful extraction of a Bs4
        object.

        The method initializes a series of BaseWebPageResponse objects with
        reliable urls. It then performs an Assertion Test on the ._html_body
        parameter, testing if the extracted data was a BeautifulSoup object. Once
        again the content is not being parsed, just the data type.

        """
        # Declaring a list of known active urls:
        active_urls = [
            'https://www.google.com/',
            'https://stackoverflow.com/',
            'https://www.bing.com/',
            'https://www.wikipedia.org/'
        ]

        # Passing active urls into the BaseWebPageResponse objects:
        web_objects_html_body_lst = [BaseWebPageResponse(url)._html_body for url in active_urls]

        # Performing type testing for the html body of the BaseWebPageResponse:
        html_body_type_assertion = [

            self.assertIsInstance(html_body_obj, bs4.BeautifulSoup) for
            html_body_obj in web_objects_html_body_lst
        ]
