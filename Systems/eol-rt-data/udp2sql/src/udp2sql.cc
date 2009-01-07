#include <iostream>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <bzlib.h>

#include "udp2sql.h"

static const int port = 31007;

/* -------------------------------------------------------------------- */
udp2sql::udp2sql()
{
  _conn = 0;
  _timer_id = 0;
  newUDPConnection();
//  newPostgresConnection();
}

/* -------------------------------------------------------------------- */
void udp2sql::newPostgresConnection()
{
  _conn = PQconnectdb("");

  if (PQstatus(_conn) == CONNECTION_BAD)
  {
    std::cerr << "SourceSQL: Connection failed: "
         << "(Check PGHOST, PGDATABASE & PGUSER environment variables.)\n";
    std::cerr << PQerrorMessage(_conn) << std::endl;
    PQfinish(_conn);
    _conn = NULL;
  }
}

/* -------------------------------------------------------------------- */
void udp2sql::newUDPConnection()
{
  _udp = new QSocketDevice(QSocketDevice::Datagram);
  QHostAddress	host;

  host.setAddress("0.0.0.0");	// Inhouse
//host.setAddress("12.47.179.48");	// Reachback.

  _udp->setAddressReusable(true);
  std::cout << "conn = " << _udp->bind(host, port) << std::endl;

  _notify = new QSocketNotifier(_udp->socket(), QSocketNotifier::Read);
  QObject::connect(_notify, SIGNAL(activated(int)), this, SLOT(newData()));
}

/* -------------------------------------------------------------------- */
void udp2sql::timerEvent(QTimerEvent *)
{
  std::cout << "Resetting connection\n";
  PQfinish(_conn);
  newPostgresConnection();
//  delete _notify;
//  delete _udp;
//  _timer_id = 0;
}

/* -------------------------------------------------------------------- */
void udp2sql::newData()
{
  char udp_str[65000], sql_str[65000], *p, timestamp[1000];
  char vars[65000], buffer[65000];
  memset(udp_str, 0, 65000);
  memset(sql_str, 0, 65000);
  memset(vars, 0, 65000);
  memset(buffer, 0, 65000);

  if (_timer_id)
    killTimer(_timer_id);

  int nBytes = _udp->readBlock(udp_str, 65000);
  if (nBytes < 1) return;

  // decompress the stream recv'd from the aircraft
  unsigned int bufLen = sizeof(buffer);
  int ret = BZ2_bzBuffToBuffDecompress( buffer, &bufLen, udp_str, nBytes, 0, 0 );
  if (ret < 0) {
    typedef struct {     // copied from bzlib.c
      FILE*     handle;
      char      buf[BZ_MAX_UNUSED];
      int       bufN;
      bool      writing;
      bz_stream strm;
      int       lastErr;
      bool      initialisedOk;
    } bzFile;
    bzFile b;
    b.lastErr = ret;
    int errnum;
    printf( "Failed to decompress the ground feed stream: %s\n", BZ2_bzerror(&b, &errnum) );
    return;
  }
  printf("\ndecompressed %d -> %d\n", nBytes, bufLen);
  printf("%s\n",buffer);

  // filter out messages from un-expected sources
  if (strncmp(buffer, "C130", 4) &&
      strncmp(buffer, "GV", 2) &&
      strncmp(buffer, "P3", 2))
    return;

  // break the stream into two usable substrings
  p = strtok(buffer, ",");
  p = strtok(NULL, ",");
  strcpy(timestamp, p);
  p = strtok(NULL, "");
  strcpy(vars, p);

  // trim off '\n' character if present
  if (vars[strlen(vars)-1] == '\n')
    vars[strlen(vars)-1] = 0;

  // create postgres statement
  sprintf(sql_str, "INSERT INTO raf_lrt VALUES ('%s',%s);", timestamp, vars);
  std::cout << strlen(sql_str) << ": " << sql_str << std::endl;
  
  newPostgresConnection();
  PGresult * res;
  res = PQexec(_conn, sql_str);
  std::cerr << PQerrorMessage(_conn);
  PQclear(res);

  sprintf(sql_str, "UPDATE global_attributes SET value='%s.999' WHERE key='EndTime';", timestamp);
  res = PQexec(_conn, sql_str);
  std::cerr << PQerrorMessage(_conn);
  PQclear(res);
  PQfinish(_conn);

//  _timer_id = startTimer(360000);
}
