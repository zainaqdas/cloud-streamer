#!/bin/bash
# install ffmpeg
apt-get update
apt-get install -y ffmpeg

# install python dependencies
pip install -r requirements.txt
