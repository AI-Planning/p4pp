
FROM aiplanning/planutils:latest

RUN mkdir /PROJECT

COPY src/ /PROJECT/src
COPY setup.sh /PROJECT/setup.sh

WORKDIR /PROJECT

RUN ./setup.sh

CMD planutils activate
