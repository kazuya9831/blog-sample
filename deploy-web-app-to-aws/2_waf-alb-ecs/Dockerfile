FROM --platform=linux/amd64 public.ecr.aws/amazonlinux/amazonlinux:2023

WORKDIR /usr/src/app

RUN dnf -y update && \
    dnf -y install gcc python3.11-setuptools.noarch python3.11-pip.noarch && \
    dnf clean all

COPY ./app/ ../Pipfile ../Pipfile.lock ./
RUN pip3.11 install pipenv
RUN pipenv install

CMD ["pipenv", "run", "gunicorn", "-b=0.0.0.0:8000", "-w=1", "views:app"]
