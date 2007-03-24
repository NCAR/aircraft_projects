/*
 * timepps.h -- PPS API main header
 *
 *
 * Copyright (C) 2005-2006   Rodolfo Giometti <giometti@linux.it>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the Free Software
 *   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 * NOTE: this file is *strongly* based on a previous job by Ulrich Windl.
 *       The original copyright note follows:
 *
 *    Interface to the PPS API described in RFC 2783 (March 2000)
 *
 *    Copyright (c) 1999, 2001, 2004 by Ulrich Windl,
 * 	   based on code by Reg Clemens <reg@dwf.com>
 *	   based on code by Poul-Henning Kamp <phk@FreeBSD.org>
 *
 *    ----------------------------------------------------------------------
 *    "THE BEER-WARE LICENSE" (Revision 42):
 *    <phk@FreeBSD.org> wrote this file.  As long as you retain this notice
 *    you can do whatever you want with this stuff. If we meet some day, and
 *    you think this stuff is worth it, you can buy me a beer in return.
 *       Poul-Henning Kamp
 *    ----------------------------------------------------------------------
 */

#ifndef _SYS_TIMEPPS_H_
#define _SYS_TIMEPPS_H_

/* Implementation note: the logical states ``assert'' and ``clear''
 * are implemented in terms of the chip register, i.e. ``assert''
 * means the bit is set.  */

/* --- 3.2 New data structures --------------------------------------------- */

#define PPS_API_VERS_2		2	/* LinuxPPS proposal, dated 2006-05 */
#define PPS_API_VERS		PPS_API_VERS_2
#define LINUXPSS_API		1	/* mark LinuxPPS API */
#define NETLINK_PPSAPI		17	/* we use just one free number... */

typedef struct pps_handle_s {
	int source;
	int socket;
} pps_handle_t;				/* represents a PPS source */

typedef unsigned long pps_seq_t;	/* sequence number */

typedef struct ntp_fp {
	unsigned int	integral;
	unsigned int	fractional;
} ntp_fp_t;				/* NTP-compatible time stamp */

typedef union pps_timeu {
	struct timespec tspec;
	ntp_fp_t ntpfp;
	unsigned long longpad[3];
} pps_timeu_t;				/* generic data type to represent time stamps */

typedef struct pps_info {
	pps_seq_t	assert_sequence;	/* seq. num. of assert event */
	pps_seq_t	clear_sequence;		/* seq. num. of clear event */
	pps_timeu_t	assert_tu;		/* time of assert event */
	pps_timeu_t	clear_tu;		/* time of clear event */
	int		current_mode;		/* current mode bits */
} pps_info_t;

#define assert_timestamp        assert_tu.tspec
#define clear_timestamp         clear_tu.tspec

#define assert_timestamp_ntpfp  assert_tu.ntpfp
#define clear_timestamp_ntpfp   clear_tu.ntpfp

typedef struct pps_params {
	int		api_version;	/* API version # */
	int		mode;		/* mode bits */
	pps_timeu_t assert_off_tu;	/* offset compensation for assert */
	pps_timeu_t clear_off_tu;	/* offset compensation for clear */
} pps_params_t;

#define assert_offset   assert_off_tu.tspec
#define clear_offset    clear_off_tu.tspec

#define assert_offset_ntpfp     assert_off_tu.ntpfp
#define clear_offset_ntpfp      clear_off_tu.ntpfp

/* --- 3.3 Mode bit definitions -------------------------------------------- */

/* Device/implementation parameters */
#define PPS_CAPTUREASSERT	0x01	/* capture assert events */
#define PPS_CAPTURECLEAR	0x02	/* capture clear events */
#define PPS_CAPTUREBOTH		0x03	/* capture assert and clear events */

#define PPS_OFFSETASSERT	0x10	/* apply compensation for assert ev. */
#define PPS_OFFSETCLEAR		0x20	/* apply compensation for clear ev. */

#define PPS_CANWAIT		0x100	/* Can we wait for an event? */
#define PPS_CANPOLL		0x200	/* "This bit is reserved for
                                           future use." */

/* Kernel actions */
#define PPS_ECHOASSERT		0x40	/* feed back assert event to output */
#define PPS_ECHOCLEAR		0x80	/* feed back clear event to output */

