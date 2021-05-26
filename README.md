# Shadow Lab Streaming Layer (LSL)

Lab Streaming Layer (LSL) app for your Shadow Motion Capture System. Convert a
Shadow devkti stream into a LSL Stream Outlet. Runs as a command line Python
app.

## Install required packages

```
pip install -r requirements.txt
```

## Run the application

```
python main.py --help

usage: main.py [-h] [--header] [--host HOST] [--port PORT]

Read data from your Shadow mocap system and create a Stream Outlet for the Lab
Streaming Layer (LSL)

optional arguments:
  -h, --help   show this help message and exit
  --header     write header to the stream as per the XDF metadata spec
  --host HOST  IP address of your Shadow app
  --port PORT  port number of your Shadow app
```
