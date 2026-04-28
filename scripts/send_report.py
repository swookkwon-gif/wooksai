import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
import sys, os
sys.path.append(os.path.dirname(__file__))
from auth import authenticate_gmail

def send_email():
    creds = authenticate_gmail(account="mail1")
    if not creds:
        print("Failed auth")
        return
    service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()
    
    try:
        with open('evaluations_report.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("File not found")
        return
        
    message.set_content(content)
    message['To'] = 'swookkwon@gmail.com'
    message['From'] = 'swookkwon@gmail.com'
    message['Subject'] = '[AI 봇] 뉴스레터 발신자별 평가 요약 리포트'
    
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    try:
        service.users().messages().send(userId="me", body=create_message).execute()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_email()
