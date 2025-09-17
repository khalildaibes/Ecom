import argparse
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from ecommerce.common.api.digitalOcean.vpcCommands import VpcCommands
from ecommerce.common.helpFunctions.common import handle_error, logger




def install_strapi_on_droplet(ip_address, vpc_name):
    """
    Install Strapi on an existing droplet
    """
    try:
        logger.info(f"Installing Strapi on droplet: {vpc_name} at IP: {ip_address}")
        
        # Prepare the content to write to the file
        # Use password authentication instead of SSH key for Windows compatibility
        vpc = VpcCommands(vpc_ip=ip_address, username="root", password="KHALIL123er", ssh_key_file_path=r"C:\Users\Admin\.ssh\id_ed25519")
        
        # Define local and remote file paths
        local_file_path = Path(r"D:\Ecom\Ecom\ecommerce\common\api\digitalOcean\setup_strapi.sh")
        remote_file_path = f"./setup_strapi.sh"

        # Copy the script to the server
        logger.info("Copying setup script to server...")
        vpc.copy_file_to_server(local_file_path, remote_file_path)
        
        # Run the script on the server with correct argument order
        # Arguments: KHALIL_PASS, GITHUB_TOKEN, DROPLET_NAME, VPC_IP
        logger.info("Running Strapi setup script on server...")
        vpc.run_script_on_server(
            remote_file_path, 
            "KHALIL123er",  # KHALIL_PASS
            os.getenv("GITHUB_TOKEN"),  # GITHUB_TOKEN
            vpc_name,  # DROPLET_NAME
            ip_address  # VPC_IP
        )
        
        logger.info("Strapi installation completed successfully!")
        return True
        
    except Exception as ex:
        logger.error(f"Failed to install Strapi: {ex}")
        handle_error(ex)
        return False


def get_job_params():
    parser = argparse.ArgumentParser(description="Install Strapi on a droplet")
    parser.add_argument('--ip_address', required=True, help='IP address of the droplet')
    parser.add_argument('--vpc_name', required=True, help='Name of the VPC/droplet')
    
    return parser.parse_args()


def main():
    args = get_job_params()
    try:
        success = install_strapi_on_droplet(args.ip_address, args.vpc_name)
        if success:
            logger.info("Strapi installation completed successfully!")
        else:
            logger.error("Strapi installation failed!")
            sys.exit(1)
    except Exception as e:
        handle_error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()