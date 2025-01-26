import os
import paramiko
import logging
import subprocess
import time
from retrying import retry
from ecommerce.common.helpFunctions.common import handle_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VpcCommands:
    def __init__(self, vpc_ip, username, password, ssh_key_file_path=r"C:\Users\Admin\.ssh\id_ed25519"):
        self.ssh_key_file_path = ssh_key_file_path
        self.ssh_client_sftp = None
        self.username= username
        self.password= password
        self.vpc_ip= vpc_ip
        self.ssh_client = self.setup_ssh_connection(self.vpc_ip, self.username, self.password)

    @retry(stop_max_attempt_number=4, wait_exponential_multiplier=2000)
    def setup_ssh_connection(self, vpc_ip, username, password):
        """Establish an SSH connection to the VPS."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(vpc_ip, username=username, password=password, key_filename=self.ssh_key_file_path, timeout=30)
            logger.info(f"Connected to VPS at {vpc_ip}")
            return ssh
        except Exception as e:
            logger.error(f"Failed to connect to VPS: {vpc_ip}\nError: {str(e)}")
            raise

    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def copy_file_to_server(self, local_file_path, remote_file_path):
        """Copy a file from local machine to the server using SFTP."""
        try:
            self.ssh_client = self.setup_ssh_connection(self.vpc_ip, self.username, self.password)
            transport = self.ssh_client.get_transport()
            transport.set_keepalive(interval=900000)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(local_file_path, remote_file_path)
            sftp.close()
            logger.info(f"File {local_file_path} copied to {remote_file_path} on the server.")
        except Exception as e:
            logger.error(f"Failed to copy file to server: {str(e)}")
            raise

    @retry(stop_max_attempt_number=4, wait_exponential_multiplier=2000)
    def run_script_on_server(self, remote_script_path, vpc_ip, git_token, droplet_name, password):
        """Run a script on the server."""
        try:
            self.ssh_client = self.setup_ssh_connection(self.vpc_ip, self.username, self.password)
            logger.info("started the run process")
            log_file_path = "/root/run_process_log.txt"
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"chmod +x {remote_script_path} && {remote_script_path} {password} {git_token} {droplet_name} {vpc_ip} > {log_file_path} 2>&1"
            )
            output = stdout.read().decode()
            error = stderr.read().decode()

            if stdout.channel.recv_exit_status() == 0:
                logger.info(f"Script ran successfully: {remote_script_path}\nOutput: {output}")
            else:
                logger.error(f"Failed to run script: {remote_script_path}\nError: {error}")
            return
        except Exception as e:
            logger.error(f"Failed to run script on server: {str(e)}")
            raise


# Usage example
