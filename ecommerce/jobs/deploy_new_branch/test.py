import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import subprocess
import os
import time

from ecommerce.common.api.github.gitManager import GitManager




# github token for jenkins ghp_58DQsSmfG
# .38M52lL8gHoqYr
# m5zklOIg3Dc9Jc

def checkout_and_create_branch(existing_branch, new_branch):
    try:
        # Define project details
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        github_username = "khalildaibes1"
        
       # Create an instance of GitManager
        git_manager = GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN"))

        # Checkout to 'main' and create a new branch 'feature/my-new-branch'
        git_manager.checkout_and_create_branch('main', 'feature/my-new-branch')
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")




def send_success_email(to_email):
    # Set up the email details
    from_email = "khalildaibes1@gmail.com"  # Replace with your email
    subject = "Pipeline Run Successful"
    body = f"Hello, \n\nThe pipeline has completed its run successfully.\n\nBest regards,\nYour Jenkins Pipeline"

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:

        YOUR_GOOGLE_EMAIL = 'khalildaibes1@gmail.com'  # The email you setup to send the email using app password
        YOUR_GOOGLE_EMAIL_APP_PASSWORD = 'rovx umao gokt fssy'  # The app password you generated

        smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtpserver.ehlo()
        smtpserver.login(YOUR_GOOGLE_EMAIL, YOUR_GOOGLE_EMAIL_APP_PASSWORD)

        # Test send mail
        sent_from = YOUR_GOOGLE_EMAIL
        sent_to = to_email  #  Send it to self (as test)
        smtpserver.sendmail(sent_from, sent_to, body)

        # Close the connection
        smtpserver.close()
        print(f"Success email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process email, password, and template ID")
    
    parser.add_argument('--email', required=True, help='Email address')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--templatesId', required=True, help='Template ID')
    
    args = parser.parse_args()

    # Prerequisite check to ensure none of the parameters are empty
    if not args.email or not args.password or not args.templatesId:
        print("Error: All parameters (email, password, templatesId) must be provided.")
        return

    # Example actions with the provided parameters
    print(f"Email: {args.email}")
    print(f"Password: {args.password}")
    print(f"Template ID: {args.templatesId}")

    
    # Example usage:
    checkout_and_create_branch('main', 'feature/my-new-branch1')
    
    
    # run_npm_command_to_run_dev()
    
    # Send success email after processing
    send_success_email(args.email)

if __name__ == '__main__':
    main()
