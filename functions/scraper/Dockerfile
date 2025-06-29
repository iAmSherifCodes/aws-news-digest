ARG FUNCTION_DIR="/scraper"

FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy AS build-image

RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev \
  software-properties-common \
  fonts-liberation \
  libappindicator3-1 \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libcups2 \
  libdbus-1-3 \
  libgdk-pixbuf2.0-0 \
  libnspr4 \
  libnss3 \
  pciutils \
  xdg-utils

ARG FUNCTION_DIR

RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

RUN pip install \
    --target ${FUNCTION_DIR} \
        awslambdaric

COPY requirements.txt .
RUN pip install --target ${FUNCTION_DIR} -r requirements.txt

FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "python", "-m", "awslambdaric" ]

CMD [ "app.lambda_handler" ]