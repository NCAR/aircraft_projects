/*
-------------------------------------------------------------------------
OBJECT NAME:	Colors.cc

FULL NAME:	X Color values.

ENTRY POINTS:	Colors()

STATIC FNS:		

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Colors.h"

#ifdef PNG
#include <sys/types.h>
#include <netinet/in.h>
#include <inttypes.h>
#endif

struct {
        char            name[20];
        float           ps_rgb[3];      /* For PostScript       */
        unsigned short  x_rgb[3];       /* For X (save PNG)     */
        unsigned long   pixel;
        unsigned long   cpixel;         /* Xserver byte order of 'pixel' */
} colorInfo[] = {
        { "Black",      { 0.0, 0.0, 0.0 },      { 0, 0, 0}, 0, 0 },
        { "red",        { 1.0, 0.0, 0.0 },      { 0, 0, 0}, 0, 0 },
        { "blue",       { 0.0, 0.0, 1.0 },      { 0, 0, 0}, 0, 0 },
        { "green",      { 0.0, 1.0, 0.0 },      { 0, 0, 0}, 0 },
        { "yellow",     { 1.0, 1.0, 0.0 },      { 0, 0, 0}, 0, 0 },
        { "maroon",     { 0.69, 0.1882, 0.3765 }, { 0, 0, 0}, 0, 0 },
        { "violet",     { 0.9333, 0.5098, 0.9333 }, { 0, 0, 0}, 0, 0 },
        { "purple",     { 0.6275, 0.1255, 0.9412 }, { 0, 0, 0}, 0, 0 },
        { "grey",       { 0.0, 0.0, 0.0 },      { 0, 0, 0}, 0, 0 },
        { "",         { 0.0, 0.0, 0.0 },      { 0, 0, 0}, 0, 0 } };

/* -------------------------------------------------------------------- */
Colors::Colors(const Widget w)
{
  int		i = 5, defaultDepth;
  Colormap	defaultCMap;
  Display	*dpy;
  int		screenNum;
  XVisualInfo	visualInfo;
  XColor	screenDef, exactDef;
  Window	win;

  Color = true;

  dpy = XtDisplay(w);
  screenNum = XScreenNumberOfScreen(XtScreen(w));
  defaultDepth = DefaultDepth(dpy, screenNum);

  if (defaultDepth == 1)
    {
    Color = false;
    return;
    }

  while (!XMatchVisualInfo(dpy, screenNum, defaultDepth, i, &visualInfo))
    --i;

  if (i < StaticColor)
    {
    Color = false;
    return;
    }


  /* OK, we have a color screen, allocate colors.
   */
  defaultCMap = DefaultColormap(dpy, screenNum);
  win = XCreatePixmap(dpy, XtWindow(w), 20, 1, defaultDepth);

  for (numberColors = 0; colorInfo[numberColors].name[0]; ++numberColors)
    {
    if (!XAllocNamedColor(
         dpy, defaultCMap, colorInfo[numberColors].name, &screenDef, &exactDef))
      {
      std::cerr << "Color.cc: Can't allocate color, reverting to B&W.\n";
      Color = false;
      return;
      }

    colorInfo[numberColors].pixel = exactDef.pixel;
#ifdef PNG
    XSetForeground(dpy, XDefaultGC(dpy, screenNum), exactDef.pixel);
    XDrawPoint(dpy, win, XDefaultGC(dpy, screenNum), numberColors, 0);

    colorInfo[numberColors].cpixel = screenDef.pixel;
    colorInfo[numberColors].x_rgb[0] = screenDef.red;
    colorInfo[numberColors].x_rgb[1] = screenDef.green;
    colorInfo[numberColors].x_rgb[2] = screenDef.blue;
#endif

    colorInfo[numberColors].ps_rgb[0] = (float)exactDef.red / 65535;
    colorInfo[numberColors].ps_rgb[1] = (float)exactDef.green / 65535;
    colorInfo[numberColors].ps_rgb[2] = (float)exactDef.blue / 65535;
    }


#ifdef PNG
{
  /* Hack to fix the Exceed bug.  Exceed returns exactDef for both exactDef
   * and screenDef, so write each color (above), and read them back here.
   */
  XImage *image = XGetImage(dpy, win, 0, 0, 20, 1,
        (unsigned long)AllPlanes, ZPixmap);

  for (i = 0; i < numberColors; ++i)
    {
    if (image->depth == 16)
      colorInfo[i].cpixel = ((ushort *)image->data)[i];
    if (image->depth > 16)
      colorInfo[i].cpixel = ((ulong *)image->data)[i];
    }

}
#endif

  XFreePixmap(dpy, win);

}	/* END CONSTRUCTOR */

#ifdef PNG
/* -------------------------------------------------------------------- */
void Colors::SavePNG(const char file_name[], XImage *image)
{
  int           i, j;
  FILE          *outFP;
  ushort        *s;
  png_structp   png_ptr;
  png_infop     info_ptr;
  png_bytep     row_pointers[2000];

  png_color     *palette;


  if ((outFP = fopen(file_name, "wb")) == NULL)
    return;


  png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING,
                        (png_voidp)NULL, NULL, NULL);

  if (!png_ptr)
    return;

  info_ptr = png_create_info_struct(png_ptr);

  if (!info_ptr) {
    png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
    return;
    }


  if (setjmp(png_ptr->jmpbuf)) {
    png_destroy_write_struct(&png_ptr, &info_ptr);
    fclose(outFP);
    return;
    }


  checkByteSwap(image);

  png_init_io(png_ptr, outFP);


  png_set_IHDR(png_ptr, info_ptr,
        image->width, image->height, 8,
        PNG_COLOR_TYPE_PALETTE, PNG_INTERLACE_NONE,
        PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);


  palette = new png_color[NumberOfColors()];

  for (i = 0; i < NumberOfColors(); i++) {
    s = GetColorRGB_X(i);
    palette[i].red   = s[0];
    palette[i].green = s[1];
    palette[i].blue  = s[2];
    }

  palette[i-1].red = palette[i-1].green = palette[i-1].blue = 0xffff;

  png_set_PLTE(png_ptr, info_ptr, palette, NumberOfColors());
