#  URL Shortener Application

## Overview
This is a simple URL shortener application built using Python. It allows users to shorten URLs.

### POST api: 
This api is used for obtaining the shortened URL when we send a long URL

Endpoint: `/shorten`

Method: `POST`

Request Body:
`long_url`: The URL we want to shorten (it should be a string).
`expires_in`: The expiration time for the shortened URL in seconds. Defaults to 1 minute (60 seconds) if not provided.
            This is an integer and it is optional.

Example:
```
curl -X POST localhost:5000/shorten \
-H "Content-Type: application/json" \
-d '{"long_url": "https://www.google.com", "expires_in": 60}'
```
Successful Response:
```
{
  "short_url": "localhost:5000/1"
}

```
Failed Response:
```
{
  "error": "Error shortening URL"
}

```

### GET api: 
This API allows us to redirect the shortened URL to the long URL
T
Endpoint: `/<short_url>`

Method: `GET`

Usage: Replace `<short_url>` with the actual shortened URL suffix.

Example:
```
curl -X GET localhost:5000/abc123

```


Successful Response:
```

 Redirect to : "https://www.google.com"


```


Failed Response:
```
{
  "error": "URL has expired" 
            or
   "error": "URL not found" 
}


```
## Prerequisites
Please ensure that you have met the following requirements:
- Python 3.x
- Redis server
The installation instructions for Python and Redis server are given below

## Installation Instructions

### 1. Install Required Software

#### 1.1. Install Python
Ensure you have Python installed. You can check if Python is installed by running:

```
python --version
```
#### 1.2. Install Redis

##### 1.2.1 For Ubuntu/Debian:
```
sudo apt-get update
sudo apt-get install redis-server
```
##### 1.2.2 For macOs:
```
brew install redis
```

##### 1.2.3 For Windows: 
You can download Redis from the official website or use a package like Chocolatey:

```
choco install redis-64
```

### 2. Clone the Project

```
git clone https://github.com/gokulbalagopal/URLShortener.git
cd URLShortner
```
You can also transfer the files manually if you have the zip file


### 3. Set Up a Virtual Environment
Create and activate a virtual environment using the following commands:

```
# Create a virtual environment named 'env'
python -m venv env

# Activate the virtual environment
# On Windows
env\Scripts\activate

# On macOS/Linux
source env/bin/activate

```

### 4. Install Python Dependencies
With the virtual environment activated, install the necessary Python packages:

```
pip install -r requirements.txt

```

### 5. Initialize the SQLite Database
The app will automatically create the `instance/url_shortener.db` file when you run the app for the first time:

```
python app.py
```
Once you start adding the url to the app , you can view the data by stopping the remote server . For that quit the app.py file 
and run the following command to see the contents of the data base.

```
python show_db.py
```


### 6. Start Redis Server
To start the Redis server on your machine:

```
# On Ubuntu/Debian
sudo service redis-server start

# On macOS (using Homebrew)
brew services start redis

# On Windows (using Chocolatey)
redis-server

```

### 7. Run the Flask Application

```
python app.py

```

### 8. Access the Application
Go to the following url: :`http://localhost:5000/`, to acces the application.

