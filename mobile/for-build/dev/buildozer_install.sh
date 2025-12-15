After installing buildozer in venv, you can run the following commands to install the required packages for buildozer:
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool \
    pkg-config zlib1g-dev libncurses-dev libtinfo6 cmake libffi-dev libssl-dev

Then the following to ~/.bashrc file in home directory:
export PATH=$PATH:~/.local/bin/

python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade Cython==0.29.33 virtualenv