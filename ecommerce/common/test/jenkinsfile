pipeline {
    agent any

    parameters {
        string(name: 'email', defaultValue: '', description: 'Enter your email')
        password(name: 'password', defaultValue: '', description: 'Enter your password')
        string(name: 'templatesId', defaultValue: '', description: 'Enter the template ID')
    }

    environment {
        // Define the path to the Python script (in the same folder as Jenkinsfile)
        PYTHON_SCRIPT = "${WORKSPACE}/script.py"
    }

    stages {
        stage('Setup') {
            steps {
                echo 'Setting up the environment'
                // Print the parameters for debug
                echo "Email: ${params.email}"
                echo "Template ID: ${params.templatesId}"
            }
        }

        stage('Run Python Script') {
            steps {
                echo 'Running Python script...'
                // Execute the Python script with the passed parameters
                sh """
                    python3 ${PYTHON_SCRIPT} \
                    --email ${params.email} \
                    --password ${params.password} \
                    --templatesId ${params.templatesId}
                """
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
        }
        failure {
            echo 'Pipeline failed!'
        }
        success {
            echo 'Pipeline succeeded!'
        }
    }
}
