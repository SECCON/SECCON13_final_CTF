#!/bin/sh

cd $(dirname $0)
file=$(mktemp -p /tmp nvme-XXXXXXXX.img) && {
	truncate -s 128M $file

	timeout -sKILL 180 ./qemu-system-x86_64 \
		-L ./pc-bios \
		-kernel ./bzImage \
		-append "console=ttyS0 oops=panic panic=1 quiet" \
		-cpu kvm64,smap,smep \
		-m 64M \
		-initrd ./rootfs.cpio.gz \
		-monitor /dev/null \
		-nographic \
		-no-reboot \
		-device nvme,serial=1234 \
		-device nvme-ns,drive=nvm-1,nsid=1,zoned=on \
		-drive file=$file,if=none,format=raw,id=nvm-1 \
		-net nic,model=virtio \
		-net user

	rm -v $file
}

