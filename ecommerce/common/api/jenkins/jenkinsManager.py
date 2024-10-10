import time
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass


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
        self.jenkins_url = jenkins_url
        self.auth = HTTPBasicAuth(username, api_token)

    def trigger_job(self, job_name, parameters=None):
        """
        Triggers a Jenkins job (pipeline) with or without parameters and returns the queue URL.
        :param job_name: The name of the Jenkins job to trigger.
        :param parameters: Optional dictionary of parameters to pass to the job.
        :return: The queue URL of the triggered job or None on failure.
        """
        if parameters:
            trigger_url = f"{self.jenkins_url}/job/{job_name}/buildWithParameters"
        else:
            trigger_url = f"{self.jenkins_url}/job/{job_name}/build"

        try:
            response = requests.post(trigger_url, auth=self.auth, data=parameters)

            if response.status_code == 201:
                queue_url = response.headers.get('Location')
                print(f"Job '{job_name}' triggered successfully. Queue URL: {queue_url}")
                return queue_url
            else:
                print(f"Failed to trigger job. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"An error occurred while triggering the job: {str(e)}")
            return None

    def get_build_number_from_queue(self, queue_url):
        """
        Retrieves the build number of the job once it starts from the queue URL.
        :param queue_url: The queue URL returned after triggering the job.
        :return: The build number of the job.
        """
        while True:
            try:
                response = requests.get(f"{queue_url}api/json", auth=self.auth)
                if response.status_code == 200:
                    data = response.json()
                    if 'executable' in data:
                        build_number = data['executable']['number']
                        print(f"Job started. Build number: {build_number}")
                        return build_number
                    else:
                        print("Job is still in the queue. Waiting for it to start...")
                        time.sleep(5)  # Wait 5 seconds before retrying
                else:
                    print(f"Failed to get build number from queue. Status code: {response.status_code}")
                    return None
            except Exception as e:
                print(f"An error occurred while getting the build number: {str(e)}")
                return None

    def get_console_output(self, job_name, build_number):
        """
        Retrieves the console output of a specific Jenkins job build.
        :param job_name: The name of the Jenkins job.
        :param build_number: The build number to retrieve the console output for.
        :return: The console output as a string.
        """
        console_url = f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText"

        try:
            response = requests.get(console_url, auth=self.auth)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to retrieve console output. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"An error occurred while retrieving the console output: {str(e)}")
            return None

    def get_build_status(self, job_name, build_number):
        """
        Retrieves the status of a specific Jenkins build.
        :param job_name: The name of the Jenkins job.
        :param build_number: The build number to check the status for.
        :return: The result of the build (SUCCESS, FAILURE, etc.), or None if not found.
        """
        build_status_url = f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json"

        try:
            response = requests.get(build_status_url, auth=self.auth)
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                if result:
                    print(f"Build result: {result}")
                    return result
                else:
                    print(f"Build is still running. No result yet.")
                    return None
            else:
                print(f"Failed to retrieve build status. Status code: {response.status_code}")
                return None
        except Exception as e:
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
            result = self.get_build_status(job_name, build_number)
            if result is None:
                print("Build is still running. Waiting...")
                time.sleep(10)  # Wait 10 seconds before checking again
            else:
                print(f"Build finished with result: {result}")
                return result

    def trigger_and_wait_for_output(self, job_name, parameters=None):
        """
        Triggers a job, waits for it to start, and retrieves its console output after completion.
        :param job_name: The name of the Jenkins job.
        :param parameters: Optional parameters to pass to the job.
        :return: JenkinsJob dataclass with job details.
        """
        # Step 1: Trigger the job and get the queue URL
        queue_url = self.trigger_job(job_name, parameters)

        if queue_url is None:
            print("Failed to trigger job.")
            return None

        job_url = f"{self.jenkins_url}/job/{job_name}/"

        # Create the JenkinsJob object with basic details
        jenkins_job = JenkinsJob(job_name=job_name, job_url=job_url)

        # Step 2: Get the build number once the job starts
        build_number = self.get_build_number_from_queue(queue_url)

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

