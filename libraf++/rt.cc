#include "adsIO.h"

char buffer[65000];
P2d_rec	pBuf;

main()
{
  FILE	*hdrFP;

  hdrFP = fopen("/home/local/proj/hosts/rtdata.filename", "w+");
  fprintf(hdrFP, "/home/data/r1/RealTime\n");
  fclose(hdrFP);

  ADS_DataFile sync("/home/data/102rf07.ads");
  ADS_DataFile twoD("/home/data/102rf07.2d");

  hdrFP = fopen("/home/data/102rf07.ads", "rb");
  fread(buffer, 20+(2*sync.hdr->HeaderLength()), 1, hdrFP);
  fclose(hdrFP);

  FILE	*outFP = fopen("/home/data/r1/RealTime.ads", "w+b");
  FILE	*out2D = fopen("/home/data/r1/RealTime.2d", "w+b");
  fwrite(buffer, 20+(2*sync.hdr->HeaderLength()), 1, outFP);
  fwrite(buffer, 20+(2*sync.hdr->HeaderLength()), 1, out2D);

  sync.FirstSyncRecord(buffer);
  twoD.FirstPMS2dRecord(&pBuf);

  do
    {
    fwrite(buffer, sync.hdr->lrLength(), 1, outFP);

    while (memcmp((char *)&pBuf.hour, &buffer[2], 6) <= 0)
      {
      fwrite(&pBuf, sizeof(P2d_rec), 1, out2D);
      twoD.NextPMS2dRecord(&pBuf);
      }

    usleep(700000);
    }
  while (sync.NextSyncRecord(buffer));

  fclose(outFP);

}
