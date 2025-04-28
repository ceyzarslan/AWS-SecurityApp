import json
import boto3
import base64
from datetime import datetime
from enum import Enum

print('Loading function')

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
"""
def create_message_request():
    token = recipient["token"]
    service = recipient["service"]
    message_request = {
            'Addresses': {
                token: {
                    'ChannelType': 'GCM',
                },
            },
            'MessageConfiguration': {
                'GCMMessage': {
                    'Action': action,
                    'Body': message,
                    'Priority' : priority,
                    'SilentPush': silent,
                    'Title': title,
                    'TimeToLive': ttl,
                    'Url' : url
                }
            }
        }
    return message_request"""
    
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

def sendAlertNotification(message_request):
    pinpoint = boto3.client('pinpoint')
    # Gönderilecek veri

    token = recipient["token"]
    service = recipient["service"]

    response = pinpoint.send_messages(
            ApplicationId=application_id,
            MessageRequest=message_request
        )
        
    # Pinpoint ile bildirim gönderme işlemi
    """response = pinpoint.send_messages(
        ApplicationId=application_id,
        MessageRequest={
            'Addresses': {
                device_token: {
                    'ChannelType': 'GCM',
                    'Context': {
                        'deeplink': deep_link
                    }
                }
            },
            'MessageConfiguration': {
                'GCMMessage': {
                    'Action': 'DEEP_LINK',
                    'Body': message_body
                }
            }
        }
    )"""
    return response

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    
    #print(event["image"])
    
    #clients
    rekognition_client = boto3.client('rekognition')
    s3_client = boto3.client('s3')
    
    base64_image = event["image"]
    base64_image_formatted = base64_image.replace('/','_')
    
     # Base64 kodlu resmi decode et
    image_data = base64.b64decode(base64_image)

    print("original : ",base64_image)

    print("replaced")
    print(base64_image.replace('/','_'))

    # Önce gelen veride yüz tespiti yap
    detect_faces_response = rekognition_client.detect_faces(
        Image={
            'Bytes': image_data
        },
        Attributes=['DEFAULT']
    )
    isNotThing = False
    isKnownFace = False
    
    if detect_faces_response['FaceDetails']:
        print("Gelen veride yüz tespit edildi.")
        
         # S3 bucket adı ve yolunu belirle
        bucket_name = 'securevisagebucket140218-dev'  # S3 bucket adınız
        folder_prefix = 'public/homeowner/'
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        
        # Her bir fotoğraf için yüz karşılaştırması yap
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('.jpeg') or key.endswith('.jpg') or key.endswith('.png'):
                print("Comparing with:", key)
                reference_image_data = s3_client.get_object(Bucket=bucket_name, Key=key)['Body'].read()
                # Yüz tespit edildiyse, hedef yüz olarak gelen verideki yüzü kullanarak karşılaştırma yap
                result = rekognition_client.compare_faces(
                    SourceImage={'Bytes': image_data},
                    TargetImage={'Bytes': reference_image_data},
                    SimilarityThreshold=80  # İki yüz arasındaki benzerlik eşiği (0-100 arası değer)
                )
                # compare_faces işlemi başarıyla tamamlandı, sonuçları kullanabilirsiniz
                print("Yüz karşılaştırma işlemi başarıyla tamamlandı.")
                #print(result)
                if result['FaceMatches']:
                    print("Yüz tanımlandı!")
                    isNotThing = True
                    isKnownFace = True
                    person = key.split("/")[-1].split(".")[0:-1]
                    person = ".".join(person)
                    sendAlertNotification(create_message_request(AlertType.KNOWN_PERSON,"",person))
                    break
                else:
                    print("Yüz tanınamadı :(")
                    isNotThing = True
                    isKnownFace = False

    else:
        print("Gelen veride yüz tespit edilemedi.")
        sendAlertNotification(create_message_request(AlertType.THING,str(base64_image_formatted),""))
    
    if isNotThing and not isKnownFace:
        sendAlertNotification(create_message_request(AlertType.UNKOWN_PERSON,str(base64_image_formatted),str(key)))
    
    """try:
        result = rekognition_client.compare_faces(
            SourceImage={
                'Bytes': image_data
            },
            TargetImage={
                'Bytes': reference_image_data
            },
            SimilarityThreshold=80  # İki yüz arasındaki benzerlik eşiği (0-100 arası değer)
        )
        # compare_faces işlemi başarıyla tamamlandı, sonuçları kullanabilirsiniz
        print("Yüz karşılaştırma işlemi başarıyla tamamlandı.")
        print(result)
    except rekognition_client.exceptions.InvalidParameterException as e:
        # compare_faces işlemi geçersiz parametrelerle çağrıldı
        print("Hata: Geçersiz parametreler:", e)
    except Exception as e:
        # compare_faces işlemi sırasında genel bir hata oluştu
        print("Hata:", e)"""
    
    return "return"  # Echo back the first key value
    #raise Exception('Something went wrong')
