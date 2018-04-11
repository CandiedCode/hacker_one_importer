import six
from h1.models import ActivityBase

_type_commands = {}


# These are models missing from h1 library
# Weakness/Severity/StructureScope are all objects on the report object
# ActivityCVEIDAdded is an activity that doesn't show up in the hacker one api documentation, thus will blow up this app
# if we run across one, thus we need a class defined for it
def _get_attributes(relationship, key):
    data = relationship.get(key, None)

    if data is not None:
        return data['data']['attributes']

    return None


def add_attributes_to_report(report):
    relationship = report.raw_data["relationships"]

    weakness = Weakness(relationship)
    severity = Severity(relationship)
    scope = StructuredScope(relationship)

    setattr(report, 'weakness', weakness)
    setattr(report, 'severity', severity)
    setattr(report, 'structured_scope', scope)


class Weakness:
    TYPE = "weakness"

    def __init__(self, relationship):
        self._raw_data = _get_attributes(relationship, self.TYPE)

        if self._raw_data is not None:
            self.name = self._raw_data.get('name')
            self.description = self._raw_data.get('description')
            self.external_id = self._raw_data.get('external_id')
        else:
            self.name = None
            self.description = None
            self.external_id = None


class Severity:
    TYPE = "severity"

    def __init__(self, relationship):
        self._raw_data = _get_attributes(relationship, self.TYPE)

        if self._raw_data is not None:
            self.rating = self._raw_data.get('rating')
            self.score = self._raw_data.get('score')
        else:
            self.rating = None
            self.score = None


class StructuredScope:
    TYPE = "structured_scope"

    def __init__(self, relationship):
        self._raw_data = _get_attributes(relationship, self.TYPE)

        if self._raw_data is not None:
            self.asset_type = self._raw_data.get('asset_type')
            self.asset_identifier = self._raw_data.get('asset_identifier')
        else:
            self.asset_type = None
            self.asset_identifier = None


# this is missing from Uber HackerOne Library
class ActivityCVEIDAdded(ActivityBase):
    TYPE = "activity-cve-id-added"


class ActivityChangedScope(ActivityBase):
    TYPE = "activity-changed-scope"


def get_command(activity):
    if activity is None:
        return None
    command = _type_commands.get(activity.TYPE, None)
    if not callable(command):
        raise Exception("Can't hydrate a %s!")
    return command(activity)


class _CommandRegistrant(type):
    def __init__(cls, name, bases, nmspc):
        super(_CommandRegistrant, cls).__init__(name, bases, nmspc)
        h1_type = getattr(cls, "TYPE", None)
        if h1_type:
            _type_commands[h1_type] = cls


@six.add_metaclass(_CommandRegistrant)
class ActivityBaseMessage(object):
    MSG_TEMPLATE = '''%(id)s - %(created)s:
Internal: %(internal)s
%(message)s
'''

    COMMENT_MSG_TEMPLATE = '''%(id)s - %(created)s:
Internal: %(internal)s
%(message)s
{quote}%(comment)s{quote}
'''

    def __init__(self, activity):
        self._activity = activity

    def _get_concatenated_message(self, message):
        if self._activity.message:
            return self.COMMENT_MSG_TEMPLATE % {
                'id': self._activity.id,
                'created': str(self._activity.created_at),
                'internal': self._activity.internal,
                'message': message,
                'comment': self._activity.message
            }
        else:
            return self.MSG_TEMPLATE % {
                'id': self._activity.id,
                'created': str(self._activity.created_at),
                'internal': self._activity.internal,
                'message': message
            }

    def get_message(self):
        return self._get_concatenated_message(self.CUSTOM_MSG_TEMPLATE % self._activity.actor.name)

    def perform_action(self, jira_client, report_client, jira, report):
        pass


class ActivityPublicAgreementMessage(ActivityBaseMessage):
    TYPE = "activity-agreed-on-going-public"
    CUSTOM_MSG_TEMPLATE = '''_%s_ agreed on going public'''


