# How to setup database environment

1. create global environment variable, by running

```shell
   touch ~/.bashrc
```

2. open the file and add the following at the end

```shell
export DATABASE_USERNAME=sql8507066 # replace with database username
export DATABASE_PASSWORD=8Dh6qETGM5 # replace with databse password
export DATABASE_HOST=sql8.freemysqlhosting.net # replace with database host
export DATABASE_PORT=3306 # replace if needed but mysql port is always accessed via this port
export DATABASE_DB_NAME=sql8507066 # replace with database name
```

3. Refresh environment by running 

```shell
source ~/.bashrc
```

# Running the application as a background process