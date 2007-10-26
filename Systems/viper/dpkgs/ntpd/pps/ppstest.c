#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <timepps.h>

#define STRING_LEN	LINUXPPS_MAX_NAME_LEN

int find_source(int try_link, char *link, pps_handle_t *handle, int *avail_mode)
{
	int num = -1;
	char id[STRING_LEN] = "",		/* no ID string by default   */
	     path[STRING_LEN];
	pps_params_t params;
	int ret;

	if (try_link)
		printf("trying PPS source \"%s\"\n", link);
	if (!try_link) {
#ifdef PPS_HAVE_FINDSOURCE
		/* Try to find the source (by using "index = -1" we ask just
		 * for a generic source) */
		ret = time_pps_findsource(num, path, STRING_LEN, id, STRING_LEN);
#else
#warning "cannot use time_pps_findsource()"
		ret = -1;
#endif   /* PPS_HAVE_FINDSOURCE */
	}
	else {
#ifdef PPS_HAVE_FINDPATH
		/* Get the PPS source's real name */
		time_pps_readlink(link, STRING_LEN, path, STRING_LEN);

		/* Try to find the source by using the supplied "path" name */
		ret = time_pps_findpath(path, STRING_LEN, id, STRING_LEN);
#else
#warning "cannot use time_pps_findpath()"
		ret = -1;
#endif   /* PPS_HAVE_FINDPATH */
	}
	if (ret < 0) {
		fprintf(stderr, "no available PPS source in the system\n");
		return -1;
	}
	num = ret;
	printf("found PPS source #%d \"%s\" on \"%s\"\n", num, id, path);

	/* If "path" is not NULL we should *at least* open the pointed
	 * device in order to enable the interrupts generation.
	 * Note that this can be NOT enough anyway, infact you may need sending
	 * additional commands to your GPS antenna before it starts sending
	 * the PPS signal. */
	if (strlen(path)) {
		ret = open(path, O_RDWR);
		if (ret < 0) {
			fprintf(stderr, "cannot open \"%s\" (%m)\n", path);
			return -1;
		}
	}

	/* Open the PPS source */
	ret = time_pps_create(num, handle);
	if (ret < 0) {
		fprintf(stderr, "cannot create a PPS source (%m)\n");
		return -1;
	}

	/* Find out what features are supported */
	ret = time_pps_getcap(*handle, avail_mode);
	if (ret < 0) {
		fprintf(stderr, "cannot get capabilities (%m)\n");
		return -1;
	}
	if ((*avail_mode & PPS_CAPTUREASSERT) == 0) {
		fprintf(stderr, "cannot CAPTUREASSERT\n");
		return -1;
	}
	if ((*avail_mode & PPS_OFFSETASSERT) == 0) {
		fprintf(stderr, "cannot OFFSETASSERT\n");
		return -1;
	}

	/* Capture assert timestamps, and compensate for a 675 nsec
	 * propagation delay */
	ret = time_pps_getparams(*handle, &params);
	if (ret < 0) {
		fprintf(stderr, "cannot get parameters (%m)\n");
		return -1;
	}
	params.assert_offset.tv_sec = 0;
	params.assert_offset.tv_nsec = 675;
	params.mode |= PPS_CAPTUREASSERT|PPS_OFFSETASSERT;
	ret = time_pps_setparams(*handle, &params);
	if (ret < 0) {
		fprintf(stderr, "cannot set parameters (%m)\n");
		return -1;
	}

	return 0;
}

int fetch_source(int i, pps_handle_t *handle, int *avail_mode)
{
	struct timespec timeout;
	pps_info_t infobuf;
	int ret;

	/* create a zero-valued timeout */
	timeout.tv_sec = 0;
	timeout.tv_nsec = 0;

	if (*avail_mode&PPS_CANWAIT) {
		ret = time_pps_fetch(*handle, PPS_TSFMT_TSPEC, &infobuf, NULL); /* waits for the next event */
		if (ret < 0) {
			fprintf(stderr, "cannot set parameters (%m)\n");
			return -1;
		}
	}
	else {
		sleep(1);
		ret = time_pps_fetch(*handle, PPS_TSFMT_TSPEC, &infobuf, &timeout);
		if (ret < 0) {
			fprintf(stderr, "cannot set parameters (%m)\n");
			return -1;
		}
	}

	printf("source %d - "
	       "assert %ld.%09ld, sequence: %ld - "
	       "clear  %ld.%09ld, sequence: %ld\n",
	        i,
		infobuf.assert_timestamp.tv_sec,
		infobuf.assert_timestamp.tv_nsec,
		infobuf.assert_sequence,
		infobuf.clear_timestamp.tv_sec,
		infobuf.clear_timestamp.tv_nsec,
		infobuf.clear_sequence);

	return 0;
}

int main(int argc, char *argv[])
{
	int num,
	    try_link = 0;			/* by default use findsource */
	char link[STRING_LEN] = "/dev/gps0";	/* just a default device */
	pps_handle_t handle[4];
	int avail_mode[4];
	int i = 0, ret;

	if (argc == 1) {
		ret = find_source(try_link, link, &handle[0], &avail_mode[0]);
		if (ret < 0)
			exit(1);

		num = 1;
	}
	else {
		for (i = 1; i < argc && i <= 4; i++) {
			ret = sscanf(argv[i], "%d", &num);
			if (ret < 1) {
				try_link = ~0;
				strncpy(link, argv[i], STRING_LEN);
			}
	
			ret = find_source(try_link, link, &handle[i-1], &avail_mode[i-1]);
			if (ret < 0)
				exit(1);
		}

		num = i-1;
	}

	printf("ok, found %d source(s), now start fetching data...\n", num);

	/* loop, printing the most recent timestamp every second or so */
	while (1) {
		for (i = 0; i < num; i++) {
			ret = fetch_source(i, &handle[i], &avail_mode[i]);
			if (ret < 0)
				break;
		}
	}

	for (; i >= 0; i--)
		time_pps_destroy(handle[i]);

	return 0;
}
