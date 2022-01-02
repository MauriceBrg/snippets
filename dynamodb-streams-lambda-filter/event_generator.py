import random
import time

from datetime import datetime

import boto3
import pytz

VIDEO_IDS = range(0, 10)
USER_IDS = range(0, 5)
EVENT_TYPES = ["LIKE", "DISLIKE", "VIEW", "VIEW", "VIEW", "VIEW"] # to make views more likely

TABLE_NAME = "filter-demo-data"

def generate_event():

    event_type = random.choice(EVENT_TYPES)

    if event_type == "VIEW":
        user_id = random.choice(USER_IDS)
        video_id = random.choice(VIDEO_IDS)
        timestamp = datetime.now(pytz.UTC).isoformat(timespec="milliseconds")

        print(f"USER {user_id} watches VIDEO {video_id}")

        return {
            "type": "VIEW",
            "PK": f"USER#{user_id}",
            "SK": f"VIDEO#{video_id}#VIEW#{timestamp}",
            "duration": random.randint(30, 120),
            "userId": str(user_id),
            "videoId": str(video_id), 
            "GSI1PK": f"VIDEO#{video_id}",
            "GSI1SK": f"VIEW#{timestamp}#USER#{user_id}"
        }
    elif event_type == "DISLIKE":
        user_id = random.choice(USER_IDS)
        video_id = random.choice(VIDEO_IDS)

        print(f"USER {user_id} dislikes VIDEO {video_id}")

        return {
            "type": "VOTE",
            "PK": f"USER#{user_id}",
            "SK": f"VIDEO#{video_id}#VOTE",
            "userId": str(user_id),
            "videoId": str(video_id),
            "voteType": "DISLIKE",
            "GSI1PK": f"VIDEO#{video_id}",
            "GSI1SK": f"DISLIKE#USER#{user_id}"
        }
    else:
        user_id = random.choice(USER_IDS)
        video_id = random.choice(VIDEO_IDS)

        print(f"USER {user_id} likes VIDEO {video_id}")

        return {
            "type": "VOTE",
            "PK": f"USER#{user_id}",
            "SK": f"VIDEO#{video_id}#VOTE",
            "userId": str(user_id),
            "videoId": str(video_id),
            "voteType": "LIKE",
            "GSI1PK": f"VIDEO#{video_id}",
            "GSI1SK": f"LIKE#USER#{user_id}"
        }

def main():

    table = boto3.resource("dynamodb").Table(TABLE_NAME)

    while True:
        event = generate_event()

        table.put_item(Item=event)

        time.sleep(.5)


if __name__ == "__main__":
    main()
