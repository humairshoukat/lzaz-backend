## Setting up the Project

```bash
# Make sure you have Python, Git, and Docker Desktop installed in your machine
# Clone the repo in your repective foler
$ git clone https://github.com/Lzaz-com/PIM_Backend

# After successfully cloning the repo, go the project folder
$ cd PIM_Backend

# Setup the virtual environment
$ python -m venv venv

# Activate the virtual environment
$ venv\Scripts\activate

# If you're unable to activate the venv OR if you get the error running/execution scripts are disabled, 
# If you're using windows, Fix it by following the below instruction:
# Open your Windows Powershell by running it as Administrator and run the following command and enter 'Y':
$ Set-ExecutionPolicy RemoteSigned
# Issue will get fixed, and now activate the virtual environment again and follow the next instructions.

```

## Running the Project

```bash
# Install the requirements 
$ pip install -r requirements.txt

# Run the docker compose command
$ docker-compose up

# Access the adminer using the following URL in the browser
$ http://localhost:4444/

# Login using the following credentials
# Username: root
# Password: root

# Now Create the database for your project and go back to the project terminal

# Create & Setup the .env file by using example.env file from the project files

# Run the migrations
$ python manage.py migrate

# Run the Project
$ python manage.py runserver

# Your can access the project on the following URL
$ http://127.0.0.1:8000/

```