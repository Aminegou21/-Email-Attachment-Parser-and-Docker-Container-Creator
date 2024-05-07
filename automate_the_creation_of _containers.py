#1. Make sure you enable IMAP in your gmail settings
#(Log on to your Gmail account and go to Settings, See All Settings, and select
#Forwarding and POP/IMAP tab. In the "IMAP access" section, select Enable IMAP.)

#2. If you have 2-factor authentication, gmail requires you to create an application
#specific password that you need to use. 
#Go to your Google account settings and click on 'Security'.
#Scroll down to App Passwords under 2 step verification.
#Select Mail under Select App. and Other under Select Device. (Give a name, e.g., python)
#The system gives you a password that you need to use to authenticate from python.

import imaplib
import email
import os
import PyPDF2
import yaml
import docker
import time
from email.message import EmailMessage
import re
import random


def connect_to_email(username, password, server='imap.gmail.com'):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    return mail

# Function to fetch attachments from emails
def fetch_attachments(mail, folder='INBOX', save_path='./attachments', processed_emails=set()):
    while True:
        mail.select(folder)
        result, data = mail.search(None, 'UNSEEN')  # Fetch only unread emails
        for num in data[0].split():
            if num not in processed_emails:
                result, data = mail.fetch(num, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                if msg.get_content_maintype() == 'multipart':
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue
                        filename = part.get_filename()
                        if filename:
                            os.makedirs(save_path, exist_ok=True)
                            attachment_path = os.path.join(save_path, filename)
                            with open(attachment_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            print(f"Attachment '{filename}' saved successfully.")
                            yield attachment_path
                processed_emails.add(num)  # Add the email ID to processed set
        time.sleep(10)  # Wait for new emails every 10 seconds

# Function to parse PDF form and generate YAML config
def parse_pdf_form(pdf_file, yaml_file):
    text = ""
    with open(pdf_file, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()

    # Extract data from PDF and generate YAML config
    database_name, username, password = extract_form_fields(text)
    generate_yaml_config(database_name,username,password, yaml_file)

# Function to extract form fields from text
def extract_form_fields(text):
    # Define regex patterns for extracting form fields
    database_pattern = r'Database:\s*(\w+)'
    username_pattern = r'Username:\s*(\w+)'
    password_pattern = r'Password:\s*(\w+)'

    # Extract database name
    database_match = re.search(database_pattern, text)
    database_name = database_match.group(1) if database_match else "Database"

    # Extract username
    username_match = re.search(username_pattern, text)
    username = username_match.group(1) if username_match else "Username"

    # Extract password
    password_match = re.search(password_pattern, text)
    password = password_match.group(1) if password_match else "Password"

    return database_name, username, password

used_ports = set()

def generate_unique_port():
    # Generate a random port number between 33000 and 33999
    while True:
        port = random.randint(33000, 33999)
        if port not in used_ports:
            used_ports.add(port)
            return port
# Function to generate YAML config
def generate_yaml_config(database_name,username,password, yaml_file):
    
    # Generate a unique port number for the containern
    host_port = generate_unique_port()

    data = {
        'image': "mysql:latest",
        'container_name': f'{password}_container',
        'environment': {
            'MYSQL_ROOT_PASSWORD': password,
            'MYSQL_DATABASE': database_name,  # Added comma here
            'MYSQL_USER': username,      # Added comma here
            'MYSQL_PASSWORD': password   # Added comma here
        },
        'ports': {
            "3306/tcp": f"{host_port}"  # Map container port 3306 to a unique host port
        }
    }

    with open(yaml_file, 'w') as file:
        yaml.dump(data, file)
    print(f"YAML configuration file '{yaml_file}' generated successfully.")


# Function to create container from YAML
def create_container_from_yaml(yaml_file):
    try:
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)
        client = docker.from_env()
        container = client.containers.run(
            image=config['image'],
            name=config['container_name'],
            detach=True,
            environment=config.get('environment', None),
            ports=config.get('ports', None)
        )
        print(f"Container '{config['container_name']}' created successfully.")
    except Exception as e:
        error_message = f"Error occurred: {e}"
        print(error_message)

if __name__ == "__main__":
    username = 'email you want to extract the pdf file'
    password = 'the password that syestem give you'#read 2
    processed_emails = set()  # Set to store processed email IDs
    mail = connect_to_email(username, password)
    attachments = fetch_attachments(mail, processed_emails=processed_emails)
    for attachment in attachments:
        pdf_file = attachment
        yaml_file = os.path.splitext(pdf_file)[0] + ".yaml"
        parse_pdf_form(pdf_file, yaml_file)
        create_container_from_yaml(yaml_file)
