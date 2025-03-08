import json
import boto3
import os

# Initialize AWS SES client
ses = boto3.client("ses", region_name="us-east-1")  # Change to your AWS region

# Your email (where messages will be sent)
RECIPIENT_EMAIL = "yourname@example.com"  # Your personal email to receive messages


def lambda_handler(event, context):
    try:
        # Parse incoming request body
        body = json.loads(event["body"])
        name = body["name"]
        sender_email = body["email"]  # The email provided by the user
        message = body["message"]

        # Construct email content
        subject = f"New Contact Form Submission from {name}"
        body_text = f"Name: {name}\nEmail: {sender_email}\nMessage:\n{message}"

        # Send the email using SES
        response = ses.send_email(
            Source=RECIPIENT_EMAIL,  # Must be verified in SES
            Destination={"ToAddresses": [RECIPIENT_EMAIL]},  # You receive the email
            ReplyToAddresses=[sender_email],  # When you reply, it goes to the user
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}}
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Enable CORS
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"message": "Email sent successfully!"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
