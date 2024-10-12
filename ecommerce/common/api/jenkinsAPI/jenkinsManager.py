
import time
from dataclasses import dataclass
import jenkins

@dataclass
class JenkinsJob:
    job_name: str
    job_url: str
    build_number: int = None
    status: str = None
    console_output: str = None


class JenkinsManager:
    def __init__(self, jenkins_url, username, api_token):
        """
        Initializes the JenkinsManager with Jenkins instance details.
        :param jenkins_url: The base URL of the Jenkins instance.
        :param username: Jenkins username.
        :param api_token: Jenkins API token.
        """
        self.server = jenkins.Jenkins(jenkins_url, username=username, password=api_token)

    def trigger_job(self, job_name, parameters=None):
        """
        Triggers a Jenkins job (pipeline) with or without parameters and returns the build number.
        :param job_name: The name of the Jenkins job to trigger.
        :param parameters: Optional dictionary of parameters to pass to the job.
        :return: The build number of the triggered job or None on failure.
        """
        try:
            if parameters:
                queue_item_number = self.server.build_job(job_name, parameters)
            else:
                queue_item_number = self.server.build_job(job_name)
            print(f"Job '{job_name}' triggered successfully. Queue Item: {queue_item_number}")
            return queue_item_number
        except jenkins.JenkinsException as e:
            print(f"Failed to trigger job: {str(e)}")
            return None

    def get_build_number_from_queue(self, job_name, queue_item_number):
        """
        Retrieves the build number once the job starts from the queue.
        :param job_name: The name of the Jenkins job.
        :param queue_item_number: The queue item number of the job.
        :return: The build number of the job.
        """
        while True:
            try:
                queue_item = self.server.get_queue_item(queue_item_number)
                if 'executable' in queue_item:
                    build_number = queue_item['executable']['number']
                    print(f"Job started. Build number: {build_number}")
                    return build_number
                else:
                    print("Job is still in the queue. Waiting for it to start...")
                    time.sleep(5)
            except jenkins.JenkinsException as e:
                print(f"An error occurred while getting the build number: {str(e)}")
                return None

    def get_console_output(self, job_name, build_number):
        """
        Retrieves the console output of a specific Jenkins job build.
        :param job_name: The name of the Jenkins job.
        :param build_number: The build number to retrieve the console output for.
        :return: The console output as a string.
        """
        try:
            console_output = self.server.get_build_console_output(job_name, build_number)
            return console_output
        except jenkins.JenkinsException as e:
            print(f"Failed to retrieve console output: {str(e)}")
            return None

    def get_build_status(self, job_name, build_number):
        """
        Retrieves the status of a specific Jenkins build.
        :param job_name: The name of the Jenkins job.
        :param build_number: The build number to check the status for.
        :return: The result of the build (SUCCESS, FAILURE, etc.).
        """
        try:
            build_info = self.server.get_build_info(job_name, build_number)
            return build_info['result']
        except jenkins.JenkinsException as e:
            print(f"An error occurred while retrieving the build status: {str(e)}")
            return None

    def wait_for_build_to_finish(self, job_name, build_number):
        """
        Waits for the Jenkins build to complete and returns the final result.
        :param job_name: The name of the Jenkins job.
        :param build_number: The build number to wait for.
        :return: The final result of the build (SUCCESS, FAILURE, etc.).
        """
        while True:
            status = self.get_build_status(job_name, build_number)
            if status is None:
                print("Build is still running. Waiting...")
                time.sleep(10)
            else:
                status = self.get_build_status(job_name, build_number)
                print(f"Build finished with result: {status}")
                return status

    def trigger_and_wait_for_output(self, job_name, parameters=None):
        """
        Triggers a job, waits for it to start, and retrieves its console output after completion.
        :param job_name: The name of the Jenkins job.
        :param parameters: Optional parameters to pass to the job.
        :return: JenkinsJob dataclass with job details.
        """
        # Step 1: Trigger the job and get the queue item number
        queue_item_number = self.trigger_job(job_name, parameters)

        if queue_item_number is None:
            print("Failed to trigger job.")
            return None

        job_url = f"{self.server.server}/job/{job_name}/"

        # Create the JenkinsJob object with basic details
        jenkins_job = JenkinsJob(job_name=job_name, job_url=job_url)

        # Step 2: Get the build number once the job starts
        build_number = self.get_build_number_from_queue(job_name, queue_item_number)

        if build_number is None:
            print("Failed to retrieve the build number.")
            return None

        jenkins_job.build_number = build_number

        # Step 3: Wait for the build to finish and get the result
        build_result = self.wait_for_build_to_finish(job_name, build_number)
        jenkins_job.status = build_result

        # Step 4: Retrieve the console output
        if build_result in ["SUCCESS", "FAILURE"]:
            console_output = self.get_console_output(job_name, build_number)
            if console_output:
                jenkins_job.console_output = console_output
                return jenkins_job
            else:
                print("Failed to retrieve console output.")
                return None
        else:
            print("Build did not complete successfully. No console output retrieved.")
            return jenkins_job