class ActivityBountyAwardedMessage(ActivityBaseMessage):
    TYPE = "activity-bounty-awarded"
    CUSTOM_MSG_TEMPLATE = '''_%s_ awarded bounty'''

    def get_message(self):
        return self._get_concatenated_message(self.CUSTOM_MSG_TEMPLATE % self._activity.actor.handle)


class ActivityBountySuggestedMessage(ActivityBaseMessage):
    TYPE = "activity-bounty-suggested"
    CUSTOM_MSG_TEMPLATE = '''_%s_ suggested bounty'''


class ActivityBugClonedMessage(ActivityBaseMessage):
    TYPE = "activity-bug-cloned"
    CUSTOM_MSG_TEMPLATE = '''_%s_ cloned bug - %s'''

    def get_message(self):
        return self._get_concatenated_message(self.CUSTOM_MSG_TEMPLATE
                                              % (self._activity.actor.name, self._activity.original_report_id))

    def perform_action(self, jira_client, report_client, jira, report):
        cloned_report = report_client.get_report(self._activity.original_report_id)
        jira_client.add_remote_link(cloned_report, jira, "Cloners")


class ActivityBugDuplicateMessage(ActivityBaseMessage):
    TYPE = "activity-bug-duplicate"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked bug as duplicated - %s'''

    def get_message(self):
        return self._get_concatenated_message(self.CUSTOM_MSG_TEMPLATE
                                              % (self._activity.actor.name, self._activity.original_report_id))

    def perform_action(self, jira_client, report_client, jira, report):
        dup_report = report_client.get_report(self._activity.original_report_id)
        jira_client.add_remote_link(dup_report, jira, "Duplicate")


class ActivityBugInformativeMessage(ActivityBaseMessage):
    TYPE = "activity-bug-informative"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked bug as informative'''


class ActivityBugNeedsMoreInformationMessage(ActivityBaseMessage):
    TYPE = "activity-bug-needs-more-info"
    CUSTOM_MSG_TEMPLATE = '''_%s_ requested more information'''


class ActivityBugNewMessage(ActivityBaseMessage):
    TYPE = "activity-bug-new"
    CUSTOM_MSG_TEMPLATE = '''_%s_ changed state to new'''


class ActivityBugNotApplicableMessage(ActivityBaseMessage):
    TYPE = "activity-bug-not-applicable"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked bug as not applicable'''


class ActivityBugReopenedMessage(ActivityBaseMessage):
    TYPE = "activity-bug-reopened"
    CUSTOM_MSG_TEMPLATE = '''_%s_ reopened bug'''


class ActivityBugResolvedMessage(ActivityBaseMessage):
    TYPE = "activity-bug-resolved"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked bug as resolved'''


class ActivityBugSpamMessage(ActivityBaseMessage):
    TYPE = "activity-bug-spam"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked bug as spam'''


class ActivityBugTriagedMessage(ActivityBaseMessage):
    TYPE = "activity-bug-triaged"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked bug as triaged'''


class ActivityChangedScopeMessage(ActivityBaseMessage):
    TYPE = "activity-changed-scope"
    CUSTOM_MSG_TEMPLATE = '''_%s_ changed structured scope'''

    def perform_action(self, jira_client, report_client, jira, report):
        pass
        # TODO: update scope


class ActivityCommentMessage(ActivityBaseMessage):
    TYPE = "activity-comment"
    CUSTOM_MSG_TEMPLATE = '''_%s_ added a comment'''


class ActivityCommentsClosedMessage(ActivityBaseMessage):
    TYPE = "activity-comments-closed"
    CUSTOM_MSG_TEMPLATE = '''_%s_ closed comments'''


class ActivityExternalInvitationCancelledMessage(ActivityBaseMessage):
    TYPE = "activity-external-user-invitation-cancelled"
    CUSTOM_MSG_TEMPLATE = '''_%s_ cancelled invitation for %s'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.email))


class ActivityExternalInvitationInvitedMessage(ActivityBaseMessage):
    TYPE = "activity-external-user-invited"
    CUSTOM_MSG_TEMPLATE = '''_%s_ invited %s'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.email))


