#include <stddef.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>

#include "ioctl.h"
#include "endian.h"

static int nvme_submit_passthru(int fd, unsigned long ioctl_cmd, struct nvme_passthru_cmd *cmd, __u32 *result) {
	int err = ioctl(fd, ioctl_cmd, cmd);

	if (err >= 0 && result)
		*result = cmd->result;
	return err;
}

int nvme_submit_io_passthru(int fd, struct nvme_passthru_cmd *cmd, __u32 *result) {
	return nvme_submit_passthru(fd, NVME_IOCTL_IO_CMD, cmd, result);
}

int nvme_submit_admin_passthru(int fd, struct nvme_passthru_cmd *cmd, __u32 *result) {
	return nvme_submit_passthru(fd, NVME_IOCTL_ADMIN_CMD, cmd, result);
}

static int nvme_set_var_size_tags(__u32 *cmd_dw2, __u32 *cmd_dw3, __u32 *cmd_dw14, __u8 pif, __u8 sts, __u64 reftag, __u64 storage_tag) {
	__u32 cdw2 = 0, cdw3 = 0, cdw14;

	switch (pif) {
	case NVME_NVM_PIF_16B_GUARD:
		cdw14 = reftag & 0xffffffff;
		cdw14 |= ((storage_tag << (32 - sts)) & 0xffffffff);
		break;
	case NVME_NVM_PIF_32B_GUARD:
		cdw14 = reftag & 0xffffffff;
		cdw3 = reftag >> 32;
		cdw14 |= ((storage_tag << (80 - sts)) & 0xffff0000);
		if (sts >= 48)
			cdw3 |= ((storage_tag >> (sts - 48)) & 0xffffffff);
		else
			cdw3 |= ((storage_tag << (48 - sts)) & 0xffffffff);
		cdw2 = (storage_tag >> (sts - 16)) & 0xffff;
		break;
	case NVME_NVM_PIF_64B_GUARD:
		cdw14 = reftag & 0xffffffff;
		cdw3 = (reftag >> 32) & 0xffff;
		cdw14 |= ((storage_tag << (48 - sts)) & 0xffffffff);
		if (sts >= 16)
			cdw3 |= ((storage_tag >> (sts - 16)) & 0xffff);
		else
			cdw3 |= ((storage_tag << (16 - sts)) & 0xffff);
		break;
	default:
		errno = EINVAL;
		return -1;
	}

	*cmd_dw2 = cpu_to_be32(cdw2);
	*cmd_dw3 = cpu_to_be32(cdw3);
	*cmd_dw14 = cpu_to_be32(cdw14);
	return 0;
}

int nvme_io(struct nvme_io_args *args, __u8 opcode) {
	const size_t size_v1 = sizeof_args(struct nvme_io_args, dsm, __u64);
	//const size_t size_v2 = sizeof_args(struct nvme_io_args, pif, __u64);
	__u32 cdw2, cdw3, cdw10, cdw11, cdw12, cdw13, cdw14, cdw15;

	cdw10 = args->slba & 0xffffffff;
	cdw11 = args->slba >> 32;
	cdw12 = args->nlb | (args->control << 16);
	cdw13 = args->dsm | (args->dspec << 16);
	cdw15 = args->apptag | (args->appmask << 16);

	if (args->args_size == size_v1) {
		cdw2 = (args->storage_tag >> 32) & 0xffff;
		cdw3 = args->storage_tag & 0xffffffff;
		cdw14 = args->reftag;
	} else {
		if (nvme_set_var_size_tags(&cdw2, &cdw3, &cdw14,
				args->pif,
				args->sts,
				args->reftag_u64,
				args->storage_tag)) {
			return -1;
		}
	}

	struct nvme_passthru_cmd cmd = {
		.opcode		= opcode,
		.nsid		= args->nsid,
		.cdw2		= cdw2,
		.cdw3		= cdw3,
		.cdw10		= cdw10,
		.cdw11		= cdw11,
		.cdw12		= cdw12,
		.cdw13		= cdw13,
		.cdw14		= cdw14,
		.cdw15		= cdw15,
		.data_len	= args->data_len,
		.metadata_len	= args->metadata_len,
		.addr		= (__u64)(uintptr_t)args->data,
		.metadata	= (__u64)(uintptr_t)args->metadata,
		.timeout_ms	= args->timeout,
	};

	return nvme_submit_io_passthru(args->fd, &cmd, args->result);
}

int nvme_io_mgmt_recv(struct nvme_io_mgmt_recv_args *args) {
	__u32 cdw10 = args->mo | (args->mos << 16);
	__u32 cdw11 = (args->data_len >> 2) - 1;

	struct nvme_passthru_cmd cmd = {
		.opcode		= nvme_cmd_io_mgmt_recv,
		.nsid		= args->nsid,
		.cdw10		= cdw10,
		.cdw11		= cdw11,
		.addr		= (__u64)(uintptr_t)args->data,
		.data_len	= args->data_len,
		.timeout_ms	= args->timeout,
	};

	return nvme_submit_io_passthru(args->fd, &cmd, NULL);
}

int nvme_zns_mgmt_recv(struct nvme_zns_mgmt_recv_args *args) {
	__u32 cdw10 = args->slba & 0xffffffff;
	__u32 cdw11 = args->slba >> 32;
	__u32 cdw12 = (args->data_len >> 2) - 1;
	__u32 cdw13 = NVME_SET(args->zra, ZNS_MGMT_RECV_ZRA) |
			NVME_SET(args->zrasf, ZNS_MGMT_RECV_ZRASF) |
			NVME_SET(args->zras_feat, ZNS_MGMT_RECV_ZRAS_FEAT);

	struct nvme_passthru_cmd cmd = {
		.opcode		= nvme_zns_cmd_mgmt_recv,
		.nsid		= args->nsid,
		.cdw10		= cdw10,
		.cdw11		= cdw11,
		.cdw12		= cdw12,
		.cdw13		= cdw13,
		.addr		= (__u64)(uintptr_t)args->data,
		.data_len	= args->data_len,
		.timeout_ms	= args->timeout,
	};

	if (args->args_size < sizeof(*args)) {
		errno = EINVAL;
		return -1;
	}
	return nvme_submit_io_passthru(args->fd, &cmd, args->result);
}

int nvme_format_nvm(struct nvme_format_nvm_args *args) {
	const size_t size_v1 = sizeof_args(struct nvme_format_nvm_args, lbaf, __u64);
	const size_t size_v2 = sizeof_args(struct nvme_format_nvm_args, lbafu, __u64);
	__u32 cdw10;

	if (args->args_size < size_v1 || args->args_size > size_v2) {
		errno = EINVAL;
		return -1;
	}

	cdw10 = NVME_SET(args->lbaf, FORMAT_CDW10_LBAF) |
		NVME_SET(args->mset, FORMAT_CDW10_MSET) |
		NVME_SET(args->pi, FORMAT_CDW10_PI) |
		NVME_SET(args->pil, FORMAT_CDW10_PIL) |
		NVME_SET(args->ses, FORMAT_CDW10_SES);

	if (args->args_size == size_v2) {
		/* set lbafu extension */
		cdw10 |= NVME_SET(args->lbafu, FORMAT_CDW10_LBAFU);
	}

	struct nvme_passthru_cmd cmd = {
		.opcode		= nvme_admin_format_nvm,
		.nsid		= args->nsid,
		.cdw10		= cdw10,
		.timeout_ms	= args->timeout,
	};

	return nvme_submit_admin_passthru(args->fd, &cmd, args->result);
}

