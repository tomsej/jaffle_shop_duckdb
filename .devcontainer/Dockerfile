# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

COPY requirements.txt /tmp/pip-tmp/
# Install
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp \
   # Get Arch
   && arch_base=$(arch) \
   && arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) \
   # Install AWS CDK
   && npm install -g aws-cdk \
   && cd /tmp \
   # Install AWS cli
   && curl "https://awscli.amazonaws.com/awscli-exe-linux-${arch_base}.zip" -o "awscliv2.zip" \
   && unzip awscliv2.zip \
   && aws/install \
    # Install vegas credentials
   && curl -L "https://github.com/aripalo/vegas-credentials/releases/download/v0.14.4/vegas-credentials_0.14.4_linux_${arch}.tar.gz" -o "vegascreds.tar.gz" \
   && tar -xf vegascreds.tar.gz \
   && mv vegas-credentials /usr/bin/ \
   && chmod +x /usr/bin/vegas-credentials \
   # Persist bash history
   && SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
   && echo $SNIPPET >> "/root/.bashrc" \
   # Add dbt completion to bash
   && curl https://raw.githubusercontent.com/fishtown-analytics/dbt-completion.bash/master/dbt-completion.bash > ~/.dbt-completion.bash \
   && echo 'source ~/.dbt-completion.bash' >> ~/.bash_profile

USER root