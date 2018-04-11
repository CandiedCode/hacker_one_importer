from h1.models import hydrate_object
import hacker_one_importer.models as h1_model
from . import load_resource_blob
from datetime import datetime
import pytest


def test_report_hydration():
    report = hydrate_object(load_resource_blob("report_322474"))
    assert report.id == '322474'
    assert report.title == "Backup SQL file lingering on https://ops.playtronics.com/"
    assert report.created_at == datetime.strptime("2018-03-05T16:17:42.998 +0000", '%Y-%m-%dT%H:%M:%S.%f %z')


def test_report_severity():
    report = hydrate_object(load_resource_blob("report_322474"))
    h1_model.add_attributes_to_report(report)
    assert report.severity.rating == 'critical'
    assert report.severity.score == 10


def test_report_weakness():
    report = hydrate_object(load_resource_blob("report_322474"))
    h1_model.add_attributes_to_report(report)
    assert report.weakness.name == "Information Disclosure"


def test_report_structured_scope():
    report = hydrate_object(load_resource_blob("report_322474"))
    h1_model.add_attributes_to_report(report)
    assert report.structured_scope.asset_type == "APPLE_STORE_APP_ID"
    assert report.structured_scope.asset_identifier == "com.playtronics.PlayTronicsStore"


def test_report_cve_activity():
    report = hydrate_object(load_resource_blob("report_322474"))
    assert any(activity.TYPE == "activity-cve-id-added" for activity in report.activities)


@pytest.mark.parametrize("messageclass, message",
                         [(h1_model.ActivityPublicAgreementMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ agreed on going public
{quote}Agreed On Going Public!{quote}
"""),
                          (h1_model.ActivityBountyAwardedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_security_ awarded bounty
{quote}Bounty Awarded!{quote}
"""),
                          (h1_model.ActivityBountySuggestedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ suggested bounty
{quote}Bounty Suggested!{quote}
"""),
                          (h1_model.ActivityBugClonedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ cloned bug - 1336
{quote}Bug Cloned!{quote}
"""),
                          (h1_model.ActivityBugDuplicateMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked bug as duplicated - 1336
{quote}Bug Duplicate!{quote}
"""),
                          (h1_model.ActivityBugInformativeMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked bug as informative
{quote}Bug Informative!{quote}
"""),
                          (h1_model.ActivityBugNeedsMoreInformationMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ requested more information
{quote}Bug Needs More Info!{quote}
"""),
                          (h1_model.ActivityBugNewMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ changed state to new
{quote}Bug New!{quote}
"""),
                          (h1_model.ActivityBugNotApplicableMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked bug as not applicable
{quote}Bug Not Applicable!{quote}
"""),
                          (h1_model.ActivityBugReopenedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ reopened bug
"""),
                          (h1_model.ActivityBugResolvedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked bug as resolved
{quote}Bug Resolved!{quote}
"""),
                          (h1_model.ActivityBugSpamMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked bug as spam
{quote}Bug Spam!{quote}
"""),
                          (h1_model.ActivityBugTriagedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked bug as triaged
{quote}Bug Triaged!{quote}
"""),
                          (h1_model.ActivityChangedScopeMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ changed structured scope
{quote}A different scope has added{quote}
"""),
                          (h1_model.ActivityCommentMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ added a comment
{quote}Comment!{quote}
"""),
                          (h1_model.ActivityCommentsClosedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ closed comments
{quote}Comments Closed!{quote}
"""),
                          (h1_model.ActivityExternalInvitationCancelledMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ cancelled invitation for hacker@example.com
{quote}External User Invitation Cancelled!{quote}
"""),
                          (h1_model.ActivityExternalInvitationInvitedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ invited hacker@example.com
{quote}External User Invited!{quote}
"""),
                          (h1_model.ActivityExternalUserJoinedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ user joined.  Duplicate Report: 10
{quote}External User Joined!{quote}
"""),
                          (h1_model.ActivityExternalUserRemovedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ removed user _API Example_
{quote}External User Removed!{quote}
"""),
                          (h1_model.ActivityGroupAssignedToBugMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ assigned group: _Admin_
{quote}Group Assigned To Bug!{quote}
"""),
                          (h1_model.ActivityGroupAssignedToBugMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ assigned group: _Admin_
{quote}Group Assigned To Bug!{quote}
"""),
                          (h1_model.ActivityHackerRequestedMediationMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ requested mediation
{quote}Hacker Requested Mediation!{quote}
"""),
                          (h1_model.ActivityManuallyDisclosedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ manually disclosed
{quote}Manually Disclosed!{quote}
"""),
                          (h1_model.ActivityMediationRequestedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ requested mediation
{quote}Mediation Requested!{quote}
"""),
                          (h1_model.ActivityNotEligibleForBountyMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ marked not eligible for bounty
{quote}Not Eligible For Bounty!{quote}
"""),
                          (h1_model.ActivityReferenceIDAddedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_api-example_ added reference id - reference
{quote}Reference Id Added!{quote}
"""),
                          (h1_model.ActivityReportBecamePublicMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
report became public
{quote}Report Became Public!{quote}
"""),
                          (h1_model.ActivityTitleUpdatedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ updated report title
{quote}Report Title Updated!{quote}
"""),
                          (h1_model.ActivityReportVulnerabilityTypesMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ updated vulnerability types
{quote}Report Vulnerability Types Updated!{quote}
"""),
                          (h1_model.ActivityReportSeverityUpdatedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ updated report severity
{quote}Report Severity Updated!{quote}
"""),
                          (h1_model.ActivitySwagAwardedsMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: False
_API Example_ awarded swag
{quote}Swag Awarded!{quote}
"""),
                          (h1_model.ActivityUserAssignedMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ assigned user - _Other User_
{quote}User Assigned To Bug!{quote}
"""),
                          (h1_model.ActivityUserBannedFromProgramMessage, """1337 - 2016-02-02 04:05:06+00:00:
Internal: True
_API Example_ banned user - _API Example_
{quote}User Banned From Program!{quote}
"""),
                          (h1_model.ActivityCVEIDAddedMessage, """2507463 - 2018-03-19 20:25:11.847000+00:00:
Internal: False
_Jennifer Cwagenberg_ added CVE-ID
"""),

                          ])
def test_activity_message(messageclass, message):
    activity = hydrate_object(load_resource_blob(messageclass.TYPE))
    activity_message = messageclass(activity)
    assert activity_message.get_message() == message
