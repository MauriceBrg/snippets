import os

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "filter-demo-data")

TABLE = boto3.resource("dynamodb").Table(TABLE_NAME)
CLIENT = boto3.client("dynamodb")

def lambda_handler(event, context):

    # We can work on the assumption that we only get items
    # in NewImage with a type of "VIEW", that means we can
    # rely on userId, videoId, and duration being present.
    # We can also assume we get a single record.

    item = event["Records"][0]["dynamodb"]["NewImage"]
    event_name = event["Records"][0]["eventName"] # INSERT or REMOVE
    user_id = item["userId"]["S"]
    video_id = item["videoId"]["S"]
    duration = item["duration"]["N"]

    print(f"Type: {event_name} User: {user_id} Video: {video_id} Duration: {duration}")

    # We use a transaction so either both writes succeed, or both fail.
    CLIENT.transact_write_items(
        TransactItems=[
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S": f"USER#{user_id}"},
                        "SK": {"S": "SUMMARY"}
                    },
                    "UpdateExpression": "ADD #views :view_increment, "\
                        "#duration :duration_increment "\
                        "SET #type = :type, "\
                        "#userId = :userId",
                    "ExpressionAttributeNames": {
                        "#views": "views",
                        "#duration": "duration",
                        "#type": "type",
                        "#userId": "userId",
                    },
                    "ExpressionAttributeValues": {
                        ":view_increment": {"N": str(1)},
                        ":duration_increment": {"N": str(duration)},
                        ":type": {"S": "USER_SUMMARY"},
                        ":userId": {"S": str(user_id)},
                    },

                },
            },
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S": f"VIDEO#{video_id}"},
                        "SK": {"S": "SUMMARY"}
                    },
                    "UpdateExpression": "ADD #views :view_increment, "\
                        "#duration :duration_increment "\
                        "SET #type = :type, "\
                        "#videoId = :videoId, "\
                        "#gsi1pk = :gsi1pk, "\
                        "#gsi1sk = :gsi1sk",
                    "ExpressionAttributeNames": {
                        "#views": "views",
                        "#duration": "duration",
                        "#type": "type",
                        "#videoId": "videoId",
                        "#gsi1pk": "GSI1PK",
                        "#gsi1sk": "GSI1SK",
                    },
                    "ExpressionAttributeValues": {
                        ":view_increment": {"N": str(1)},
                        ":duration_increment": {"N": str(duration)},
                        ":type": {"S": "VIDEO_SUMMARY"},
                        ":videoId": {"S": str(video_id)},
                        ":gsi1pk": {"S": f"VIDEO#{video_id}"},
                        ":gsi1sk": {"S": "SUMMARY"},
                    },
                }
            },
        ]
    )
