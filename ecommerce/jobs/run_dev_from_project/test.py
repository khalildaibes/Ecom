import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import subprocess
import os
import sys
import time
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))



def run_npm_command_to_run_dev():
    
    
    #  note the when we continue we already close the process of the npm run 
    try:
        # Change to the desired project directory
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        os.chdir(project_directory)
        logger.info(f"Changed to directory: {os.getcwd()}")

        # Copy the current environment variables (e.g., from VS Code terminal)
        env = os.environ.copy()

        # Ensure npm and npx paths are included in the environment
        env["PATH"] = r"C:\Program Files\nodejs;" + env["PATH"]

        # Start the process using Popen
        process = subprocess.Popen(['npm', 'run', 'dev'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

        # Track the start time
        start_time = time.time()

        # Read the output for up to 10 seconds
        while True:
            # Check if 10 seconds have passed
            if time.time() - start_time > 10:
                logger.info("10 seconds passed, continuing with the rest of the code.")
                break

            # Read the next line of stdout
            output = process.stdout.readline()

            # If there is no output and the process has finished, break
            if output == '' and process.poll() is not None:
                break

            # If there is output, print it
            if output:
                logger.info(output.strip())

        # Continue executing the rest of your code without waiting for the process to finish
        logger.info("Code continues after 10 seconds without waiting for full output.")

    except FileNotFoundError as fnf_error:
        logger.info(fnf_error)
    except Exception as e:
        logger.info(f"An error occurred: {e}")


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
        logger.info(f"Success email sent to {to_email}")
    except Exception as e:
        logger.info(f"Failed to send email: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process email, password, and template ID")
    
    parser.add_argument('--email', required=True, help='Email address')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--templatesId', required=True, help='Template ID')
    
    args = parser.parse_args()

    # Prerequisite check to ensure none of the parameters are empty
    if not args.email or not args.password or not args.templatesId:
        logger.info("Error: All parameters (email, password, templatesId) must be provided.")
        return

    # Example actions with the provided parameters
    logger.info(f"Email: {args.email}")
    logger.info(f"Password: {args.password}")
    logger.info(f"Template ID: {args.templatesId}")

    
    
    run_npm_command_to_run_dev()
    
    # Send success email after processing
    send_success_email(args.email)

if __name__ == '__main__':
    main()
