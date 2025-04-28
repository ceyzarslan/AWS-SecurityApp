recipient = {
"token": "dz9vZxQ7QAKbC_MEbJETkI:APA91bGDpJDFOXV4pntMToHrdixGcvv2jEdffIWPmgCm2xZxSbO4ONVPGP7PvUnq2EjYRx3OUT20Z219C7Fscac6mKo7rMtN3gsXUeX94v5VIIdpIJNYem8Fpor6n8b8uN10jHSn9WtG",
"service": "GCM"
}
deep_link = "https://berkayykurtoglu.github.io"
device_token = "dz9vZxQ7QAKbC_MEbJETkI:APA91bGDpJDFOXV4pntMToHrdixGcvv2jEdffIWPmgCm2xZxSbO4ONVPGP7PvUnq2EjYRx3OUT20Z219C7Fscac6mKo7rMtN3gsXUeX94v5VIIdpIJNYem8Fpor6n8b8uN10jHSn9WtG"
application_id = "f799f778c1cf42da8d0c3c1d0701f614"
message = ("This is a sample message sent from Amazon Pinpoint by using the "
           "AWS SDK for Python (Boto3).")
title = "Test message sent from Amazon Pinpoint."
region = "us-east-1"
action = "DEEP_LINK"
url = "https://berkayykurtoglu.github.io/"
priority = "high"
ttl = 30
silent = False


class AlertType(Enum) :
    UNKOWN_PERSON = 1
    KNOWN_PERSON = 2
    THING = 3
    
def create_message_request(is_known : AlertType, image = "",person = ""):

    token = recipient["token"]
    service = recipient["service"]
    if is_known == AlertType.KNOWN_PERSON : 
        #prepare for known
        message_request = {
                'Addresses': {
                    token: {
                        'ChannelType': 'GCM',
                    },
                },
                'MessageConfiguration': {
                    'GCMMessage': {
                        'Action': "OPEN_APP",
                        'Body': f"{person} eve geldi !",
                        'Priority' : priority,
                        'SilentPush': silent,
                        'Title': "Tık Tık",
                        'TimeToLive': ttl,
                        'Url' : f"{url}{image}"
                    }
                }
            }
        
    elif is_known == AlertType.UNKOWN_PERSON : 
        #prepare for unkown
        message_request = {
                'Addresses': {
                    token: {
                        'ChannelType': 'GCM',
                    },
                },
                'MessageConfiguration': {
                    'GCMMessage': {
                        'Action': "DEEP_LINK",
                        'Body': "Tanınmayan bir kişi kapıya yaklaştı !",
                        'Priority' : priority,
                        'SilentPush': silent,
                        'Title': "Uyarı !",
                        'TimeToLive': ttl,
                        'Url' : f"{url}{image}"
                    }
                }
            }
    else : 
        #Thing
        message_request = {
                'Addresses': {
                    token: {
                        'ChannelType': 'GCM',
                    },
                },
                'MessageConfiguration': {
                    'GCMMessage': {
                        'Action': "DEEP_LINK",
                        'Body': "Bir şey kapıya yaklaştı gibi hissettik, emin olamadık bir bak istersen !",
                        'Priority' : priority,
                        'SilentPush': silent,
                        'Title': "Uyarı !",
                        'TimeToLive': ttl,
                        'Url' : f"{url}{image}"
                    }
                }
            }
    return message_request