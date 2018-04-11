import concurrent.futures
import logging
from datetime import datetime

import requests

from hacker_one_importer.config import get_config
from hacker_one_importer.dynamodb import put_last_activity_date, get_last_activity_date
from hacker_one_importer.issues import JiraIssues
from hacker_one_importer.models import get_command
from hacker_one_importer.reports import HackerOneReports

logger = logging.getLogger()

# get configs
config = get_config()

# initiate clients
report_client = HackerOneReports(
    config.H1_API_IDENTIFIER,
    config.TOKEN,
    config.H1_PROGRAM)

jira_client = JiraIssues(
    config.JIRA_SERVER,
    config.USERNAME,
    config.PASSWORD,
    config.JIRA_PROJECT)


def _get_attachment_file_name(attachment):
    """ Attachments in HackerOne will show inline in the report.  We can't do that in jira.
    To map where these images appear in the hackerone report {FXXX} ,where XXX represents the attachmentid, we are
    appending attachment.id + attachment.file_name
    """
    return "%s_%s" % (attachment.id, attachment.file_name)


def _parse_datetime_string(datetime_string):
    return datetime.strptime(''.join(datetime_string.rsplit(':', 1)), "%Y-%m-%dT%H:%M:%S.%f%z")


def import_issues(last_activity_date=None, multithread=True, import_all=False, ignore_dynamodb=False, update_h1=True):
    """

    :type last_activity_date: datetime
    :param last_activity_date: date to pull in reports from h1 where last_activity_date

    :type multithread: bool
    :param multithread: process in parallel vs single threaded

    :type import_all: bool
    :param import_all: import all h1 reports

    :type ignore_dynamodb: bool
    :param ignore_dynamodb: ignore reading and writing to dynamodb
    """
    # get max_last_activity_date from dynamodb
    if last_activity_date is None and not ignore_dynamodb:
        last_activity_date = get_last_activity_date()

    # if we are still none, then this is our first run, or
    if last_activity_date is None or import_all:
        reports = report_client.get_reports()
        max_last_activity_date = config.MIN_START_DATETIME
    else:
        reports = report_client.get_reports_activity_since_x_datetime(last_activity_date)
        max_last_activity_date = _parse_datetime_string(last_activity_date)

    logger.info("%s reports to process" % len(reports))

    if multithread:
        logging.debug("starting concurrency processing")

        with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_WORKER) as executor:
            # Start the load operations and mark each future with its URL
            futures = {executor.submit(import_issue, report.id, last_activity_date, update_h1): report.id for report in reports}

            # wait for all the reports for finish
            concurrent.futures.wait(futures)

            # we want to get the max last activity from the original report object vs the direct lookup done in import
            # issues
            for report in reports:
                max_last_activity_date = max(max_last_activity_date, report.last_activity_at)
    else:
        for report in reports:
            import_issue(report.id, last_activity_date, update_h1)
            max_last_activity_date = max(max_last_activity_date, report.last_activity_at)

    logger.info("Max Last_Activity_Date: %s" % max_last_activity_date)

    # write max_last_activity_date to dynamodb
    if not ignore_dynamodb:
        put_last_activity_date(max_last_activity_date)


def import_issue(report_id, last_activity_date=None, update_h1=False):
    # get the detailed report object taht includes attachments & activities
    report = report_client.get_report(report_id)

    logger.info("Processing ReportID: %s State: %s LastActivityDate: %s JiraId: %s" %
                (report.id, report.state, report.last_activity_at, report.issue_tracker_reference_id))

    # create jira_issues
    create_new_issue, jira = create_jira_issue(report, update_h1=update_h1)

    # add_attachments
    add_attachments(report, jira)

    # add remote_link
    jira_client.add_remote_link(report, jira)

    # add_comments
    add_comments(report, jira, last_activity_date)


def create_jira_issue(report, check_if_report_exists=True, update_h1=True):
    """
    Create a jira issue only if one doesn't exist:
         either based on hacker one issue_tracker_reference_id is empty
         or jira jql search for H1 ReportID
    :type report: h1.models.Report
    :param report: H1 Report
    :type check_if_report_exists boolean
    :param check_if_report_exists: Toggle to prevent duplicate report creation in jira
    :returns: report_created, Jira
    :rtype bool, jira.Jira
    """

    if check_if_report_exists:
        # check if H1 thinks we have a report in Jira
        if report.issue_tracker_reference_id is not None:
            # verify hackerone report is in jira
            jira = jira_client.get_jira_issue(report)

            if jira is not None:
                logger.debug("Jira Issue Exists: %s" % jira.id)
                # if this is an existing jira issue, we need to check if we need to update any existing jira fields
                jira_client.update_jira_issue(report, jira)
                return False, jira
        else:
            # check if jira thinks we have h1 report
            jira = jira_client.search_for_report(report.id)
            if jira:
                logger.debug("Jira Issue Found: %s" % jira[0].id)
                return False, jira[0]

    jira = jira_client.create_jira_issue(report)
    logger.debug("Created New Jira Issue: %s" % jira.id)

    if update_h1:
        report_client.set_issue_tracker_reference_id(report, jira)
        logger.debug("Updated Issue Tracker Reference in H1")

    return True, jira


def add_attachments(report, jira, override=False):
    """Only add attachments if the jira issue doesn't already have an attachment with the same filename"""

    for attachment in report.attachments:
        filename = _get_attachment_file_name(attachment)

        if not override \
                and any(file.filename == _get_attachment_file_name(attachment) for file in jira.fields.attachment):
            logger.info("Attachment: %s already exists" % filename)
        else:
            logger.info("Adding attachment: %s to Jira: %s" % (filename, jira.id))
            r = requests.get(attachment.expiring_url)
            jira_client.add_jira_attachment(jira, r.content, filename)


def add_comments(report, jira, last_activity_date):
    # Get all the jira comments we've created
    logger.info("%s Adding Comments" % report.id)
    import_comments = [comment.body for comment in jira.fields.comment.comments
                       if comment.author.name == config.USERNAME]

    # By default activities are sorted newest to oldest, which is not the way we want to have them in jira
    report.activities.sort(key=lambda x: x.updated_at)

    for activity in report.activities:
        comment = get_command(activity).get_message()

        if last_activity_date is None or activity.created_at > last_activity_date:
            # don't write h1 comments already in jira
            if comment not in import_comments:
                jira_client.create_comments(jira, comment)

        # add attachment if missing
        if activity.attachments:
            add_attachments(activity, jira)
