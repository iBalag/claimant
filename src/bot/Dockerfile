FROM python:3.8.12-alpine AS compile-image
RUN mkdir claimant
RUN apk add --no-cache gcc g++ musl-dev libffi-dev openssl-dev cargo build-base
COPY requirements.txt /claimant/requirements.txt
RUN pip install -r /claimant/requirements.txt --user

FROM python:3.8.12-alpine AS run-image
COPY --from=compile-image /root/.local /root/.local
COPY --from=compile-image claimant claimant
ENV PATH=/root/.local/bin:$PATH
COPY . claimant
WORKDIR claimant
CMD ["python", "bot.py", "-e", "dev"]