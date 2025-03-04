import json
import boto3
import time

# AWS Clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Set Bucket Name & DynamoDB Table
BUCKET_NAME = "arijitpal-photography-static-site-s3"
DYNAMO_TABLE_NAME = "arijitpal-photography-datastore"


# Lambda Handler
def lambda_handler(event, context):
    try:
        # Parse input JSON
        body = json.loads(event["body"])
        filename = body["filename"]
        title = body.get("title", "")
        category = body.get("category", [])
        description = body.get("description", "")
        exif = body.get("exif", "")

        # Unique file path inside S3
        file_path = f"photos/{filename}"

        # ✅ Generate a presigned URL for uploading
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_path, "ContentType": "image/jpeg"},
            ExpiresIn=3600  # URL expires in 1 hour
        )

        public_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_path}"

        # ✅ Store metadata in DynamoDB
        table = dynamodb.Table(DYNAMO_TABLE_NAME)
        table.put_item(
            Item={
                "s3_key": file_path,
                "image_url": public_url,  # Store the public URL
                "title": title,
                "category": category,
                "description": description,
                "exif": exif,
                "timestamp": int(time.time())
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"s3_key": file_path, "presigned_url": presigned_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