/* Timestamp formats */
#define PPS_TSFMT_TSPEC		0x1000	/* select timespec format */
#define PPS_TSFMT_NTPFP		0x2000	/* select NTP format */

/* --- 3.4.4 New functions: disciplining the kernel timebase --------------- */

/* Kernel consumers */
#define PPS_KC_HARDPPS		0	/* hardpps() (or equivalent) */
#define PPS_KC_HARDPPS_PLL	1	/* hardpps() constrained to
					   use a phase-locked loop */
#define PPS_KC_HARDPPS_FLL	2	/* hardpps() constrained to
					   use a frequency-locked loop */

/* --- Here begins the implementation-specific part! ----------------------- */

#define LINUXPPS_MAX_NAME_LEN           32
struct pps_netlink_msg {
	int cmd;			  /* the command to execute */
	int source;
	char name[LINUXPPS_MAX_NAME_LEN]; /* symbolic name */
	char path[LINUXPPS_MAX_NAME_LEN]; /* path of the connected device */
	int consumer;			  /* selected kernel consumer */
	pps_params_t params;
	int mode;			  /* edge */
	int tsformat;			  /* format of time stamps */
	pps_info_t info;
	struct timespec timeout;
	int ret;
};
#define PPSAPI_MAX_PAYLOAD	sizeof(struct pps_netlink_msg)

/* check Documentation/ioctl-number.txt! */
#define PPS_CREATE		1
#define PPS_DESTROY		2
#define PPS_SETPARMS		3
#define PPS_GETPARMS		4
#define PPS_GETCAP		5
#define PPS_FETCH		6
#define PPS_KC_BIND		7
#define PPS_FIND_SRC		8
#define PPS_FIND_PATH		9

#ifdef __KERNEL__

#include <linux/socket.h>
#include <net/sock.h>
#include <linux/netlink.h>

struct pps_state {
	pps_params_t	parm;		  /* PPS parameters */
	pps_info_t info;		  /* PPS information */
	int cap;			  /* PPS capabilities */
	long ecount;			  /* interpolation offset of event */
	struct timespec etime;		  /* kernel time of event */
	wait_queue_head_t ewait;	  /* wait queue for event */
};

/* State variables to bind kernel consumer */
/* PPS API (RFC 2783): current source and mode for ``kernel consumer'' */
extern const struct pps *pps_kc_hardpps_dev; /* some unique pointer to device */
extern int pps_kc_hardpps_mode;		     /* mode bits for kernel consumer */

/* Return allowed mode bits for given pps struct, file's mode, and user.
 * Bits set in `*obligatory' must be set.  Returned bits may be set. */
extern int pps_allowed_mode(const struct pps *pps, mode_t fmode, int *obligatory);

#else /* !__KERNEL__ */

/* --- 3.4 Functions ------------------------------------------------------- */

#include <unistd.h>
#include <errno.h>
#include <asm/types.h>
#include <sys/socket.h>
#include <linux/netlink.h>

/* Private functions */

static int netlink_msg(int socket, struct pps_netlink_msg *nlpps)
{
	struct sockaddr_nl dest_addr;
	struct nlmsghdr *nlh;
	struct iovec iov;
	struct msghdr msg;

	int ret;

	memset(&msg, 0, sizeof(msg));

	/* Create the destination address */
	memset(&dest_addr, 0, sizeof(dest_addr));
	dest_addr.nl_family = AF_NETLINK;
	dest_addr.nl_pid = 0;          /* for the kernel */
	dest_addr.nl_groups = 0;       /* not in mcast groups */

	nlh = (struct nlmsghdr *) alloca(NLMSG_SPACE(PPSAPI_MAX_PAYLOAD));
	if (nlh == NULL)
		return -1;

	/* Fill the netlink message header */
	nlh->nlmsg_len = NLMSG_SPACE(PPSAPI_MAX_PAYLOAD);
	nlh->nlmsg_pid = getpid();
	nlh->nlmsg_flags = 0;
	memcpy(NLMSG_DATA(nlh), nlpps, sizeof(struct pps_netlink_msg));

	iov.iov_base = (void *) nlh;
	iov.iov_len = nlh->nlmsg_len;
	msg.msg_name = (void *) &dest_addr;
	msg.msg_namelen = sizeof(dest_addr);
	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;

	/* Send the message */
	ret = sendmsg(socket, &msg, 0);
	if (ret < 0)
		return ret;

	/* Wait for the answer */
	memset(nlh, 0, NLMSG_SPACE(PPSAPI_MAX_PAYLOAD));
	ret = recvmsg(socket, &msg, 0);
	if (ret < 0)
		return ret;

	/* Check the return value */
	memcpy(nlpps, NLMSG_DATA(nlh), sizeof(struct pps_netlink_msg));
	if (nlpps->ret < 0) {
		errno = -nlpps->ret;
		return -1;
	}

	return 0;
}

