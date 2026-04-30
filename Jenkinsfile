pipeline {
    agent any

    environment {
        PORT = "8501"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install streamlit wordcloud matplotlib pillow
                '''
            }
        }

        stage('Run Streamlit App') {
            steps {
                sh '''
                . venv/bin/activate

                nohup streamlit run app.py \
                    --server.port $PORT \
                    --server.address 0.0.0.0 \
                    > streamlit.log 2>&1 &
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Streamlit app started successfully!"
            echo "🌐 Open: http://<your-server-ip>:8501"
        }
        failure {
            echo "❌ Build failed"
        }
    }
}