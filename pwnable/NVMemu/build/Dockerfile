FROM ubuntu:24.04@sha256:72297848456d5d37d1262630108ab308d3e9ec7ed1c3286a32fe09856619a782

ENV DEBIAN_FRONTEND=noninteractive

RUN apt -y update --fix-missing
RUN apt -y install xinetd
RUN apt -y install libslirp0 libpixman-1-0 libpng16-16t64 libjpeg-turbo8 libsdl2-image-2.0-0 libglib2.0-0t64 libasound2t64 libpulse0 libsndio7.0
RUN apt -y install hashcash
RUN groupadd -r pwn && useradd -r -g pwn pwn

COPY --chmod=640 build/pwn.xinetd /etc/xinetd.d/pwn
COPY --chmod=700 build/init.sh /etc/init.sh
RUN chmod 1733 /tmp /var/tmp /dev/shm

WORKDIR /home/pwn
COPY --chmod=750 build/pow.sh pow.sh
COPY files/release .
RUN chmod a+x qemu-system-x86_64 run.sh

ARG FLAG
RUN echo "${FLAG}" > flag.txt
RUN chmod 440 flag.txt
RUN mv flag.txt flag-$(md5sum flag.txt | awk '{print $1}').txt

RUN chown -R root:pwn /home/pwn
RUN chmod -R go-w /home/pwn
