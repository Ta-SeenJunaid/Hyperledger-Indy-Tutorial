sudo apt-get update -y  && sudo apt-get install \
-y git wget python3.5 python3-pip python-setuptools \
python3-nacl apt-transport-https ca-certificates


sudo pip3 install -U 'pip<10.0.0' setuptools


sudo apt-key adv --keyserver keyserver.ubuntu.com \
--recv-keys CE7709D068DB5E88


sudo apt-key adv --keyserver keyserver.ubuntu.com \
--recv-keys BD33704C


sudo bash -c \
'echo "deb https://repo.sovrin.org/deb xenial master" >> /etc/apt/sources.list'


sudo bash -c \
'echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list'


sudo apt-get update -y && sudo apt-get install -y \
indy-node indy-plenum libindy indy-cli


sudo pip3 install python3-indy


sudo awk \
'{if (index($1, "NETWORK_NAME") != 0) {print("NETWORK_NAME = \"sandbox\"")} else print($0)}' /etc/indy/indy_config.py> /tmp/indy_config.py


sudo mv /tmp/indy_config.py /etc/indy/indy_config.py