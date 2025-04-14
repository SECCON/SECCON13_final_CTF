FROM ubuntu:24.04@sha256:72297848456d5d37d1262630108ab308d3e9ec7ed1c3286a32fe09856619a782 as mkimg

ENV DEBIAN_FRONTEND=noninteractive

RUN apt -y update --fix-missing
RUN apt -y install cpio

WORKDIR /work
COPY files/release/rootfs.cpio.gz .

WORKDIR ./rootfs
RUN gzip -d < ../rootfs.cpio.gz | cpio -iv

ARG FLAG
RUN echo "${FLAG}" > root/flag.txt
RUN chmod 440 root/flag.txt
RUN find . | cpio --quiet -o -H newc | gzip -c > ../rootfs.cpio.gz

FROM ubuntu:24.04@sha256:72297848456d5d37d1262630108ab308d3e9ec7ed1c3286a32fe09856619a782

ENV DEBIAN_FRONTEND=noninteractive

RUN apt -y update --fix-missing
RUN apt -y install xinetd
RUN apt -y install qemu-system-x86
RUN apt -y install hashcash
RUN groupadd -r pwn && useradd -r -g pwn pwn

COPY --chmod=640 build/pwn.xinetd /etc/xinetd.d/pwn
COPY --chmod=700 build/init.sh /etc/init.sh
RUN chmod 1733 /tmp /var/tmp /dev/shm

WORKDIR /home/pwn
COPY --chmod=750 build/pow.sh .
COPY --chmod=750 files/release/run.sh .
COPY files/release/bzImage .
COPY --from=mkimg /work/rootfs.cpio.gz .

RUN chown -R root:pwn /home/pwn
RUN chmod -R go-w /home/pwn
