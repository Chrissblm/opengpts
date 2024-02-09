# Backend Dockerfile
FROM python:3.11.7-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y unixodbc libmagic1 curl apt-transport-https lsb-release gnupg && rm -rf /var/lib/apt/lists/*

# Add Microsoft's packages.microsoft.com to trusted sources for Azure CLI and SQL ODBC
RUN curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/azure-cli.list && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install Azure CLI
RUN apt-get update && apt-get install -y azure-cli

# Install ODBC Driver 18 for SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Set the working directory
WORKDIR /backend

COPY . .

RUN rm poetry.lock

RUN pip install .

ENTRYPOINT [ "uvicorn", "app.server:app", "--host", "0.0.0.0" ]