class ActivityExternalUserJoinedMessage(ActivityBaseMessage):
    TYPE = "activity-external-user-joined"
    CUSTOM_MSG_TEMPLATE = '''_%s_ user joined.  Duplicate Report: %s'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.duplicate_report_id))

    def perform_action(self, jira_client, report_client, jira, report):
        dup_report = report_client.get_report(self._activity.original_report_id)
        jira_client.add_remote_link(dup_report, jira, "Duplicate")


class ActivityExternalUserRemovedMessage(ActivityBaseMessage):
    TYPE = "activity-external-user-removed"
    CUSTOM_MSG_TEMPLATE = '''_%s_ removed user _%s_'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.removed_user.name))


class ActivityGroupAssignedToBugMessage(ActivityBaseMessage):
    TYPE = "activity-group-assigned-to-bug"
    CUSTOM_MSG_TEMPLATE = '''_%s_ assigned group: _%s_'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.group.name))


class ActivityHackerRequestedMediationMessage(ActivityBaseMessage):
    TYPE = "activity-hacker-requested-mediation"
    CUSTOM_MSG_TEMPLATE = '''_%s_ requested mediation'''


class ActivityManuallyDisclosedMessage(ActivityBaseMessage):
    TYPE = "activity-manually-disclosed"
    CUSTOM_MSG_TEMPLATE = '''_%s_ manually disclosed'''


class ActivityMediationRequestedMessage(ActivityBaseMessage):
    TYPE = "activity-mediation-requested"
    CUSTOM_MSG_TEMPLATE = '''_%s_ requested mediation'''


class ActivityNotEligibleForBountyMessage(ActivityBaseMessage):
    TYPE = "activity-not-eligible-for-bounty"
    CUSTOM_MSG_TEMPLATE = '''_%s_ marked not eligible for bounty'''


class ActivityReferenceIDAddedMessage(ActivityBaseMessage):
    TYPE = "activity-reference-id-added"
    CUSTOM_MSG_TEMPLATE = '''_%s_ added reference id - %s'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.username, self._activity.reference))


class ActivityReportBecamePublicMessage(ActivityBaseMessage):
    TYPE = "activity-report-became-public"
    CUSTOM_MSG_TEMPLATE = "report became public"

    def get_message(self):
        return self._get_concatenated_message(self.CUSTOM_MSG_TEMPLATE)


class ActivityTitleUpdatedMessage(ActivityBaseMessage):
    TYPE = "activity-report-title-updated"
    CUSTOM_MSG_TEMPLATE = '''_%s_ updated report title'''


class ActivityReportVulnerabilityTypesMessage(ActivityBaseMessage):
    TYPE = "activity-report-vulnerability-types-updated"
    CUSTOM_MSG_TEMPLATE = '''_%s_ updated vulnerability types'''


class ActivityReportSeverityUpdatedMessage(ActivityBaseMessage):
    TYPE = "activity-report-severity-updated"
    CUSTOM_MSG_TEMPLATE = '''_%s_ updated report severity'''


class ActivitySwagAwardedsMessage(ActivityBaseMessage):
    TYPE = "activity-swag-awarded"
    CUSTOM_MSG_TEMPLATE = '''_%s_ awarded swag'''


class ActivityUserAssignedMessage(ActivityBaseMessage):
    TYPE = "activity-user-assigned-to-bug"
    CUSTOM_MSG_TEMPLATE = '''_%s_ assigned user - _%s_'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.assigned_user.name))


class ActivityUserBannedFromProgramMessage(ActivityBaseMessage):
    TYPE = "activity-user-banned-from-program"
    CUSTOM_MSG_TEMPLATE = '''_%s_ banned user - _%s_'''

    def get_message(self):
        return self._get_concatenated_message(
            self.CUSTOM_MSG_TEMPLATE % (self._activity.actor.name, self._activity.removed_user.name))


class ActivityCVEIDAddedMessage(ActivityBaseMessage):
    TYPE = "activity-cve-id-added"
    CUSTOM_MSG_TEMPLATE = '''_%s_ added CVE-ID'''
