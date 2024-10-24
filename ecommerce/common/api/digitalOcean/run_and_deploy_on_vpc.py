import os

import paramiko
import logging


from ecommerce.common.helpFunctions.common import handle_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VpcCommands:
    def __init__(self, ssh_client):
        self.ssh_client = ssh_client
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise Exception(
                "GitHub token not found. Please set the GITHUB_TOKEN environment variable or pass it to the class.")


    def run_ssh_command(self,  command):
        """Run a command on the remote VPS using SSH."""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
    
            if stdout.channel.recv_exit_status() == 0:
                logger.info(f"Command succeeded: {command}\nOutput: {output}")
                return output
            else:
                logger.error(f"Command failed: {command}\nError: {error}")
                handle_error(error)
        except Exception as e:
            logger.error(f"Failed to execute command: {command}\nError: {str(e)}")
            raise
    
    
    def setup_ssh_connection(self, vpc_ip, username, password):
        """Establish an SSH connection to the VPS."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
            ssh.connect(vpc_ip, username=username, password=password)
            logger.info(f"Connected to VPS at {vpc_ip}")
            return ssh
        except Exception as e:
            logger.error(f"Failed to connect to VPS: {vpc_ip}\nError: {str(e)}")
            raise
    
    
    def setup_strapi_on_vps(self, vpc_ip, droplet_name, github_token, username, password):
        """
        Set up Strapi on a VPS with the given VPC IP and droplet name using SSH.
        Executes the step-by-step setup for Strapi.
        """
        # Establish SSH connection
        self.ssh_client = self.setup_ssh_connection(vpc_ip, username, password)
    
        try:
            # Step 1: Requirements
            logger.info(f"Setting up Strapi on VPS: {droplet_name} with VPC: {vpc_ip}")
    
            # Step 2: Install Git & GitHub CLI
            logger.info("Installing Git and GitHub CLI...")
            self.run_ssh_command( f"mkdir /root/{droplet_name}")
            self.run_ssh_command( "sudo apt install git -y")
            self.run_ssh_command( f"echo '{github_token}' | gh auth login --with-token")
    
            # Step 3: Clone the Strapi repository
            logger.info("Cloning Strapi repository...")
            #  TODO make this dynamic
            repo  = "https://github.com/khalildaibes/ecommerce-strapi.git"
            self.run_ssh_command( f"git clone {repo}")

            # Step 4: Install PostgreSQL & Set Up Database
            logger.info("Installing PostgreSQL and setting up the database...")
            self.run_ssh_command("sudo apt install postgresql postgresql-contrib -y")
            khalil_pass = "KHALIL123er"
            self.run_ssh_command(f"sudo -u postgres psql -c \"CREATE USER strapi WITH PASSWORD '{khalil_pass}';\"")
            self.run_ssh_command("sudo -u postgres psql -c \"ALTER USER strapi WITH SUPERUSER;\"")
            self.run_ssh_command("sudo -u postgres psql -c \"CREATE DATABASE ecommerce_strapi OWNER strapi;\"")
    
            # Step 5: Install NVM and Node.js
            logger.info("Installing NVM and Node.js...")
            self.run_ssh_command("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash")
            self.run_ssh_command("source ~/.bashrc")
            self.run_ssh_command("nvm install 20")
            self.run_ssh_command("nvm use 20")
            self.run_ssh_command("apt install npm")
            self.run_ssh_command("npm i")


            # Step 6: Install PM2
            logger.info("Installing PM2...")
            self.run_ssh_command("npm install pm2 -g")

            # Step 7: Install Nginx and configure
            logger.info("Installing and configuring Nginx...")
            self.run_ssh_command("sudo apt install nginx -y")
    
            # Create Nginx configuration file
            nginx_config = f"""
            server {{
                listen 80;
                server_name {vpc_ip};
    
                location / {{
                    proxy_pass http://localhost:1337;
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection 'upgrade';
                    proxy_set_header Host $host;
                    proxy_cache_bypass $http_upgrade;
                }}
    
                location /api {{
                    proxy_pass http://localhost:1337;
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection 'upgrade';
                    proxy_set_header Host $host;
                    proxy_cache_bypass $http_upgrade;
                }}
            }}
            """
            # Upload the nginx config file
            sftp = self.ssh_client.open_sftp()
            with sftp.file("/etc/nginx/sites-available/website.conf", "w") as f:
                f.write(nginx_config)
    
            # Enable the site and test Nginx
            self.run_ssh_command("sudo ln -s /etc/nginx/sites-available/website.conf /etc/nginx/sites-enabled/")
            self.run_ssh_command("sudo nginx -t")
            self.run_ssh_command("sudo systemctl restart nginx")
    
            # Step 8: Configure .env file for Strapi
            logger.info("Configuring .env file for Strapi...")
            env_file_content = f"""
            HOST={vpc_ip}
    
            DATABASE_CLIENT=postgres
            DATABASE_HOST={vpc_ip}
            DATABASE_PORT=5432
            DATABASE_NAME=ecommerce_strapi
            DATABASE_USERNAME=strapi
            DATABASE_PASSWORD=KHALIL123er
            DATABASE_SSL=false
    
            JWT_SECRET=JWT_SECRET
            """

            # Write the .env file to the VPS
            with sftp.file(f"/root/strapi-ecommerce/maisam-makeup-ecommerce-strapi/{droplet_name}.env", "a") as f:
                f.write(env_file_content)
    
            # Step 9: Configure PostgreSQL for external access
            logger.info("Configuring PostgreSQL for external access...")
            self.run_ssh_command(
                            "sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" /etc/postgresql/12/main/postgresql.conf")
            self.run_ssh_command("sudo ufw allow 5432/tcp")
            self.run_ssh_command("sudo systemctl restart postgresql")
    
            # Step 10: Final Steps - Build and Start Strapi
            logger.info("Running the final build and starting Strapi...")
            self. run_ssh_command("npm run build")
            self.run_ssh_command("pm2 start npm --name 'strapi-app' -- run start")
            self.run_ssh_command("pm2 restart all")
    
            logger.info("Strapi setup complete!")
            logger.info(f"Strapi is successfully set up on VPS {droplet_name} at {vpc_ip}.")
    
        finally:
            self.ssh_client.close()
            logger.info("SSH connection closed.")
    
