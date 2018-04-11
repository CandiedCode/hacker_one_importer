import json
import logging

from jira import JIRA, JIRAError

logger = logging.getLogger()


def time_format(dt):
    return "%s:%.3f%s" % (
        dt.strftime('%Y-%m-%dT%H:%M'),
        float("%.3f" % (dt.second + dt.microsecond / 1e6)),
        dt.strftime('%z')
    )


class JiraIssues(object):
    APPLICATION = {
        "type": "www.hackerone.comr",
        "name": "Hacker One"
    }

    SCOPE = '''
h4.Scope
----
asset type: %(type)s
asset identifier: %(identifier)s\n'''

    DESCRIPTION = '''
h4.Report Info
----
Report State: %(state)s
Reporter: %(reporter)s
Assignee: %(assignee)s
Report Created: %(created)s
Report Last Activity: %(last_activity)s

h4.Weakness
----
name: %(name)s
description: %(w_description)s
id: %(id)s

h4.Severity
----
rating: %(rating)s
score: %(score)s'

h4.Description
----
%(description)s
'''

    def __init__(self, server, username, password, project):
        """Inits jira client.  This current setup requires a jira username to be setup with the appropriate
        permissions in the jira project

        :type server: string
        :param server: jira url

        :type username: string
        :param username: token

        :type password: string
        :param password: jira username password

        :type project: string
        :param project: jira project
        """
        self.__jira_server = server
        self.__username = username
        self.__password = password
        self.jira_project = project
        self._init_jira_client()

    def _init_jira_client(self):
        options = {'server': self.__jira_server}

        def create_custom_field(fields=None):
            url = self._get_url('field')
            r = self._session.post(url, data=json.dumps(fields))

            if r.status_code != 201:
                raise JIRAError(r.status_code, request=r)

            return r

        # Jira library doesn't have method for creating custom fields
        setattr(JIRA, 'create_custom_field', create_custom_field)

        self.jira_client = JIRA(options, basic_auth=(self.__username, self.__password))

    def get_jira_projects(self):
        return self.jira_client.projects()

    def create_project(self, key, name, jira_type="Software"):
        return self.jira_client.create_project(key, name, jira_type)

    def get_jira_issue(self, report):
        """
        Return Jira Issue based on HackerOne Report issue_tracker_reference_id

        :type report: h1.models.Report
        :param report: hackerone report
        :return: Jira Issue
        """
        try:
            return self.jira_client.issue(report.issue_tracker_reference_id)
        except JIRAError as e:
            if e.text == "Issue Does Not Exist":
                return None
            else:
                raise

    @staticmethod
    def _get_jira_summary(report):
        return "%s - %s" % (report.id, report.title)

    def _get_jira_description(self, report):
        return self.DESCRIPTION % {
                                    'description': report.vulnerability_information,
                                    'reporter': report.reporter.name,
                                    'assignee': report.assignee.name if report.assignee is not None else "",
                                    'state': report.state,
                                    'created': report.created_at,
                                    'last_activity': report.last_activity_at,
                                    'name': report.weakness.name,
                                    'w_description': report.weakness.description,
                                    'id': report.weakness.external_id,
                                    'rating': report.severity.rating,
                                    'score': report.severity.score
                                  }

    def create_jira_issue(self, report):
        """
        Create Jira Issue
        https://developer.atlassian.com/server/jira/platform/jira-rest-api-example-create-issue-7897248/

        :type report: h1.models.Report
        :param report: hackerone report

        :type :return: string
        :return: Jira ID
        """
        issue_dict = {
            'project': {'key': self.jira_project},
            'summary': self._get_jira_summary(report),
            'description': self._get_jira_description(report),
            'issuetype': {'name': 'Bug'},
            'labels': ['hackerOne']
        }

        return self.jira_client.create_issue(fields=issue_dict, prefetch=True)

    def update_jira_issue(self, report, jira):
        fields = {}

        summary = self._get_jira_summary(report)

        if jira.fields.summary != summary:
            fields['summary'] = summary

        description = self._get_jira_description(report)

        if jira.fields.description != description:
            fields['description'] = description

        if fields:
            logging.info("Updating Existing Jira Issue: %s" % fields.keys())
            jira.update(fields=fields)

    def search_for_jira_issues(self, report_id):
        """
        Perform a Jira query search using JQL
        :param report_id: hacker one report id
        :return: returns jira issue match
        """
        return self.jira_client.search_issues('''project = %s AND summary ~ "%s"''' %
                                              (self.jira_project, report_id),
                                              maxResults=1)

    def get_fields(self):
        return self.jira_client.fields()

    def create_custom_field(self, fields):
        return self.jira_client.create_custom_field(fields)

    def get_remote_links(self, jira):
        return self.jira_client.remote_links(jira)

    def add_remote_link(self, report, jira, relationship="Relates"):
        links = set()

        # note all rmeote links have to have a global id
        for link in self.get_remote_links(jira):
            if hasattr(link, 'globalId'):
                links.add(link.globalId)

        if report.id not in links:
            destination = {'url': report.html_url, 'title': report.title}
            return self.jira_client.add_remote_link(jira, destination, report.id, self.APPLICATION, relationship)

    def add_simple_link(self, report, jira):
        """https://developer.atlassian.com/server/jira/platform/jira-rest-api-for-remote-issue-links/"""
        link = {'url': report.html_url, 'title': report.title}

        return self.jira_client.add_simple_link(jira, object=link)

    def add_jira_attachment(self, jira, attachment, filename):
        """Add H1 Attachment in Jira

        :param jira: Jira object that has attachments
        :param attachment: hacker one attachment object content
        :param filename: attachment file name
        :return: return
        """
        return self.jira_client.add_attachment(issue=jira.id, attachment=attachment, filename=filename)

    def create_comments(self, jira, comment):
        return self.jira_client.add_comment(jira, comment)
