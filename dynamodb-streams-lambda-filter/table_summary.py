import time

from datetime import datetime
import boto3

from event_generator import USER_IDS, VIDEO_IDS, TABLE_NAME

QUERY_INTERVAL_IN_SECONDS = 15

ATTRIBUTES = ["views", "duration", "likes", "dislikes"]

TABLE = boto3.resource("dynamodb").Table(TABLE_NAME)
DYNAMODB = boto3.resource("dynamodb")

TABLE_CELL_WIDTH = 10

def get_summary(pk, key, list_of_ids):
    response = DYNAMODB.batch_get_item(
        RequestItems={
            TABLE_NAME: {
                "Keys": [
                    {"PK": f"{pk}#{id_}", "SK": "SUMMARY"} for id_ in list_of_ids
                ]
            }
        }
    )

    items = response["Responses"][TABLE_NAME]

    clean_items = []
    for item in items:
        clean_item = {key: item[key]}
        for attr in ATTRIBUTES:
            clean_item[attr] = int(item.get(attr, 0))
        clean_items.append(clean_item)

    return sorted(clean_items, key=lambda x: x[key])    

def print_table(list_of_rows, key):

    def get_divider(num_cells, row_char="-", middle_char="+"):
        single_cell = row_char * TABLE_CELL_WIDTH

        cells = [single_cell for _ in range(num_cells)]

        return "|" + middle_char.join(cells) + "|"

    def get_row(values, middle_char="|"):
        values = [str(value).ljust(TABLE_CELL_WIDTH)[:TABLE_CELL_WIDTH] for value in values]
        return "|" + middle_char.join(values) + "|"

    num_cells = len(ATTRIBUTES) + 1

    print("")
    print(get_divider(num_cells))
    header = [key] + ATTRIBUTES
    print(get_row(header))
    print(get_divider(num_cells))

    attrs = [key] + ATTRIBUTES

    for row in list_of_rows:
        cells = [row.get(item) for item in attrs]
        print(get_row(cells))
        print(get_divider(num_cells))
    print(f"Fetched at {datetime.now().isoformat(timespec='seconds')}")
    print("")

def format_delta(old, new):
    if old < new:
        return f"+ {new - old}"

    if old > new:
        return f"- {new - old}"

    return "± 0"

def main():


    while True:
        print_table(get_summary("VIDEO", "videoId", VIDEO_IDS), "videoId")
        print_table(get_summary("USER", "userId", USER_IDS), "userId")
        print("x" * 56)
        time.sleep(QUERY_INTERVAL_IN_SECONDS)

if __name__ == "__main__":
    main()
