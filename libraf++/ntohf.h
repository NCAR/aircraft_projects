#include <netinet/in.h>

#if defined(__LITTLE_ENDIAN) || defined(_LITTLE_ENDIAN) || defined(LITTLE_ENDIAN)

float   ntohf(float);
#define htonf(x)        ntohf(x)

#else

#define ntohf(x)        (x)
#define htonf(x)        (x)

#endif

