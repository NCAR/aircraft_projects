/*
-------------------------------------------------------------------------
OBJECT NAME:	hdrAPI.cc

FULL NAME:	Header API, C++ version.

ENTRY POINTS:	

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "hdrAPI.h"

#include <memory.h>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <sys/stat.h>
#include <sys/uio.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>

using namespace std;

/* -------------------------------------------------------------------- */
Header::Header(const string fileName)
{
  readHeader(fileName.c_str());
}

/* -------------------------------------------------------------------- */
Header::Header(const char fileName[])
{
  readHeader(fileName);
}

/* -------------------------------------------------------------------- */
void Header::readHeader(const char fileName[])
{
  int		fd;
  int		nBytes;
  char		buff[65535];
  bool		tape = false;
  TapeDrive	*drv;

  projName[0] = '\0';

  if (strncmp(fileName, "/dev", 4) == 0)
    tape = true;

  header = (Fl *)buff;

  if (tape)
    {
    drv = new TapeDrive(fileName);
    }
  else
    {
    if ((fd = open(fileName, O_RDONLY)) == (-1))
      {
      std::cerr << "Header: can't open " << fileName << " fatal, errno = " << errno << ".\n";
      exit(1);
      }
    }


  if (tape)
    {
    int	len = strlen(FIRST_REC_STRING);

    if (drv->Read(buff) < len)
      {
      std::cerr << "Header: read problem.\n";
      exit(1);
      }

    if (strncmp(FIRST_REC_STRING, buff, len) != 0)
      {
      std::cerr << "Header: not an ADS tape, fatal.\n";
      exit(1);
      }

    nBytes = drv->Read(buff);
    delete drv;
    }
  else
    {
    // Legacy support: header files on tape stored an identifying string at the
    // beginning of the file.  If it exists then read past it to access the Fl
    // block.  Otherwise rewind the file pointer.
    read(fd, buff, 40);
    if (strncmp(buff, FIRST_REC_STRING, strlen(FIRST_REC_STRING)) != 0)
      lseek(fd, 0, 0);

    if (strncmp(buff, FIRST_XML_STRING, strlen(FIRST_XML_STRING)) != 0)
      {
	// Read binary header file into the buffer.
	nBytes = read(fd, buff, sizeof(Fl));
	nBytes += read(fd, &buff[sizeof(Fl)], ntohl(header->thdrlen));
      }
    else
      {
	// Close the file and re-open as an XML document.
	close(fd);
	TiXmlDocument doc( fileName );
	if (!doc.LoadFile())
	  {
	    std::cerr << "Could not load file '" << fileNamee
		      << "'. Error='"<< doc.ErrorDesc() << "'. fatal.\n";
	    exit(1);
	  }
// 	TiXmlHandle docHandle( & );

// 	TiXmlNode* node = doc.FirstChild( "header" );
// 	assert

// 	for( child; child; child=child->NextSiblingElement() )
// 	  {
// 	    // do something
// 	  }


	// Parse the ascii XML file into the binary buffer.
	TiXmlNode* node = 0;
	TiXmlElement* ele = 0;
	
	node = doc.FirstChild( "Fl" );
	assert( node );
	ele = node->FirstChildElement();
	assert( node );

        Fl->thdr     = (str8)  asdf("thdr");     // I.D. "THDR"
        Fl->item_len = (long)  asdf("item_len"); // Length of this struct in bytes
        Fl->version  = (str8)  asdf("version");  // header version number
        Fl->prnum    = (str8)  asdf("prnum");    // project number
        Fl->fltnum   = (str8)  asdf("fltnum");   // flight number
        Fl->tpnum    = (str8)  asdf("tpnum");    // tape number
        Fl->date     = (str12) asdf("date");     // "mm/dd/yyyy
        Fl->time     = (str12) asdf("time");     // "hh:mm:ss"
        Fl->tzone    = (str4)  asdf("tzone");    // i.e. "MST"
        Fl->acraft   = (str8)  asdf("acraft");   // i.e. "N308D"
        Fl->n_items  = (long)  asdf("n_items");  // # of items excluding this one
        Fl->lrlen    = (long)  asdf("lrlen");    // logical record length
        Fl->lrppr    = (long)  asdf("lrppr");    // logical records per physical rec
        Fl->thdrlen  = (long)  asdf("thdrlen");  // length of this tape header
        Fl->ads_type = (str8)  asdf("ads_type"); // data system type
	
	

      }
    close(fd);
    }


  hdr = new char [nBytes];
  memcpy((void *)hdr, (void *)buff, (unsigned)nBytes);
  header = (Fl *)hdr;

  /* Check if valid file
   */
  if (strcmp(TAPEHDR_STR, header->thdr) != 0)
    {
    std::cerr << "Header: Bad header, fatal [" << header->thdr << "].\n";
    exit(1);
    }

}	/* END READHEADER */

