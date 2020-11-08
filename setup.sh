snap install firefox classic
sudo classic
apt-get install -y git python3 python3-setuptools build-essential software-properties-common python3-distutils
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install python3.8
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
echo "2\n" | update-alternatives --config python3
export LC_ALL=C
python3.8 -m easy_install pip
pip3 install -U pip
pip3 install -r requirements.txt

printf "[Unit]\nDescription = autoosball\n\n[Service]\nWorkingDirectory=/app\nExecStart=/app/start.sh\n\n[Install]\nWantedBy=multi-user.target\n" > /etc/systemd/system/autoosball.service
systemctl enable autoosball.service