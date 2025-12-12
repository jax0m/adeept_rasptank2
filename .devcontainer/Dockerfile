FROM ptrsr/pi-ci
RUN apt update && apt -y install apt-utils  && apt clean -y

RUN apt update && apt -y install git python3 pip python-is-python3 libcap-dev sudo && apt clean -y

RUN apt update && apt upgrade -y && apt autoremove -y && apt clean -y
# RUN pip install -U pip
