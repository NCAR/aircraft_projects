#include <sys/types.h>
#include <netinet/in.h>
#include <inttypes.h>

#include "hdrbld.h"
#include "hardwire.h"

static void fnqsort(int beg, int end);

struct sort
	{
	int	SampleRate;
	int	type;
	char	dsm[8];
	int	cardAddr;
	Sh	*sdi;
	} *sortKeys[MX_SDI];

/* -------------------------------------------------------------------- */
void SortSh()
{
  int		i, j;

  /* Set up Keys.
   */
  for (i = 0; i < nsdi; ++i)
    {
    sortKeys[i] = (struct sort *)GetMemory(sizeof(struct sort));
    memset(sortKeys[i], 0, sizeof(struct sort));

    sortKeys[i]->SampleRate	= htonl(10000 - sdi[i]->rate);
    sortKeys[i]->cardAddr	= htonl(sdi[i]->adsaddr);
    sortKeys[i]->sdi		= sdi[i];
    strcpy(sortKeys[i]->dsm, sdi[i]->dsm_locn);

    for (j = 0; typeListChar[j]; ++j)
      if (typeListChar[j][0] == sdi[i]->type[0])
        sortKeys[i]->type = htonl(j);
    }


  fnqsort(0, nsdi-1);


  /* Re-assign sdi, and free memory.
   */
  for (i = 0; i < nsdi; ++i)
    {
    sdi[i] = sortKeys[i]->sdi;
    free(sortKeys[i]);
    }

}

/* -------------------------------------------------------------------- */
struct sort	temp, mid;

static void fnqsort(int beg, int end)
{
  register int	x = beg,
		y = end;

  memcpy((char *)&mid, (char *)sortKeys[(x + y) / 2], sizeof(struct sort));

  while (x <= y)
    {
    while (memcmp((char *)sortKeys[x],(char *)&mid,sizeof(struct sort)) < 0)
      ++x;

    while (memcmp((char *)sortKeys[y],(char *)&mid,sizeof(struct sort)) > 0)
      --y;

    if (x <= y)
      {
      memcpy((char *)&temp, (char *)sortKeys[x], sizeof(struct sort));
      memcpy((char *)sortKeys[x],(char *)sortKeys[y],sizeof(struct sort));
      memcpy((char *)sortKeys[y], (char *)&temp, sizeof(struct sort));
      ++x;
      --y;
      }
    }

  if (beg < y)
    fnqsort(beg, y);

  if (x < end)
    fnqsort(x, end);

}	/* END FNQSORT */

/* END SORT.C */
