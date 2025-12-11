FROM ptrsr/pi-ci
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y && apt-get clean -y
RUN apt-get update && apt-get -y install apt-utils  && apt-get clean -y
RUN apt-get update && apt-get -y install git python3 pip python-is-python3 libcap-dev && apt-get clean -y
# RUN pip install -U pip
