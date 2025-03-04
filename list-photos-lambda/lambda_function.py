import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# AWS Clients
dynamodb = boto3.resource("dynamodb")

# Set DynamoDB Table Name
DYNAMO_TABLE_NAME = "arijitpal-photography-datastore"


# ✅ Helper Function to Convert Decimal to Int/Float
def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)  # Convert to int if whole number
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    return obj


# ✅ Lambda Handler
def lambda_handler(event, context):
    try:
        # ✅ Extract genre from query parameters
        genre = event.get("queryStringParameters", {}).get("genre", "")

        if not genre:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"error": "Missing genre parameter"})
            }

        # ✅ Query DynamoDB for all photos in the specified genre
        table = dynamodb.Table(DYNAMO_TABLE_NAME)
        response = table.query(
            KeyConditionExpression=Key("genre").eq(genre)
        )

        # ✅ Convert Decimal values to standard types
        photos = convert_decimal(response.get("Items", []))

        # ✅ Ensure response is always a JSON-compatible list
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(photos)  # ✅ JSON-friendly response
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"error": str(e)})
        }
