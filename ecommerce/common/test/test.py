import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import subprocess
import os
import time




def checkout_and_create_branch(existing_branch, new_branch):
    try:
                # Change to the desired project directory
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        os.chdir(project_directory)
        print(f"Changed to directory: {os.getcwd()}")

        # Copy the current environment variables (e.g., from VS Code terminal)
        env = os.environ.copy()

        # Ensure npm and npx paths are included in the environment
        env["PATH"] = r"C:\Program Files\nodejs;" + env["PATH"]
        # Step 1: Checkout the existing branch
        result = subprocess.run(['git', 'checkout', existing_branch], check=True, capture_output=True, text=True)
        print(f"Checked out to {existing_branch}")
        
        # Step 2: Create and checkout the new branch
        result = subprocess.run(['git', 'checkout', '-b', new_branch], check=True, capture_output=True, text=True)
        print(f"Created and switched to new branch {new_branch}")
        
        # Step 3: Push the new branch to the remote repository
        result = subprocess.run(['git', 'push', '-u', 'origin', new_branch], check=True, capture_output=True, text=True)
        print(f"Pushed {new_branch} to origin and set upstream")
    
    except subprocess.CalledProcessError as e:
        # Capture both stdout and stderr for better logging
        print(f"An error occurred: {e.stderr}")



def run_npm_command_to_run_dev():
    
    
    #  note the when we continue we already close the process of the npm run 
    try:
        # Change to the desired project directory
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        os.chdir(project_directory)
        print(f"Changed to directory: {os.getcwd()}")

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
                print("10 seconds passed, continuing with the rest of the code.")
                break

            # Read the next line of stdout
            output = process.stdout.readline()

            # If there is no output and the process has finished, break
            if output == '' and process.poll() is not None:
                break

            # If there is output, print it
            if output:
                print(output.strip())

        # Continue executing the rest of your code without waiting for the process to finish
        print("Code continues after 10 seconds without waiting for full output.")

    except FileNotFoundError as fnf_error:
        print(fnf_error)
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
    checkout_and_create_branch('main', 'feature/my-new-branch')
    
    
    # run_npm_command_to_run_dev()
    
    # Send success email after processing
    send_success_email(args.email)

if __name__ == '__main__':
    main()
