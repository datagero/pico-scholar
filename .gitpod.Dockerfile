FROM gitpod/workspace-python-3.9

# Install dependencies
USER root

# Install MySQL client
RUN apt-get update && apt-get install -y mysql-client

# Set up pyenv for the Gitpod user
USER gitpod

# # Install Python 3.9.6 using pyenv and install dependencies
# RUN pyenv install 3.9.6 && \
#     pyenv global 3.9.6 && \
    # pip install --upgrade pip && \
    # pip install -r /workspace/pico-scholar/backend/requirements.txt
