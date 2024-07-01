import requests
import json
from dotenv import load_dotenv
import os
import time


# Load environment variables from .env file
load_dotenv()
domain = os.getenv('CONVEYOUR_DOMAIN')

identify_url = domain+"/api/analytics/identify"
print("Identify URL:", identify_url)

email = 'tester2@example.com'

identify_payload = json.dumps({
  "id": "23656",
#   "id": "$email",
  "traits": {
    "email": email,
    "company": "Acme Inc",
    "name": "Adam Van Winkle"
    
  }
})
headers = {
  'x-conveyour-appkey': os.getenv('CONVEYOUR_APPKEY'),
  'x-conveyour-token': os.getenv('CONVEYOUR_TOKEN'),
  'Content-Type': 'application/json'
}

identify_response = requests.post(identify_url, headers=headers, data=identify_payload)

# Check the response status
identify_response_data = identify_response.json()
if identify_response_data.get("status") == "ok":
    print("Identify call status OK, waiting 30 seconds...")
    time.sleep(30)
    
    # Follow-up API call to confirm
    confirm_url = domain+"/api/contacts?filters[email]="+email+"&format=v2"
    confirm_response = requests.get(confirm_url, headers=headers)
    
    confirm_response_data = confirm_response.json()
    pretty_response = json.dumps(confirm_response_data, indent=4)
    print(pretty_response)
else:
    print("Identify call failed:", identify_response.text)