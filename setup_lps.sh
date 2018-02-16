sudo apt-get -y install python-pip
sudo apt-get -y install python3-pip
sudo pip3 install -r requirements.txt

python3 manage.py migrate

# Install Google Chrome
sudo apt-get -y install libxss1 libappindicator1 libindicator7 libnss libnss3
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
sudo apt-get -y install -f
sudo dpkg -i google-chrome*.deb


# Install chromedriver
CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
sudo apt-get -y install unzip;
sudo apt -y --fix-broken --fix-missing install
sudo apt-get -y update
sudo apt -y --fix-broken --fix-missing install
sudo apt-get -y install unzip;
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/
unzip ~/chromedriver_linux64.zip -d ~/
rm ~/chromedriver_linux64.zip
sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod 0755 /usr/local/bin/chromedriver


# Install xvfb
sudo apt-get -y install xvfb
Xvfb -ac :99 -screen 0 1280x1024x16 & export DISPLAY=:99


sudo python3 manage.py runserver 0.0.0.0:80
