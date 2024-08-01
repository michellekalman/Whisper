#!/bin/bash

python -u HTTPServer.py &
sleep 2
python -u Whisper.py &
sleep 3
python -u Client.py &
python -u Client2.py &
sleep 15