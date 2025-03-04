import json
import boto3

# AWS Clients
dynamodb = boto3.resource("dynamodb")

# Set DynamoDB Table Name
DYNAMO_TABLE_NAME = "arijitpal-photography-datastore"


# Lambda Handler
def lambda_handler(event, context):
    try:
        # ✅ Extract genre from query parameters
        genre = event["queryStringParameters"]["genre"]

        # ✅ Query DynamoDB for all photos in the specified genre
        table = dynamodb.Table(DYNAMO_TABLE_NAME)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("genre").eq(genre)
        )

        # ✅ Return list of photos
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(response["Items"])
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
