import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table_name = os.getenv("TABLE_NAME", "Photos")
table = dynamodb.Table(table_name)

s3 = boto3.client("s3")
bucket_name = os.getenv("BUCKET_NAME", "my-photography-bucket")


def lambda_handler(event, context):
    # For an HTTP GET, e.g. /list
    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {})
    if event.get("httpMethod") != "GET":
        return build_response(400, {"error": "Only GET allowed"})

    # 1) Scan all items in DynamoDB
    resp = table.scan()
    items = resp.get("Items", [])

    grouped = {}  # e.g. { "travel": [...], "landscape": [...], ... }

    for item in items:
        # item includes { imageId, title, genres, description, exif, s3Key }
        # build an object for the final JSON
        detail = {
            "image": item["imageId"],
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "exif": item.get("exif", "")
        }

        # optionally generate a GET pre-signed URL so you can display the image
        # if your bucket is not public.
        key = item["s3Key"]
        try:
            get_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=3600  # 1 hour
            )
            detail["presignedGetUrl"] = get_url
        except ClientError as e:
            detail["presignedGetUrl"] = None

        for g in item.get("genres", []):
            if g not in grouped:
                grouped[g] = []
            grouped[g].append(detail)

    return build_response(200, grouped)


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        "body": json.dumps(body)
    }
