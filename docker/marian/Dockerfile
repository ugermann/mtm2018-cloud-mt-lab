FROM ubuntu:16.04
RUN apt-get update && apt-get install -y \
    curl \
    git \
    libopenblas-base \
    libpcre3-dev \
    libtcmalloc-minimal4 \
    python3-websocket \
    python3-pip \
    python3-regex \
    wget

    
WORKDIR /marian
COPY . .

RUN ldd /marian/marian-server \
    | awk '/not found/ { print $1 }' \
    | sed 's/\.so\.//;s/_/-/g'\
    | xargs apt-get install -y 

CMD ["./marian-server","-c","model/decoder.yml"]
