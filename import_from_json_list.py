import requests
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()
domain = os.getenv('CONVEYOUR_DOMAIN')
appkey = os.getenv('CONVEYOUR_APPKEY')
token = os.getenv('CONVEYOUR_TOKEN')

verifySSL=True
failed_records = []

def identify_contact(contact):
    identify_url = f"{domain}/api/analytics/identify"
    payload = json.dumps({
        "id": contact["id"],
        "traits": contact["traits"]
    })
    headers = {
        'x-conveyour-appkey': appkey,
        'x-conveyour-token': token,
        'Content-Type': 'application/json'
    }

    response = requests.post(identify_url, headers=headers, data=payload,verify=verifySSL)
    return response.json()


def confirm_contact(email):
    confirm_url = f"{domain}/api/contacts?filters[email]={email}&format=v2"
    headers = {
       'x-conveyour-appkey': appkey,
        'x-conveyour-token': token,
        'Content-Type': 'application/json'
    }
    response = requests.get(confirm_url, headers=headers, verify=verifySSL)
    return response.json()



def process_contacts(file_path):
    with open(file_path, 'r') as file:
        contacts = json.load(file)


    if not contacts:
        print("No contacts found in the file.")
        return
    
    total_contacts = len(contacts)
    success_count_local = 0; 

    for contact in contacts:
        identify_response_data = identify_contact(contact)
        if success_count_local == 0 and identify_response_data.get("status") == "ok":
            print(f"Identify call for {contact['traits']['email']} status OK, waiting 30 seconds to check that first contact worked...")
            time.sleep(30)
            confirm_response_data = confirm_contact(contact['traits']['email'])
            if confirm_response_data.get("status") == "ok" and confirm_response_data.get("data", {}).get("results", []):
                confirmed_email = confirm_response_data["data"]["results"][0].get("email")
                if confirmed_email == contact['traits']['email']:
                    success_count_local += 1
                    print(f"Confirmed contact {contact['traits']['email']} successfully.")
                    continue
                else:
                    print(f"Email mismatch: expected {contact['traits']['email']}, got {confirmed_email}")
                    break
            else:
                print(f"Failed to confirm contact {contact['traits']['email']}: {confirm_response_data}")
                break
            
        print(f"Identify call for {contact['traits']['email']} status OK")
        if identify_response_data.get("status") == "ok":
            success_count_local += 1
        else:
            failed_records.append(contact)
        
    print(f"Processed {total_contacts} contacts, {success_count_local} successfully identified.")
            

if __name__ == "__main__":
    process_contacts('bvm_cy_sync.json')
    if failed_records:
        with open('failed_to_queue.json', 'w') as failed_file:
            json.dump(failed_records, failed_file, indent=4)
        print(f"Failed records saved to failed_to_queue.json")
