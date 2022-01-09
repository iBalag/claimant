FROM python:3.8.12-buster
RUN mkdir claimant
WORKDIR claimant
RUN pip install -r /claimant/requirements.txt
COPY . claimant
CMD ["python", "bot.py", "-e", "prod"]