import json
import os
import dicebot
import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from urllib.parse import parse_qs # to parse slack input

# https://awslabs.github.io/aws-lambda-powertools-python/#features
tracer = Tracer()
logger = Logger()
metrics = Metrics()

# Global variables are reused across execution contexts (if available)
session = boto3.Session()

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
        AWS Lambda handler
        Parameters
        ----------
        context: object, required
            Lambda Context runtime methods and attributes

        Attributes
        ----------

        context.aws_request_id: str
            Lambda request ID
        context.client_context: object
            Additional context when invoked through AWS Mobile SDK
        context.function_name: str
            Lambda function name
        context.function_version: str
            Function version identifier
        context.get_remaining_time_in_millis: function
            Time in milliseconds before function times out
        context.identity:
            Cognito identity provider context when invoked through AWS Mobile SDK
        context.invoked_function_arn: str
            Function ARN
        context.log_group_name: str
            Cloudwatch Log group name
        context.log_stream_name: str
            Cloudwatch Log stream name
        context.memory_limit_in_mb: int
            Function memory

            https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

        event: dict, required
            API Gateway Lambda Proxy Input Format

            {
                "resource": "Resource path",
                "path": "Path parameter",
                "httpMethod": "Incoming request's method name"
                "headers": {Incoming request headers}
                "queryStringParameters": {query string parameters }
                "pathParameters":  {path parameters}
                "stageVariables": {Applicable stage variables}
                "requestContext": {Request context, including authorizer-returned key-value pairs}
                "body": "A JSON string of the request payload."
                "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
            }

            https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

        Returns
        ------
        API Gateway Lambda Proxy Output Format: dict
            'statusCode' and 'body' are required

            {
                "isBase64Encoded": true | false,
                "statusCode": httpStatusCode,
                "headers": {"headerName": "headerValue", ...},
                "body": "..."
            }

            # api-gateway-simple-proxy-for-lambda-output-format
            https: // docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    dice_input = None
    status_code = 500 # fallback value
    result_output = {} # fallback
    print(event) # ensure event input is logged
    if "body" in event:
        dice_input = event["body"]
    try:
        dice_query = parse_qs(event["body"])
        print(dice_query) # log parsed message from slack
        if "text" in dice_query:
            dice_input = dice_query["text"][0] # The text field is an array
        else:
            dice_input = "" # default to empty string if missing
        parsed_input = dicebot.parse_text(dice_input)
    except Exception as e:
        status_code = 400
        result_output = {"text": str(e)}
    else:
        dice_results = dicebot.roll_dice(**parsed_input)
        print(dice_results)
        result_output = dicebot.format_slack_response(dice_results)
        status_code = 200
    finally:
        return {
            "statusCode": status_code,
            "body": json.dumps(result_output)
        }
