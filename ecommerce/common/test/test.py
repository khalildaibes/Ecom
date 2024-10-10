import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import subprocess
import os

def run_npx_command():
    try:
        # Change to D: drive
        os.chdir('D:')
        current_directory = os.getcwd()
        print("Current working directory:", current_directory)
        # Define the project directory where you want to cd into
        project_directory = r"D:\\ecommerce\\react-ecommerce-website-stripe"

        # Check if the directory exists
        if not os.path.isdir(project_directory):
            raise FileNotFoundError(f"Directory '{project_directory}' does not exist")

        # Run the correct command (try 'npm run dev' if 'npx run dev' fails)
        result = subprocess.run(['npx', 'dev'], cwd=project_directory, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print("npx dev output:")
            print(result.stdout)
        else:
            print("Error running npx dev:")
            print(result.stderr)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except Exception as e:
        print(f"An error occurred: {e}")


def run_node_command():
    try:
        # Run the Node.js script using subprocess
        result = subprocess.run(['node', 'example.js'], capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print("Node.js script output:")
            print(result.stdout)
        else:
            print("Node.js script error:")
            print(result.stderr)
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

    
    run_npx_command()
    
    # Send success email after processing
    send_success_email(args.email)

if __name__ == '__main__':
    main()
