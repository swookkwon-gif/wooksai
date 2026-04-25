import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
# We need 'modify' access to read/update labels and 'drive.file' to upload attachments.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.file'
]

def authenticate_gmail(account="mail1"):
    """Shows basic usage of the Gmail API.
    Log in via the browser and save credentials to token_{account}.json.
    """
    creds = None
    token_file = f'token_{account}.json'
    # The file stores the user's access and refresh tokens
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("No valid token found. Starting OAuth flow. Please check your browser.")
            # Ensure credentials.json exists in the current directory
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from GCP Console.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Run local server to catch the callback
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            print(f"Wrote new {token_file}")
            
    return creds

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Authenticate multiple Gmail accounts")
    parser.add_argument('-a', '--account', default='mail1', help="Account name to authenticate (e.g., mail1, mail2)")
    args = parser.parse_args()
    
    creds = authenticate_gmail(account=args.account)
    print(f"Authentication successful for account: {args.account}!")
