#!/bin/bash

# Install necessary packages
apt-get update
apt-get install -y wget gnupg

# Install Firefox
apt-get install -y firefox-esr

# Install Geckodriver
GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep 'tag_name' | cut -d\" -f4)
wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz"
tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/
