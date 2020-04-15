FROM debian:buster

WORKDIR /APP
VOLUME /data

RUN apt update \
    && apt install -y \
    ca-certificates \
    python3-pip \
    python3.7-dev \
    python3-lxml libxml2-dev libxslt-dev

# Added piwheels to make the builds faster
ARG TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ] || [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    printf "[global]\nextra-index-url=https://www.piwheels.org/simple" | touch /etc/pip.conf; \
    fi

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN update-ca-certificates -f -v

ENV APP_ENV=docker

CMD ["flask", "run", "--host", "0.0.0.0"]

COPY . ./