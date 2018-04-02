import boto3
import decimal
import json
from Contests import ContestMaker

# Helper class to convert a DynamoDB item to JSON.



def get_table(table_name):
    aws_access_key = ""
    aws_secret_access_key = ""
    region_name = "us-east-1"
    dynamodb = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=aws_access_key,
                              aws_secret_access_key=aws_secret_access_key)
    return dynamodb.Table(table_name)


def put_item():
    table = get_table("Contests")
    table.put_item(
        Item={
            "ContestID": "1",
            "questions": [1, 2, 3],
            "scores": [
            ]
        }
    )

# def get_item():
#     table = get_table("Contests")
#     return table.get_item(Key={
#         "ContestID": "1"
#     })['Item']

if __name__ == '__main__':
    table = get_table("Contests")
    contest_maker = ContestMaker(table)
    contest_maker.create_contest()
    # for problem in get_problems():
    #     problem.pop('points', None)
    #     table.put_item(Item=problem)
    #     print ("Added " + str(problem['contestId']))
