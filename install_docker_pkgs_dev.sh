#!/bin/bash

# Help debugging shell script
set -euo pipefail

# We never will give feedback
export DEBIAN_FRONTEND=noninteractive

# Update package deps
apt-get update

# Install required packages
apt-get -y install --no-install-recommends nano vim less git

# Cleanup
apt-get clean
rm -rf /var/lib/apt/lists/*