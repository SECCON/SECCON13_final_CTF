FROM ubuntu:24.04

RUN apt update && apt install -y socat python3
RUN groupadd -r ctf && useradd -r -g ctf ctf
RUN chmod 1733 /tmp /var/tmp /dev/shm

WORKDIR /home/ctf
COPY --chmod=111 ./readflag /readflag
COPY lib lib
COPY --chmod=555 server.py server.py
RUN chown -R root:ctf /home/ctf
RUN chmod 555 lib/*

USER ctf
CMD socat TCP-L:9999,reuseaddr,fork EXEC:"./server.py",stderr
