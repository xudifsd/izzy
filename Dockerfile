FROM ubuntu:16.04

RUN apt -y update && \
    apt -y install \
      curl \
      python \
      python-pip \
      unzip \
      make

RUN pip install flask \
        protobuf \
        numpy \
        scipy

RUN curl -OL https://github.com/google/protobuf/releases/download/v3.4.0/protoc-3.4.0-linux-x86_64.zip

RUN unzip protoc-3.4.0-linux-x86_64.zip -d protoc3

RUN mv protoc3/bin/* /usr/local/bin/

RUN mv protoc3/include/* /usr/local/include/

RUN rm -rf protoc-3.4.0-linux-x86_64.zip protoc3/

ENV PATH="${PATH}:/usr/local/bin"

COPY . /app

WORKDIR /app

CMD ["make", "web"]
