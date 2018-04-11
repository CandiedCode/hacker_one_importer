import datetime as dt
import logging

from h1.client import HackerOneClient
from h1.models import Report

from hacker_one_importer.models import add_attributes_to_report

logger = logging.getLogger()


class HackerOneReports:
    def __init__(self, identifier, token, program):
        """Inits hacker_one_client.  This requires that an API Token has been created via
           https://hackerone.com/{program}/api.

           The api token needs to be apart of the "standard" group to be able to have appropriate permissions
           to be able to change report state, post comments, ect..

        :type identifier: string
        :param identifier: api token identifier

        :type token: string
        :param token: token

        :type program: string
        :param program: HackerOne report
        """
        self.__identifier = identifier
        self.__token = token
        self.__program = program
        self._init_hacker_one_client()

    def _init_hacker_one_client(self):
        self.client = HackerOneClient(self.__identifier, self.__token)
        self.client.REQUEST_HEADERS['Content-Type'] = 'application/json'
        self.client.s.headers.update(self.client.REQUEST_HEADERS)

    def get_reports_activity_x_days_ago(self, days=30):
        """Get Reports that have a last_activity_date > days

        :type days: int
        :param days: represents the days ago

        :returns: returns list of HackerOne Report objects
        """
        day_ago = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
        logging.info("Checking for Reports since: " + str(day_ago))

        return self.client.find_resources(Report, program=[self.program], last_activity_at__gt=day_ago)

    def get_reports_activity_since_x_datetime(self, datetime):
        """Get Reports that have a last_activity_date > date

        :type datetime: datetime
        :param datetime: represents the days ago
        :return: returns list of HackerOne Report objects
        """
        logging.info("Checking for Reports since: " + str(datetime))

        return self.client.find_resources(Report, program=[self.__program], last_activity_at__gt=datetime)

    def get_new_reports(self):
        """
        Pull list of HackerOne Reports in NEW state
        :return: returns list of HackerOne Report objects
        """
        logging.info("Checking for new Reports")
        return self.client.find_resources(Report, program=[self.program], state=["new"])

    def get_reports(self):
        """
        Return all reports in a program
        :return: returns list of HackerOne Report objects
        """
        logging.info("Getting All Reports")
        return self.client.find_resources(Report, program=[self.__program])

    def get_report(self, report_id):
        """
        Pulls individual report object.  This Report object will have more details vs a report object
        returned from filter query (ie get_new_reports, or get_reports_activity_x_days_ago).  This report object
        will include activities, and attachments to name a few

        :type report_id: int
        :param report_id:
        :return:
        """
        logging.debug("Checking Report: %s" % report_id)
        report = self.client.get_resource(Report, report_id)

        # uber's hacker one client does not set weakness and severity on the h1.models.report object
        # so well add it afterwards
        add_attributes_to_report(report)

        return report

    def set_issue_tracker_reference_id(self, report, jira_id):
        """Set Issue Tracker Reference ID field in Jira Report.  issue_tracker_reference_id is how we map hackerOne
        reportID to Jira Issue ID

        :type report: h1.models.Report
        :param report: HackerOne Report Object

        :type jira_id: string
        :param jira_id: Jira Issue ID
        :return: returns http response
        """

        json = '''
{
  "data": {
    "type": "issue-tracker-reference-id",
    "attributes": {
      "reference": "%s"
    }
  }
}''' % jira_id

        result = self.client.make_request(report.url + "/issue_tracker_reference_id",
                                          data=json,
                                          params=None,
                                          method="POST")

        # wait for the request to complete, if it hasn't already
        response = result.result()

        if response.status_code != 200:
            logger.error("failed updating issue-tracker-reference-id")
            raise Exception('Error updating ReportID: %s to JiraID: %s - %s\n%s' %
                            (report.id, jira_id, response.status_code, response.reason))
        else:
            logger.debug("Updating HackerOne Report: %s to include %s Jira Reference ID" % (report.id, jira_id))
