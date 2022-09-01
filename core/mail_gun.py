import requests
import json

#"sandbox7f77c579408349699d3f779f1a42fe09.mailgun.org"

def send_email_from_mailgun(subject,link,_from = FROM,_to = TO,uri = URI,token = API_TOKEN):
    return requests.post(uri,
			 auth=("api", token),
			 data={"from":_from,
			       "to": [_to],
			       "subject": subject,
			       "template": "signup",
			       "h:X-Mailgun-Variables": json.dumps({"link":link})})
