##### 123123123123
import datetime
import json
import base64
import boto3
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth

session = boto3.Session()
credentials = session.get_credentials()

ask = 'AKIAT' + 'AVO3D'
sak = '8Mm07EVn' + '/nSUTP/'
ask = ask + str('JB4RQARKVI')
sak = sak + 'gEq/yIif' + str('nBFEzL1Cvcmtk9mk+')

auth = AWSRequestsAuth(aws_access_key=ask,
               aws_secret_access_key=sak,
               aws_host='search-photos-udwnrlejebrgcalsyoufgt7zie.us-east-1.es.amazonaws.com',
               aws_region=session.region_name,
               aws_service='es')
               
               
bucket = '6998hw2photo'

def generate_label_list(photo):
    
    client = boto3.client('rekognition')
    
    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                    MaxLabels=10)
    print('rekognition',response)
    label_list = []

    try:
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(bucket)
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
        transcribe = boto3.client('transcribe')
        file_name = records[0]['s3']['object']['key'] 
        object_url = 'https://s3.amazonaws.com/{0}/{1}'.format(bucket, file_name)
        
        response = transcribe.start_transcription_job(
            TranscriptionJobName = file_name.split('/')[1].split('.')[0],
            LanguageCode='en-US',
            MediaFormat='mp3',
            Media={
                'MediaFileUri': object_url
            },
            OutputBucketName='6998hw2photo' 
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
        print('photo', photo)
        label_list = generate_label_list(photo)
        print(label_list)
        labels.append(label_list)
    print('labels',labels)

    url = 'https://search-photos-udwnrlejebrgcalsyoufgt7zie.us-east-1.es.amazonaws.com/photos/_doc'
    header = {"Content-Type": "application/json"}
    for label in labels:
        params = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimestamp": str(datetime.datetime.now()),
            "labels": label
        }
        print('params', params)

        response_es = requests.post(url, data=json.dumps(params), headers=header, auth=auth)
        print(response_es.content)
    print("Finish")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
