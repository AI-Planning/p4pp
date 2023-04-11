
FROM aiplanning/planutils:latest

RUN pip3 install flask
RUN pip3 install flask-cors

COPY src/ /root/PROJECT
COPY setup.sh /root/PROJECT/setup.sh
RUN chmod +x /root/PROJECT/*.sh

WORKDIR /root/PROJECT

RUN ./setup.sh

CMD planutils activate
