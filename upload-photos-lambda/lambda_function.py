import json
import boto3
import time

# AWS Clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Set Bucket Name & DynamoDB Table
BUCKET_NAME = "arijitpal-photography-s3"
DYNAMO_TABLE_NAME = "arijitpal-photography-datastore"


# Lambda Handler
def lambda_handler(event, context):
    try:
        # ✅ Handle preflight (OPTIONS) requests
        if "httpMethod" in event and event["httpMethod"] == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS, POST",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"message": "CORS preflight successful"})
            }

        # ✅ Handle cases where API Gateway sends a raw JSON object
        body = json.loads(event["body"]) if "body" in event else event

        # Extract file details
        filename = body["filename"]
        title = body.get("title", "")
        genres = body.get("genres", [])  # List of genres
        description = body.get("description", "")
        exif = body.get("exif", "")

        # ✅ Generate S3 file path
        file_path = f"photos/{filename}"

        # ✅ Generate a presigned URL for uploading
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_path, "ContentType": "image/jpeg"},
            ExpiresIn=3600  # URL expires in 1 hour
        )

        # ✅ Public URL for S3 file
        public_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_path}"

        # ✅ Save each genre as a separate row in DynamoDB
        table = dynamodb.Table(DYNAMO_TABLE_NAME)
        for genre in genres:
            table.put_item(
                Item={
                    "genre": genre,  # ✅ Partition Key
                    "s3_key": file_path,
                    "image_url": public_url,
                    "title": title,
                    "description": description,
                    "exif": exif,
                    "timestamp": int(time.time())  # Optional for sorting
                }
            )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({
                "s3_key": file_path,
                "presigned_url": presigned_url
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"error": str(e)})
        }
