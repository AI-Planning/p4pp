
FROM aiplanning/planutils:latest

COPY src/ /PROJECT
COPY setup.sh /PROJECT/setup.sh

WORKDIR /PROJECT

RUN ./setup.sh

CMD planutils activate