/* -------------------------------------------------------------------- */
Header::Header(TapeDrive &drv)
{
  char	buff[65535];
  long	nBytes, len;

  len = strlen(FIRST_REC_STRING);

  if ((nBytes = drv.Read(buff)) < len)
    {
    std::cerr << stderr, "Header: read problem.\n";
    exit(1);
    }

  if (strncmp(FIRST_REC_STRING, buff, len) !=0)
    {
    std::cerr << "Header: not an ADS tape, fatal.\n";
    exit(1);
    }

  if ((nBytes = drv.Read(buff)) == 0)
    {
    std::cerr << "Header: empty tape.\n";
    exit(1);
    }

  hdr = new char [nBytes];
  memcpy((void *)hdr, (void *)buff, (unsigned)nBytes);
  header = (Fl *)hdr;

  /* Check if valid file
   */
  if (strcmp(TAPEHDR_STR, header->thdr) != 0)
    {
    std::cerr << "Header: Bad header, fatal.\n";
    exit(1);
    }

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void *Header::GetFirst()
{
  currentIndx = 0;
  currentPtr = (char *)header + sizeof(Fl);

  return(currentPtr);

}	/* END GETFIRST */

/* -------------------------------------------------------------------- */
void *Header::GetFirst(char blkName[])
{
  currentIndx = 0;
  currentPtr = (char *)header + ntohl(((Fl *)header)->item_len);

  for (currentIndx = 0; currentIndx < ntohl(header->n_items); ++currentIndx)
    {
    if (strcmp(((Blk *)currentPtr)->item_type, blkName) == 0)
      return(currentPtr);

    currentPtr += ntohl(((Blk *)currentPtr)->item_len);
    }

  return(NULL);

}	/* END GETFIRST */

/* -------------------------------------------------------------------- */
void *Header::GetSDI(char varName[])
{
  currentIndx = 0;
  currentPtr = (char *)header + ntohl(((Fl *)header)->item_len);

  for (currentIndx = 0; currentIndx < ntohl(header->n_items); ++currentIndx)
    {
    if (strcmp(((Blk *)currentPtr)->item_type, "SDI") == 0 &&
        strcmp(((Sh *)currentPtr)->name, varName) == 0)
        return(currentPtr);

    currentPtr += ntohl(((Blk *)currentPtr)->item_len);
    }

  return(NULL);

}	/* END GETFIRST */

/* -------------------------------------------------------------------- */
void *Header::GetNext()
{
  if (++currentIndx >= ntohl(header->n_items))
    return(NULL);

  currentPtr += ntohl(((Blk *)currentPtr)->item_len);

  return(currentPtr);

}	/* END GETNEXT */

/* -------------------------------------------------------------------- */
void *Header::GetNext(char blkName[])
{
  if (++currentIndx >= ntohl(header->n_items))
    return(NULL);

  currentPtr += ntohl(((Blk *)currentPtr)->item_len);

  for (; currentIndx < ntohl(header->n_items); ++currentIndx)
    {
    if (strcmp(((Blk *)currentPtr)->item_type, blkName) == 0)
      return(currentPtr);

    currentPtr += ntohl(((Blk *)currentPtr)->item_len);
    }

  return(NULL);

}	/* END GETNEXT */

/* -------------------------------------------------------------------- */
char *Header::ProjectName()
{
  if (strlen(projName) == 0)
    {
    char	*p;

    if ((p = getenv("PROJ_DIR")))
      {
      FILE	*fp;
      char	tmp[256];

      sprintf(tmp, "%s/%s/ProjectName", p, ProjectNumber());

      if ((fp = fopen(tmp, "r")))
        {
        fgets(projName, 32, fp);
        fclose(fp);
        projName[31] = '\0';

        if (projName[strlen(projName)-1] == '\n')
          projName[strlen(projName)-1] = '\0';
        }
      }
    }

  return(projName);

}	/* END PROJECTNAME */

/* -------------------------------------------------------------------- */
Header::~Header()
{
  delete [] hdr;

}	/* END DESTRUCTOR */

/* END HDRAPI.CC */
