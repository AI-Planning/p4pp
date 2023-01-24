
FROM aiplanning/planutils:latest

COPY src/ /root/PROJECT
COPY setup.sh /root/PROJECT/setup.sh
RUN chmod +x /root/PROJECT/*.sh

WORKDIR /root/PROJECT

RUN ./setup.sh

CMD planutils activate
