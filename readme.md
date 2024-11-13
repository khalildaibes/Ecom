README: Automated Job Deployment Script
Overview

This script automates the process of deploying and managing the setup for a business-oriented e-commerce project. It integrates with different services (Sanity and Stripe), manages Git operations, creates configuration files, and triggers deployments on Vercel. The script aims to streamline the process of creating new business configurations and deploying them in an automated and efficient way.
Script Workflow
1. Getting Job Parameters

    The get_job_params() function retrieves command-line arguments required for the deployment job.

2. Triggering the Configuration File Creation

    The trigger_create_config_file_job() function is invoked to create the necessary configuration JSON file for the new project.

3. Git Operations

    The script checks out the existing template_maisam_makeup branch and creates a new feature branch with the name provided in the arguments (feature/{args.new_branch_name}).
    This process is performed for both the main project and the sanity-ecommerce-stripe subproject.

4. Loading the Configuration JSON

    The script loads the generated configuration file located at C:\ProgramData\Jenkins\.jenkins\workspace\create_bussniss_config_file\ecommerce\jobs\create_bussniss_config_file\{project_name}_config.json.
    The JSON data is then stored in a dictionary (client_data_dict) for use in subsequent operations.

5. Conditional Deployment Based on Database Selection

    The deployment path is chosen based on the args.db_selected value:
        Sanity:
            The deploy_sanity() function is triggered to deploy the Sanity project.
        Stripe:
            The script prepares a dictionary of placeholder values to replace within the e-commerce project files.
            A vercel_env.json file is created to store these environment variables.
            The replace_placeholders_in_repo() function updates the project with these placeholder values.
            The sanity-ecommerce-stripe directory is deleted if it is not needed for the Stripe deployment.
            The trigger_setup_strapi_job() function is triggered to configure Strapi.

6. Committing and Pushing Code to Git

    The script stages changes, commits them with a message including the current timestamp and user information, and pushes the new branch to the remote repository.

7. Deploying to Vercel

    The deploy_vercel() function is used to deploy the project to Vercel with the specified branch.

Directory Structure

    Project Directory: D:\ecommerce\react-ecommerce-website-stripe
    Sanity Subproject Directory: D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe
    Configuration JSON Location: C:\ProgramData\Jenkins\.jenkins\workspace\create_bussniss_config_file\ecommerce\jobs\create_bussniss_config_file\
    Environment File: D:\ecommerce\react-ecommerce-website-stripe\vercel_env.json

Key Functions Explained

    get_job_params(): Retrieves the command-line arguments for the job.
    trigger_create_config_file_job(): Triggers a job to create a configuration JSON file.
    checkout_and_create_branch(): Checks out an existing branch and creates a new branch.
    load_json_to_dict(): Loads the JSON configuration file into a dictionary.
    deploy_sanity(): Deploys the Sanity project using the provided arguments and configuration.
    replace_placeholders_in_repo(): Replaces placeholder text in the project files with actual values.
    trigger_setup_strapi_job(): Triggers a job to set up Strapi with the provided parameters.
    deploy_vercel(): Deploys the project to Vercel with the specified branch.

How to Run

    Ensure that all dependencies and libraries are installed.
    Update the file paths and environment variables as needed.
    Run the script from a command-line interface with the required arguments:

    python run_job.py --new_branch_name <branch_name> --new_business_name <business_name> --phone <phone_number> --db_selected <Sanity/Stripe>

Prerequisites

    Python
    Git
    JSON configuration files
    Jenkins for job management (optional)
    Vercel account for deployment
    Strapi and Sanity setup

Logging and Debugging

    The script logs operations such as JSON loading and Git commits.
    Errors are caught and logged to help with debugging and tracing failures.

Notes

    Ensure all directory paths are correct and accessible.
    This script assumes that Git and Python have been configured properly on the machine where it runs.
    The placeholders for environment variables should match the structure expected by the e-commerce project.