import json
import boto3
import logging

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS SES Client
ses = boto3.client("ses", region_name="us-east-1")

# Email Configuration
RECIPIENT_EMAIL = "yourname@example.com"

def lambda_handler(event, context):
    logger.info("Lambda function invoked")

    try:
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "CORS preflight successful"})
            }

        body = json.loads(event["body"])
        name = body["name"]
        sender_email = body["email"]
        message = body["message"]

        logger.info(f"Received message from {name} ({sender_email})")

        # Send email using SES
        response = ses.send_email(
            Source=RECIPIENT_EMAIL,
            Destination={"ToAddresses": [RECIPIENT_EMAIL]},
            ReplyToAddresses=[sender_email],
            Message={
                "Subject": {"Data": f"New Contact Form Submission from {name}"},
                "Body": {"Text": {"Data": message}}
            }
        )

        logger.info(f"Email sent successfully: {response}")

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"message": "Email sent successfully!"})
        }

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"error": str(e)})
        }
