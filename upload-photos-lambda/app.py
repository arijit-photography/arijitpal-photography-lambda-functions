import json
import os
import boto3
from botocore.exceptions import ClientError
# from urllib.parse import quote_plus

dynamodb = boto3.resource("dynamodb")
table_name = os.getenv("TABLE_NAME", "arijitpal-photography-datastore")
table = dynamodb.Table(table_name)

s3 = boto3.client("s3")
bucket_name = os.getenv("BUCKET_NAME", "arijitpal-photography-s3")


def lambda_handler(event, context):
    # Expecting an API Gateway "proxy" integration with a POST method
    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {})
    if event.get("httpMethod") != "POST":
        return build_response(400, {"error": "Only POST allowed"})

    try:
        body = json.loads(event["body"])
    except:
        return build_response(400, {"error": "Invalid JSON"})

    required = ["filename", "title", "genres", "description", "exif"]
    for f in required:
        if f not in body:
            return build_response(400, {"error": f"Missing field '{f}'"})

    filename = body["filename"]  # e.g., "LakeBled.jpg"
    title = body["title"]
    genres = body["genres"]  # e.g., ["landscape", "travel"]
    description = body["description"]
    exif = body["exif"]

    # 1) Generate a PUT pre-signed URL for S3
    try:
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": filename,
                "ContentType": "image/jpeg"  # or detect from your React file
            },
            ExpiresIn=3600  # valid for 1 hour
        )
    except ClientError as e:
        return build_response(500, {"error": str(e)})

    # 2) Save metadata to DynamoDB
    item = {
        "imageId": filename,
        "title": title,
        "genres": genres,
        "description": description,
        "exif": exif,
        # Optionally store the S3 key or final URL
        "s3Key": filename
    }
    table.put_item(Item=item)

    # 3) Return the preSignedUrl in the response
    return build_response(200, {
        "message": "Metadata saved, pre-signed URL generated",
        "presignedUrl": presigned_url
    })


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS"
        },
        "body": json.dumps(body)
    }
