
#ifndef PORTABLE_H
#define PORTABLE_H

#include <sys/types.h>
#include <netinet/in.h>


#if defined(__LITTLE_ENDIAN) || defined(_LITTLE_ENDIAN) || defined(LITTLE_ENDIAN)

float   ntohf(float);

#else

#define ntohf(x)        (x)

#endif

#define htonf        ntohf

#endif
