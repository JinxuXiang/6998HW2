import json
import logging
import random
import string

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
               
               

# import requests

region = 'us-east-1'
es_url = 'https://search-photos-udwnrlejebrgcalsyoufgt7zie.us-east-1.es.amazonaws.com/photos/_search'

'''
def extract_item(item):
    bucket = item["_source"]["bucket"]
    object_key = item["_source"]["objectKey"]
    labels = item["_source"]
    image_url = "https://{:s}.s3.amazonaws.com/{:s}".format(bucket, object_key)
    return {
        "url": image_url,
        "labels": labels
    }
'''
def extract_item(item):
    bucket = item["_source"]["bucket"]
    object_key = item["_source"]["objectKey"]
    labels = item["_source"]
    image_url = "https://{:s}.s3.amazonaws.com/{:s}".format(bucket, object_key)
    return image_url


def search_images(keywords):

    try:
        query = ""
        for keyword in keywords:
            query += str(keyword + " ")
        url = es_url + "?q=%s" % query
        print(url)

        es_response = requests.get(url, auth=auth).json()
        print(list(map(extract_item, es_response["hits"]["hits"])))

        if "hits" not in es_response and "hits" not in es_response["hits"]:
            return {
                'statusCode': 400,
                'body': json.dumps("No such photos.1")
            }
        return {
            'statusCode': 200,
            'body': json.dumps(list(map(extract_item, es_response["hits"]["hits"])))
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps("No such photos.2")
        }

def lambda_handler(event, context):
    response = dict()
    response["headers"] = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT",
        "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    }
    print("start")
    try:
        print(event)
        '''
        all_keywords = event['currentIntent']['slots']['query']
        keywords = all_keywords.split(" ")
        print(keywords)
        for i in range(len(keywords)):
            if keywords[i][-1] == 's':
                keywords[i] = keywords[i][:-1]
        print(keywords)
        '''
        
        
        
        if event["httpMethod"].upper() == "OPTIONS":
            response['statusCode'] = 200

            return response
        

        query = event["queryStringParameters"]['q']
        print('Query:', query)
        lex = boto3.client('lex-runtime')

        lex_response = lex.post_text(
            botName='photos',
            botAlias='prod',
            userId='123',
            inputText=query
        )
        print("Lex", lex_response)

        keywords = []
        all_value = lex_response['slots']['query'].split(' ')
        print("All value:",all_value)
        for val in all_value:
            if val is None:
                continue
            if val[-1] == 's':
                keywords.append(val[:-1])
            else:
                keywords.append(val)

        print(keywords)
        

        response.update(search_images(keywords))
        
        
    except Exception as e:
        response['statusCode'] = 400
        response["body"] = json.dumps("No such photos.3")
    
    print(response)
    return response