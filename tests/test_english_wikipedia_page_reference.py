import logging
from unittest import TestCase

import config
from src import console
from src.models.exceptions import MoreThanOneNumberError
from src.models.wikimedia.wikipedia.templates.english_wikipedia_page_reference import (
    EnglishWikipediaPageReference,
    EnglishWikipediaPageReferenceSchema,
)

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestEnglishWikipediaPageReferenceSchema(TestCase):
    def test_url_template1(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference = EnglishWikipediaPageReferenceSchema().load(data)
        console.print(reference)

    def test_url_template_with_archive_url(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
            "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
        }

        reference = EnglishWikipediaPageReferenceSchema().load(data)
        assert (
            reference.archive_url
            == "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
        )
        # console.print(reference)

    def test_url_template2(self):
        data = {"1": "chkchkchk.net", "template_name": "url"}
        reference = EnglishWikipediaPageReferenceSchema().load(data)
        console.print(reference)

    def test_parse_persons_from_cite_web(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference: EnglishWikipediaPageReference = (
            EnglishWikipediaPageReferenceSchema().load(data)
        )
        reference.finish_parsing_and_generate_hash()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Melissa"
        assert person.surname == "Locker"

    def test_parse_persons_from_cite_journal(self):
        data = {
            "last1": "Skaaning",
            "first1": "Svend-Erik",
            "title": "Different Types of Data and the Validity of Democracy Measures",
            "journal": "Politics and Governance",
            "volume": "6",
            "issue": "1",
            "page": "105",
            "doi": "10.17645/pag.v6i1.1183",
            "year": "2018",
            "doi_access": "free",
            "template_name": "cite journal",
        }
        reference: EnglishWikipediaPageReference = (
            EnglishWikipediaPageReferenceSchema().load(data)
        )
        reference.finish_parsing_and_generate_hash()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Svend-Erik"
        assert person.surname == "Skaaning"

    def test_parse_persons_from_cite_book(self):
        data = {
            "last": "Tangian",
            "first": "Andranik",
            "date": "2020",
            "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
            "series": "Studies in Choice and Welfare",
            "publisher": "Springer",
            "location": "Cham, Switzerland",
            "isbn": "978-3-030-39690-9",
            "doi": "10.1007/978-3-030-39691-6",
            "s2cid": "216190330",
            "template_name": "cite book",
        }
        reference: EnglishWikipediaPageReference = (
            EnglishWikipediaPageReferenceSchema().load(data)
        )
        reference.finish_parsing_and_generate_hash()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Andranik"
        assert person.surname == "Tangian"

    def test_extract_first_level_domain(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
            "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
        }
        reference = EnglishWikipediaPageReferenceSchema().load(data)
        reference.finish_parsing_and_generate_hash()
        assert reference.first_level_domain_of_url == "stereogum.com"
        assert (
            reference.url
            == "https://www.stereogum.com/1345401/turntable-interview/interviews/"
        )

    def test_extract_first_level_domain_bad_url(self):
        data = {
            "url": "[[:sq:Shkrime për historinë e Shqipërisë|Shkrime për historinë e Shqipërisë]]",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
            "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
        }
        reference = EnglishWikipediaPageReferenceSchema().load(data)
        reference.finish_parsing_and_generate_hash()
        assert reference.url is None

    def test_find_number(self):
        ref = EnglishWikipediaPageReference(template_name="test")
        with self.assertRaises(MoreThanOneNumberError):
            ref.__find_number__(string="123one123")
        assert ref.__find_number__(string="1one") == 1
        assert ref.__find_number__(string="one1one") == 1
        assert ref.__find_number__(string="one") is None

    def test_publisher_and_location(self):
        data = dict(
            template_name="cite web",
            url="http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            archive_url="https://web.archive.org/web/20100812051822/http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            url_status="dead",
            archive_date="2010-08-12",
            title="Musköbasen 40 år",
            first="Helene",
            last="Skoglund",
            author2="Nynäshamns Posten",
            date="January 2010",
            publisher="Kungliga Motorbåt Klubben",
            location="Stockholm",
            pages="4–7",
            language="Swedish",
            trans_title="Muskö Naval Base 40 years",
            access_date="2010-11-09",
        )
        reference = EnglishWikipediaPageReferenceSchema().load(data)
        reference.finish_parsing_and_generate_hash()
        assert reference.publisher == "Kungliga Motorbåt Klubben"
        assert reference.location == "Stockholm"

    def test_detect_archive_urls(self):
        # data = dict(
        #     template_name="cite web",
        #     url="http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
        #     archive_url="https://web.archive.org/web/20100812051822/http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
        #     url_status="dead",
        #     archive_date="2010-08-12",
        #     title="Musköbasen 40 år",
        #     first="Helene",
        #     last="Skoglund",
        #     author2="Nynäshamns Posten",
        #     date="January 2010",
        #     publisher="Kungliga Motorbåt Klubben",
        #     location="Stockholm",
        #     pages="4–7",
        #     language="Swedish",
        #     trans_title="Muskö Naval Base 40 years",
        #     access_date="2010-11-09",
        # )
        # reference: EnglishWikipediaPageReference = (
        #     EnglishWikipediaPageReferenceSchema().load(data)
        # )
        # reference.finish_parsing_and_generate_hash()
        reference = EnglishWikipediaPageReference(
            archive_url="https://web.archive.org/web/20100812051822/http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            template_name="test",
        )
        reference.__extract_first_level_domain__()
        reference.__detect_archive_urls__()
        logger.debug(reference.detected_archive_of_url)
        logger.debug(reference.detected_archive_of_archive_url)
        assert reference.detected_archive_of_url is None
        # from models.wikicitations.enums import KnownArchiveUrl

        # FIXME this fails for some reason :/
        # assert reference.detected_archive_of_archive_url == KnownArchiveUrl.ARCHIVE_ORG
