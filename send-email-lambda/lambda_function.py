import json
import boto3
import logging
import re

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS SES Client
ses = boto3.client("ses", region_name="us-east-1")

# Email Configuration
RECIPIENT_EMAIL = "yourname@example.com"  # ✅ Replace with your verified SES email

# Regex to validate email format
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def lambda_handler(event, context):
    logger.info(f"Incoming event: {event}")

    try:
        # ✅ Handle CORS Preflight Request
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

        # ✅ Ensure 'body' exists and parse it only if it's a string
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)  # Convert JSON string to dictionary

        if not isinstance(body, dict):  # Ensure body is a dictionary
            raise ValueError("Invalid body format")

        # ✅ Extract fields safely
        subject = body.get("subject", "No Subject")
        sender_email = body.get("email", "").strip()
        message = body.get("message", "").strip()

        if not message:
            raise ValueError("Message field is empty")

        # ✅ Validate sender email format
        if not sender_email or not re.match(EMAIL_REGEX, sender_email):
            raise ValueError(f"Invalid sender email: {sender_email}")

        logger.info(f"Received message with subject '{subject}' from {sender_email}")

        # ✅ Send email using SES
        response = ses.send_email(
            Source=RECIPIENT_EMAIL,
            Destination={"ToAddresses": [RECIPIENT_EMAIL]},
            ReplyToAddresses=[sender_email],  # ✅ Ensure valid sender email
            Message={
                "Subject": {"Data": f"Contact Form: {subject}"},
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
