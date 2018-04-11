from hacker_one_importer.reports import HackerOneReports
import pytest
from pytest_mock import mocker
from requests.models import HTTPError

class FakeReport:
    id = 1234
    url = "www.google.com"


def test_set_reference_id_returns_throws_exception():
    report_client = HackerOneReports("identifier", "token", "program")

    with pytest.raises(Exception):
        report_client.set_issue_tracker_reference_id(FakeReport(), 1234)


def test_get_reports_throw_HTTPError():
    report_client = HackerOneReports("identifier", "token", "program")

    with pytest.raises(HTTPError):
        report_client.get_report(1234)