/* The PPSAPI functions */

/* Create PPS handle from source number */
static __inline int time_pps_create(int source, pps_handle_t *handle)
{
	struct sockaddr_nl src_addr, dest_addr;
	struct pps_netlink_msg nlpps;

	int ret;

	/* Create the netlink socket */
	ret = socket(PF_NETLINK, SOCK_RAW, NETLINK_PPSAPI);
	if (ret < 0)
		return ret;
	handle->socket = ret;

	/* Bind the socket with the source address */
	memset(&src_addr, 0, sizeof(src_addr));
	src_addr.nl_family = AF_NETLINK;
	src_addr.nl_pid = 0;		/* ask kernel to choose an unique ID */
	src_addr.nl_groups = 0;		/* not in mcast groups */
	ret = bind(handle->socket, (struct sockaddr *) &src_addr, sizeof(src_addr));
	if (ret < 0) {
		close(handle->socket);
		return ret;
	}

	/* Now ask the kernel to create the PPS source */
	nlpps.cmd = PPS_CREATE;
	nlpps.source = source;
	ret = netlink_msg(handle->socket, &nlpps);
	if (ret < 0)
		return ret;

	/* Save the PPS source returned by the kernel */
	handle->source = nlpps.source;

	return 0;
}

/* Release PPS handle */
static __inline int time_pps_destroy(pps_handle_t handle)
{
	struct pps_netlink_msg nlpps;

	int ret;

	/* Ask the kernel to destroy the PPS source */
	nlpps.cmd = PPS_DESTROY;
	nlpps.source = handle.source;
	ret = netlink_msg(handle.socket, &nlpps);
	if (ret < 0)
		return ret;

	/* Now we can destroy the netlink socket */
	close(handle.socket);

	return 0;
}

/* Set parameters for handle */
static __inline int time_pps_setparams(pps_handle_t handle, const pps_params_t *ppsparams)
{
	struct pps_netlink_msg nlpps;

	int ret;

	/* Ask the kernel to set the new PPS source's parameters */
	nlpps.cmd = PPS_SETPARMS;
	nlpps.source = handle.source;
	nlpps.params = *ppsparams;
	ret = netlink_msg(handle.socket, &nlpps);
	if (ret < 0)
		return ret;

	return 0;
}

static __inline int time_pps_getparams(pps_handle_t handle, pps_params_t *ppsparams)
{
	struct pps_netlink_msg nlpps;

	int ret;

	/* Ask the kernel to return the PPS source's parameters */
	nlpps.cmd = PPS_GETPARMS;
	nlpps.source = handle.source;
	ret = netlink_msg(handle.socket, &nlpps);
	if (ret < 0)
		return ret;

	/* Return the parameters */
	*ppsparams = nlpps.params; 

	return 0;
}

/* Get capabilities for handle */
static __inline int time_pps_getcap(pps_handle_t handle, int *mode)
{
	struct pps_netlink_msg nlpps;

	int ret;

	/* Ask the kernel to return the PPS source's capabilities */
	nlpps.cmd = PPS_GETCAP;
	nlpps.source = handle.source;
	ret = netlink_msg(handle.socket, &nlpps);
	if (ret < 0)
		return ret;

	/* Return the capabilities */
	*mode = nlpps.mode; 

	return 0;
}

/* current event for handle */
static __inline int time_pps_fetch(pps_handle_t handle, const int tsformat, pps_info_t *ppsinfobuf, const struct timespec *timeout)
{
	struct pps_netlink_msg nlpps;

	int ret;

	/* Ask the kernel to return the PPS source's capabilities */
	nlpps.cmd = PPS_FETCH;
	nlpps.source = handle.source;
	nlpps.tsformat = tsformat;
	if (timeout)
		nlpps.timeout = *timeout;
	else	 /* wait forever */
		nlpps.timeout.tv_sec = nlpps.timeout.tv_nsec = -1;

	ret = netlink_msg(handle.socket, &nlpps);
	if (ret < 0)
		return ret;

	/* Return the timestamps */
	*ppsinfobuf = nlpps.info; 

	return 0;
}

