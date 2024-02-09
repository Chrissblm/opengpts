### using for finding IP address  nslookup nextgen.redis.cache.windows.net


### *** fix for Pyodbc issue

Used this in the docker https://github.com/mkleehammer/pyodbc/issues/1124 
    - poetry add pyodbc==5.1.0

used this in the venv conda
    poetry install
    # make sure this runs successfully
    odbcinst -j

    export LDFLAGS="-L$(brew --prefix unixodbc)/lib"
    export CPPFLAGS="-I$(brew --prefix unixodbc)/include"
    pip3 install --no-cache-dir --no-binary :all: pyodbc

    pip uninstall pyodbc
    pip cache remove pyodbc
    pip install --no-binary :all: pyodbc


### *** Fix for pyodbc issue
    Uninstall M1 versions of brew packages (if installed at all):
        brew uninstall unixodbc msodbcsql18 mssql-tools freetds
        odbcinst -u -d -n "ODBC Driver 18 for SQL Server"
    
    Install x86 Homebrew alongside the ARM M1 homebrew:
        arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    
    Then use x86 homebrew like arch -x86_64 /usr/local/bin/brew install or use the following alias (add to ~/.bash_profile)

        # Relies on having installed x86 brew like:
        # arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
        alias x86brew="arch -x86_64 /usr/local/bin/brew"
        alias brew="/opt/homebrew/bin/brew"  # M1 version, to avoid from using x86 version accidentally

    Install the ODBC packages.
    
        x86brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
        x86brew update
        HOMEBREW_ACCEPT_EULA=Y x86brew install msodbcsql18 mssql-tools

    new Conda Env
        ENV_NAME="opengp"
        CONDA_SUBDIR=osx-64 conda create -n $ENV_NAME python=3.11
        conda activate $ENV_NAME
        conda config --env --set subdir osx-64

### *** Settings for RBAC
#!/bin/bash

subscription_id="5ef8ab16-8890-4bb5-a672-a30c1e48da69"
resource_group="rg-mvp-opengpt"

az ad sp create-for-rbac --name "opengpt" --role contributor \
                         --scopes /subscriptions/$subscription_id/resourceGroups/$resource_group \
                         --sdk-auth


    The output should be
            {
            "clientId": "client-id",
            "clientSecret": "client-secret",
            "subscriptionId": "subscription-id",
            "tenantId": "tenant-id",
            ...
            }

    export AZURE_CLIENT_ID="client-id"
    export AZURE_CLIENT_SECRET="client-secret"
    export AZURE_TENANT_ID="tenant-id"