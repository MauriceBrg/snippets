import os

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "filter-demo-data")

TABLE = boto3.resource("dynamodb").Table(TABLE_NAME)
CLIENT = boto3.client("dynamodb")

def lambda_handler(event, context):

    # We can work on the assumption that we only get items
    # in NewImage with a type of "VOTE", that means we can
    # rely on userId, videoId, and voteType being present.
    # We can also assume we get a single record.

    record = event["Records"][0]
    item = record["dynamodb"]["NewImage"]
    event_name = event["Records"][0]["eventName"] # INSERT or REMOVE
    user_id = item["userId"]["S"]
    video_id = item["videoId"]["S"]
    vote_type = item["voteType"]["S"]

    like_increment = 1 if vote_type == "LIKE" else 0
    dislike_increment = 1 if vote_type == "DISLIKE" else 0

    if "OldImage" in record["dynamodb"]:
        # This means the vote has changed, otherwise we wouldn't see this event!
        if vote_type == "LIKE":
            dislike_increment -= 1
        else:
            like_increment -= 1

    print(f"Type: {event_name} User: {user_id} Video: {video_id} VoteType: {vote_type}")

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
                    "UpdateExpression": "ADD #likes :like_increment, "\
                        "#dislikes :dislike_increment "\
                        "SET #type = :type, "\
                        "#userId = :userId",
                    "ExpressionAttributeNames": {
                        "#likes": "likes",
                        "#dislikes": "dislikes",
                        "#type": "type",
                        "#userId": "userId",
                    },
                    "ExpressionAttributeValues": {
                        ":like_increment": {"N": str(like_increment)},
                        ":dislike_increment": {"N": str(dislike_increment)},
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
                    "UpdateExpression": "ADD #likes :like_increment, "\
                        "#dislikes :dislike_increment "\
                        "SET #type = :type, "\
                        "#videoId = :videoId, "\
                        "#gsi1pk = :gsi1pk, "\
                        "#gsi1sk = :gsi1sk",
                    "ExpressionAttributeNames": {
                        "#likes": "likes",
                        "#dislikes": "dislikes",
                        "#type": "type",
                        "#videoId": "videoId",
                        "#gsi1pk": "GSI1PK",
                        "#gsi1sk": "GSI1SK",
                    },
                    "ExpressionAttributeValues": {
                        ":like_increment": {"N": str(like_increment)},
                        ":dislike_increment": {"N": str(dislike_increment)},
                        ":type": {"S": "VIDEO_SUMMARY"},
                        ":videoId": {"S": str(video_id)},
                        ":gsi1pk": {"S": f"VIDEO#{video_id}"},
                        ":gsi1sk": {"S": "SUMMARY"},
                    },
                }
            },
        ]
    )