/* Specify kernel consumer */
static __inline int time_pps_kcbind(pps_handle_t handle, const int kernel_consumer, const int edge, const int tsformat)
{
	struct pps_netlink_msg nlpps;

	int ret;

	/* Ask the kernel to destroy the PPS source */
	nlpps.cmd = PPS_KC_BIND;
	nlpps.source = handle.source;
	nlpps.consumer = kernel_consumer;
	nlpps.mode = edge;
	nlpps.tsformat = tsformat;
	ret = netlink_msg(handle.socket, &nlpps);
	if (ret < 0)
		return ret;

	return 0;
}

/* Find a PPS source */
#define PPS_HAVE_FINDSOURCE	1
static __inline int time_pps_findsource(int index, char *path, int pathlen, char *idstring, int idlen)
{
	int sock;
	struct sockaddr_nl src_addr, dest_addr;
	struct pps_netlink_msg nlpps;

	int ret;

	/* Create the netlink socket */
	ret = socket(PF_NETLINK, SOCK_RAW, NETLINK_PPSAPI);
	if (ret < 0)
		return ret;
	sock = ret;

	/* Bind the socket with the source address */
	memset(&src_addr, 0, sizeof(src_addr));
	src_addr.nl_family = AF_NETLINK;
	src_addr.nl_pid = 0;		/* ask kernel to choose an unique ID */
	src_addr.nl_groups = 0;		/* not in mcast groups */
	ret = bind(sock, (struct sockaddr *) &src_addr, sizeof(src_addr));
	if (ret < 0) {
		close(sock);
		return ret;
	}

	/* Ask the kernel to destroy the PPS source */
	nlpps.cmd = PPS_FIND_SRC;
	nlpps.source = index;
	ret = netlink_msg(sock, &nlpps);
	if (ret < 0) {
		close(sock);
		return ret;
	}

	strncpy(path, nlpps.path, pathlen);
	strncpy(idstring, nlpps.name, idlen);

	close(sock);
	return nlpps.source;
}

#define PPS_HAVE_FINDPATH	1
static __inline void time_pps_readlink(char *link, int linklen, char *path, int pathlen)
{
	int i;

	i = readlink(link, path, pathlen-1);
	if (i <= 0) {
		/* "link" is not a valid symbolic so we directly use it */
		strncpy(path, link, linklen <= pathlen ? linklen : pathlen);
		return;
	}

	/* Return the file name where "link" points to */
	path[i] = '\0';
	return;
}

static __inline int time_pps_findpath(char *path, int pathlen, char *idstring, int idlen)
{
	int sock;
	struct sockaddr_nl src_addr, dest_addr;
	struct pps_netlink_msg nlpps;

	int ret;

	/* Create the netlink socket */
	ret = socket(PF_NETLINK, SOCK_RAW, NETLINK_PPSAPI);
	if (ret < 0)
		return ret;
	sock = ret;

	/* Bind the socket with the source address */
	memset(&src_addr, 0, sizeof(src_addr));
	src_addr.nl_family = AF_NETLINK;
	src_addr.nl_pid = 0;		/* ask kernel to choose an unique ID */
	src_addr.nl_groups = 0;		/* not in mcast groups */
	ret = bind(sock, (struct sockaddr *) &src_addr, sizeof(src_addr));
	if (ret < 0) {
		close(sock);
		return ret;
	}

	/* Ask the kernel to destroy the PPS source */
	nlpps.cmd = PPS_FIND_PATH;
	strncpy(nlpps.path, path, pathlen);
	ret = netlink_msg(sock, &nlpps);
	if (ret < 0) {
		close(sock);
		return ret;
	}

	strncpy(path, nlpps.path, pathlen);
	strncpy(idstring, nlpps.name, idlen);

	close(sock);
	return nlpps.source;
}

#endif   /* !__KERNEL__ */
#endif   /* _SYS_TIMEPPS_H_ */
