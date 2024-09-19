FROM gitpod/workspace-python-3.9

# Install dependencies
USER root

# Install MySQL client
RUN apt-get update && apt-get install -y mysql-client

# Set up pyenv for the Gitpod user
USER gitpod
