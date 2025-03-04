import json
import boto3

# AWS Clients
dynamodb = boto3.resource("dynamodb")

# Configuration
BUCKET_NAME = "arijitpal-photography-static-site-s3"
DYNAMO_TABLE_NAME = "arijitpal-photography-datastore"

def lambda_handler(event, context):
    try:
        # Fetch data from DynamoDB
        table = dynamodb.Table(DYNAMO_TABLE_NAME)
        response = table.scan()

        images = []
        for item in response.get("Items", []):
            s3_key = item["s3_key"]

            # Construct the public S3 URL
            public_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

            images.append({
                "src": public_url,  # Publicly accessible image URL
                "title": item["title"],
                "category": item["category"],
                "description": item["description"],
                "exif": item["exif"],
            })

        return {
            "statusCode": 200,
            "body": json.dumps(images)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
