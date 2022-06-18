
FROM aiplanning/planutils:latest

RUN mkdir /PROJECT

COPY grade.py /PROJECT/grade.py
COPY merge.py /PROJECT/merge.py
COPY plan.sh /PROJECT/plan.sh
COPY setup.sh /PROJECT/setup.sh
COPY validate.sh /PROJECT/validate.sh

WORKDIR /PROJECT

RUN ./setup.sh

CMD planutils activate
