import datetime
import json
import base64
import boto3
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth


region = 'us-east-1'
access_key = 'AKIAQ4OP47PB42J5YBOK'
secret_key = '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'
bucket = '6998hw2'

def generate_label_list(photo):
    
    client = boto3.client('rekognition',region_name=region,
                   aws_access_key_id=access_key,
                   aws_secret_access_key=secret_key)
    print("photo:", photo)
    
    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                    MaxLabels=10)
    print(response)
    label_list = []

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    try:
        label_path = 'Label/' + photo.split('/')[1].split('.')[0] + '.txt'
        print("Label_path", label_path)
        body = my_bucket.Object(label_path).get()['Body'].read()
        print(body)
        b = body.decode("utf-8")
        b = b.split(',')
        print('Custom Labels:', b)
        for i in b:
            label_list.append(i.lower())
    except:
        pass
    
    for label in response['Labels']:
        label_list.append(label['Name'].lower())
    
    return label_list


def lambda_handler(event, context):
    records = event["Records"]
    print('Records', records)
    suffix = records[0]["s3"]["object"]["key"][-3:]
    print(suffix)
    if suffix == 'txt':
        print("Txt file!")
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda txt file!')
        }
    elif suffix == 'mp3':
        print("Mp3 file!")
        transcribe = boto3.client('transcribe',region_name=region,
                   aws_access_key_id=access_key,
                   aws_secret_access_key=secret_key)
        file_name = records[0]['s3']['object']['key'] 
        object_url = 'https://s3.amazonaws.com/{0}/{1}'.format(bucket, file_name)
            
        response = transcribe.start_transcription_job(
            TranscriptionJobName = file_name.split('/')[1].split('.')[0],
            LanguageCode='en-US',
            MediaFormat='mp3',
            Media={
                'MediaFileUri': object_url
            },
            OutputBucketName='6998hw2' 
            )
        print(response)
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda mp3 file!')
        }
    elif suffix == 'son' or suffix == 'emp':
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda other file!')
        }

    labels = []
    for record in records:
        s3 = record["s3"]
        photo = s3["object"]["key"]
        label_list = generate_label_list(photo)
        print(label_list)
        labels.append(label_list)
    print(labels)

    url = 'https://search-photos-2vwh3kzfdacftoms2qukez3i5y.us-east-1.es.amazonaws.com/photos/_doc'
    header = {"Content-Type": "application/json"}
    for label in labels:
        params = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimestamp": str(datetime.datetime.now()),
            "labels": label
        }
        print(params)
        auth = AWSRequestsAuth(aws_access_key=access_key,
                       aws_secret_access_key=secret_key,
                       aws_host='search-photos-2vwh3kzfdacftoms2qukez3i5y.us-east-1.es.amazonaws.com',
                       aws_region=region,
                       aws_service='es')

        response_es = requests.post(url, data=json.dumps(params), headers=header, auth=auth)
    print("Finish")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
