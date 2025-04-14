#!/bin/sh

cd $(dirname $0)
timeout -sKILL 180 qemu-system-x86_64 \
	-kernel ./bzImage \
	-append "console=ttyS0 oops=panic panic=1 pti=on quiet" \
	-initrd ./rootfs.cpio.gz \
	-cpu kvm64,smap,smep \
	-m 64M \
	-monitor /dev/null \
	-nographic \
	-no-reboot \
	-net nic,model=virtio \
	-net user

