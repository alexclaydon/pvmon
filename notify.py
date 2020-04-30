from libs.liblogger import local_logger
from twilio.rest import Client


def log_event(records):
    if records[0]:
        messages = [
            f"Following sensors have triggered at least two consecutive "
            f"production alerts within the {records[1]}-day analysis "
            f"window: "
        ]
        log_msg = f"Production anomaly logged when parsing data"
        local_logger.warning(log_msg)
        for key, value in records[0].items():
            for subkey, subvalue in value.items():
                if subkey[1] == "e":
                    continue
                else:
                    messages.append(
                        f"[{key}] mean: {value['mean']}%, {subkey[1]}: {subvalue}%;"
                    )
        messages = str(messages)
        strip = ["']", "['", " ,"]
        for item in strip:
            messages = messages.strip(item)
        messages = messages.rstrip(";")
        messages = messages.replace("', '", ", ")
        messages = messages.replace(";,", ";")
        messages = messages.replace(", ", "", 1)
        local_logger.warning(messages)
        return messages
    if not records[0]:
        log_msg = "No anomaly logged at this time"
        local_logger.info(log_msg)


def sms_event(
    messages,
    account_sid,
    auth_token,
    to_phone,
    from_phone,
    sms_on_no_anomaly: bool = False,
):
    client = Client(account_sid, auth_token,)
    if messages:
        try:
            client.messages.create(
                to=to_phone, from_=from_phone, body="SOLAR: " + messages,
            )
            log_msg = f"SMS alert sent to {to_phone}"
            local_logger.warning(log_msg)
        except Exception as e:
            log_msg = f"The Twilio API config successfully loaded but there was a problem sending the SMS message; returned exception {e}; no SMS will be sent at this time"
            local_logger.error(log_msg)
    if not messages:
        if sms_on_no_anomaly:
            try:
                client.messages.create(
                    to=to_phone,
                    from_=from_phone,
                    body="SOLAR: No anomaly logged at this time",
                )
                log_msg = f"Confirmation that no production anomaly has occurred was sent by SMS to {to_phone}"
                local_logger.info(log_msg)
            except Exception as e:
                log_msg = f"The Twilio API config successfully loaded but there was a problem sending the SMS message; returned exception {e}; no SMS will be sent at this time"
                local_logger.error(log_msg)
        else:
            log_msg = 'Configured not to send SMS if there is no production anomaly detected; accordingly, no SMS sent at this time.  If you want to receive explicit daily confirmation via SMS that there is no production anomaly, pass "yes" to the sms_on_no_anomaly parameter'
            local_logger.info(log_msg)