//  png_set_bKGD(png_ptr, info_ptr, NumberOfColors()-1);


  /* Write header info to PNG file. */
  png_write_info(png_ptr, info_ptr);

  for (i = 0; i < image->height; ++i)
    {
    char        *p = &(image->data[i * image->bytes_per_line]);

    row_pointers[i] = new png_byte[image->width];

    switch (image->depth)
      {
      case 8:
        for (j = 0; j < image->width; ++j)
          row_pointers[i][j] = getColorIndex(((char *)p)[j]);

        break;

      case 16:
        for (j = 0; j < image->width; ++j)
          row_pointers[i][j] = getColorIndex(((ushort *)p)[j]);

        break;

      case 24: case 32:
        for (j = 0; j < image->width; ++j)
          row_pointers[i][j] = getColorIndex(((ulong *)p)[j]);

        break;
      }
    }


  /* Write the data! */
  png_write_image(png_ptr, row_pointers);
  png_write_end(png_ptr, info_ptr);

  png_destroy_write_struct(&png_ptr, &info_ptr);

  for (i = 0; i < image->height; ++i)
    delete [] row_pointers[i];
  delete [] palette;
  fclose(outFP);

}	/* END SAVEPNG */

/* -------------------------------------------------------------------- */
void Colors::checkByteSwap(XImage *image)
{
  int   i;
  bool	prog_byte_order;
  ulong pixel, x;

  static bool firstTime = TRUE;

  if (firstTime)        /* Only swap the colors on the first call. */
    firstTime = FALSE;
  else
    return;


  prog_byte_order = (1 == ntohl(1)) ? MSBFirst : LSBFirst;

  if (image->depth == 16)
    pixel = ((ushort *)image->data)[0];

  if (image->depth > 16)
    pixel = ((ulong *)image->data)[0];

  for (i = 0; i < numberColors; ++i)
    {
    if (image->byte_order != prog_byte_order)
      {
      x = colorInfo[i].pixel;

      if (image->depth == 16)
        colorInfo[i].cpixel = ((x<<8)&0xff00) | ((x>>8)&0xff);
      else
        colorInfo[i].cpixel = ((((x<<8)&0xff00) | ((x>>8)&0xff)) << 16) |
                        (((x>>8)&0xff00) | ((x>>24)&0xff)) ;
      }

    if (image->byte_order == LSBFirst)
      {
      x = colorInfo[i].x_rgb[0];
      colorInfo[i].x_rgb[0] = ((x<<8)&0xff00) | ((x>>8)&0xff);
      x = colorInfo[i].x_rgb[1];
      colorInfo[i].x_rgb[1] = ((x<<8)&0xff00) | ((x>>8)&0xff);
      x = colorInfo[i].x_rgb[2];
      colorInfo[i].x_rgb[2] = ((x<<8)&0xff00) | ((x>>8)&0xff);
      }
    }

}

/* -------------------------------------------------------------------- */
int Colors::getColorIndex(ulong pixel)
{
  int   i;

  /* Check background color first, since it will be the most common.
   */
  if (pixel == colorInfo[BACKGROUND].cpixel)
    return(BACKGROUND);

  for (i = 0; i < numberColors; ++i)
    if (pixel == colorInfo[i].cpixel)
      return(i);

  return(BACKGROUND);

}

/* -------------------------------------------------------------------- */
unsigned short *Colors::GetColorRGB_X(int indx)
{
  return(colorInfo[indx].x_rgb);
}

#endif

/* -------------------------------------------------------------------- */
unsigned long Colors::GetColor(int indx)
{
  return(colorInfo[indx].pixel);
}

/* -------------------------------------------------------------------- */
unsigned long Colors::NextColor()
{
  return(colorInfo[++colorIndex].pixel);
}

/* -------------------------------------------------------------------- */
unsigned long Colors::CurrentColor()
{
  return(GetColor(colorIndex));
}

/* -------------------------------------------------------------------- */
float *Colors::GetColorPS(int indx)
{
  return(colorInfo[indx].ps_rgb);
}

/* -------------------------------------------------------------------- */
float *Colors::NextColorPS()
{
  return(GetColorPS(++colorIndex));
}

/* -------------------------------------------------------------------- */
float *Colors::CurrentColorPS()
{
  return(GetColorPS(colorIndex));
}

/* -------------------------------------------------------------------- */
void SetColorNames(char str[])
{
  int   i;
  char  *p;

  p = strtok(str, " \t,");

  for (i = 1; colorInfo[i+1].name[0]; ++i)
    {
    strcpy(colorInfo[i].name, p);

    if ((p = strtok(NULL, " \t,\n")) == NULL)
      break;
    }

}       /* END SETCOLORNAMES */

/* END COLORS.CC */
