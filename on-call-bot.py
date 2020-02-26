#!/usr/bin/env python
import urllib.request
import json
import os
import sys
import boto3

from flask import abort, Flask, jsonify, request

app = Flask(__name__)

# Mandatory Variables
API_TOKEN = os.environ.get('API_TOKEN') or sys.exit("No Pagerduty API Token Given")
ESCALATION_POLICY_ID = os.environ.get('ESCALATION_POLICY_ID') or sys.exit("No Pagerduty Escalation Policy Given")
SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN') or sys.exit("No Slack Verification Token Given")
SLACK_TEAM_ID = os.environ.get('SLACK_TEAM_ID') or sys.exit("No Slack Team ID Given")
os.environ.get('AWS_ACCESS_KEY_ID') or sys.exit("No AWS_ACCESS_KEY_ID given")
os.environ.get('AWS_SECRET_ACCESS_KEY') or sys.exit("No AWS_SECRET_ACCESS_KEY given")

#Default Variables
PG_ENDPOINT = os.getenv('PAGERDUTY_ENDPOINT','https://api.pagerduty.com/oncalls?time_zone=CET')
ESCALATION_LEVEL = os.getenv('ESCALATION_LEVEL',int('1'))
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')

def do_aws_eip_api_call(filters):
    ec2 = boto3.client('ec2')

    try:
        response = ec2.describe_addresses(Filters=filters)
    except ConnectionError:
        print("The Connection with AWS went wrong")

    try:
        ip_list = [ adresses['PublicIp'] for adresses in response['Addresses'] ]
    except LookupError:
        print('Un Expected Answer from the AWS API')

    return ip_list

def get_on_call_user(api_endpoint):
    response = do_pg_api_call(api_endpoint)

    try:
        user = [item for item in response['oncalls']
                if item['escalation_policy']['id'] == ESCALATION_POLICY_ID
                and item['escalation_level'] == ESCALATION_LEVEL
                ]

        return user[0]['user']['summary']
    except LookupError:
        print('Un Expected Answer from the PagerDuty API')


def do_pg_api_call(url):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": 'Token token=' + API_TOKEN,
            "Accept": "application/vnd.pagerduty+json;version=2"
        },
        method='GET'
    )

    try:
        response = urllib.request.urlopen(request)
        data = response.read()
        encoding = response.info().get_content_charset('utf-8')
        data = json.loads(data.decode(encoding))

        return data

    except ConnectionError:
        print("The Connection with the Pager Duty API went wrong")


def is_request_valid(request):
    is_token_valid = request.form['token'] == SLACK_VERIFICATION_TOKEN
    is_team_id_valid = request.form['team_id'] == SLACK_TEAM_ID

    if not (is_token_valid and is_team_id_valid):
        abort(400)

    return

def do_json_slack_response(message):
    return jsonify(
        response_type='in_channel',
        text=message,
    )

def do_flat_list_with_periods(list_to_flat):
    return (', '.join(list_to_flat))

@app.route('/who-is-on-call', methods=['POST'])
def who_is_on_call():
    is_request_valid(request)

    user_on_call = get_on_call_user(PG_ENDPOINT)

    return do_json_slack_response(user_on_call)

@app.route('/backend-ips', methods=['POST'])
def ec2_backend_ip_list():
    is_request_valid(request)

    filters = [
        {'Name': 'domain', 'Values': ['standard']}
    ]

    ip_backend_list = do_aws_eip_api_call(filters)
    ip_backend_list = do_flat_list_with_periods(ip_backend_list)

    return do_json_slack_response("Backend Ip List: %s" % (ip_backend_list))

@app.route('/apidocsproxy-ips', methods=['POST'])
def ec2_apidocsproxy_ip_list():
    is_request_valid(request)

    filters = [
        {'Name': 'domain', 'Values': ['vpc']},
        {'Name': 'tag:apidocsproxy', 'Values': ['true']},
    ]

    ip_apidocsproxy_list = do_aws_eip_api_call(filters)
    ip_apidocsproxy_list = do_flat_list_with_periods(ip_apidocsproxy_list)

    return do_json_slack_response("ApiDocsProxy Ip List:  %s" % (ip_apidocsproxy_list))

@app.route('/status', methods=['GET'])
def status():
    return "live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=8080)
