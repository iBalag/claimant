FROM python:3.8.12-buster
RUN mkdir claimant
COPY requirements.txt /claimant/requirements.txt
RUN pip install -r /claimant/requirements.txt
COPY . claimant
WORKDIR claimant
CMD ["python", "bot.py", "-e", "prod"]