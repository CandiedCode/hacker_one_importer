import logging
from datetime import datetime, timezone
from logging.config import dictConfig

import click

from hacker_one_importer.config import get_config
from hacker_one_importer.dynamodb import get_last_activity_date
from hacker_one_importer.worker import import_issues, import_issue

# get configs
config = get_config()

# setup logging
logging_config = dict(
    version=1,
    formatters={
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(threadName)s %(module)s [in %(pathname)s:%(lineno)d] %(message)s",
            "formatTime": "%Y-%m-%dT%H:%M:%S%z"
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-5s%(reset)s %(blue)s %(asctime)s %(threadName)s %(module)s[%(lineno)d]"
                      " %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
    handlers={
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
          },
        "docker": {
           "level": "INFO",
           "class": "logging.StreamHandler",
           "formatter": "verbose"
           },
    },
    root={
        "level": logging.DEBUG,
        "handlers": ["console"] if config.Environment == 'Development' else ["docker"]
    },
)

dictConfig(logging_config)
logger = logging.getLogger()


def parse_date(last_activity):
    last_date = datetime.strptime(last_activity, "%Y-%m-%d %H:%M")
    return datetime(last_date.year, last_date.month, last_date.day, last_date.hour, last_date.minute,
                    last_date.second, tzinfo=timezone.utc)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--report_id', default=0, help='Import a specific report id')
@click.option('--last_activity', default=None, help='Last Activity Date to Import (YYYY-MM-DD HH:MM:SS (in UTC))')
@click.option('--parallel/--not_parallel', default=True, help='Run in parallel mode')
@click.option('--import_all', is_flag=True, help='Ignore last_activity date and import all hacker one reports')
@click.option('--update_h1/--do_not_update_h1', default=True, help='do_not_update_h1 will prevent any updates to h1.  '
                                                                   'Which is updating issue_reference_id')
@click.option('--ignore_dynamo', is_flag=True, help='ignore_dynamodb prevents the updating the last_activity_date in '
                                                    'dynamodb')
@click.option('--debug/--no-debug', default=False, help='Prints input flags')
def imports(report_id, last_activity, parallel, import_all, update_h1, ignore_dynamo, debug):
    if debug:
        logger.debug("""Passed in settings:   
            report_id: %s
            last_activity_date: %s
            parallel: %s
            all: %s
            update_h1: %s
            ignore_dynamodb: %s""" % (report_id, last_activity, parallel, import_all, update_h1, ignore_dynamo))

        return

    if report_id:
        click.echo('Processing report: %s' % report_id)
        import_issue(report_id, update_h1=update_h1)
    elif last_activity is not None:
        last_activity_date = parse_date(last_activity)
        click.echo('Processing Reports with Last Activity Date: %s' % str(last_activity_date))
        import_issues(last_activity_date=last_activity_date,
                      multithread=parallel,
                      import_all=import_all,
                      update_h1=update_h1,
                      ignore_dynamodb=ignore_dynamo)
    else:
        click.echo('Processing All Reports')
        import_issues(multithread=parallel, import_all=import_all, update_h1=update_h1, ignore_dynamodb=ignore_dynamo)


@cli.command()
def activity_date():
    click.echo("Last activity date in dynamo: %s" % get_last_activity_date())


if __name__ == "__main__":
    import_issues()



