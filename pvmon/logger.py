import json
import logging
import logging.handlers
from pathlib import Path
from twilio.rest import Client

# Text comment to check if development mode is working.

# For a list of the logger variables used in this module, see: https://docs.python.org/3/library/logging.html


logs_path = Path.cwd()

local_logger_file = logs_path / 'pvmon.log'
if not Path.exists(local_logger_file):
    local_logger_file.touch()

local_logger = logging.getLogger("libs.logging.local_logger")


def local_logger_config():
    local_logger.setLevel(logging.INFO)
    log_handler = logging.FileHandler(local_logger_file.as_posix())
    log_format = (
        '{ "loggerName":"%(name)s", "timestamp":"%(asctime)s", '
        '"pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", '
        '"filename":"%(filename)s", "functionName":"%(funcName)s", '
        '"levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", '
        '"levelName":"%(levelname)s", "message":"%(message)s"}'
    )
    log_handler.setFormatter(logging.Formatter(log_format))
    local_logger.addHandler(log_handler)


local_logger_config()


system_logger = logging.getLogger("libs.logging.system_logger")


def system_logger_config():
    system_logger.setLevel(logging.INFO)
    log_handler = logging.handlers.SysLogHandler('/dev/log')
    log_format = (
        '{"loggerName":"%(name)s", "timestamp":"%(asctime)s", '
        '"pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", '
        '"filename":"%(filename)s", "functionName":"%(funcName)s", '
        '"levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", '
        '"levelName":"%(levelname)s", "message":"%(message)s"}'
    )
    log_handler.setFormatter(logging.Formatter(log_format))
    system_logger.addHandler(log_handler)


system_logger_config()


"""
NB system_logger (which uses the default settings for SysLogHandler) sends all logs to a UNIX socket at /dev/log; syslogd listens on that socket and then does with those logs whatever it's told to in /etc/syslog.conf.  Under the default configuration, these logs can be read from the command line using journalctl; example follows: "journalctl | less | grep python | grep CRITICAL"
"""


def parse_logs_for_warning_or_error(log_file=local_logger_file.as_posix()):
    with open(file=log_file, mode='r') as file:
        for line in file.readlines():
            if 'WARNING' or 'ERROR' in line:
                log = json.loads(line)
                print(log['timestamp'], log['functionName'], log['message'])


def sms_event(
        message: str,
        account_sid: str,
        auth_token: str,
        to_phone: str,
        from_phone: str,
):
    client = Client(
        account_sid,
        auth_token,
    )
    try:
        client.messages.create(
            to=to_phone,
            from_=from_phone,
            body=message,
        )
        local_logger.info(f"SMS alert sent to {to_phone}")
    except Exception as e:
        local_logger.error(f'The Twilio API config successfully loaded but there was a problem sending the SMS message; returned exception {e}')
