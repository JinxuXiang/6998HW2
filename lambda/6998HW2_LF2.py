import json
import logging
import random
import string

import boto3
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth


# import requests

region = 'us-east-1'
access_key = 'AKIAQ4OP47PB42J5YBOK'
secret_key = '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'
es_url = 'https://search-photos-2vwh3kzfdacftoms2qukez3i5y.us-east-1.es.amazonaws.com/photos/_search'

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
        auth = AWSRequestsAuth(aws_access_key=access_key,
                       aws_secret_access_key=secret_key,
                       aws_host='search-photos-2vwh3kzfdacftoms2qukez3i5y.us-east-1.es.amazonaws.com',
                       aws_region=region,
                       aws_service='es')
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
        lex = boto3.client('lex-runtime',region_name=region,
                   aws_access_key_id=access_key,
                   aws_secret_access_key=secret_key)

        lex_response = lex.post_text(
            botName='SearchPhotos',
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