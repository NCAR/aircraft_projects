#include <iostream>
#include <cstdio>
#include <cstring>
#include <unistd.h>

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
//  host.setAddress("12.47.179.48");	// Reachback.

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
//  timer_id = 0;
}

/* -------------------------------------------------------------------- */
void udp2sql::newData()
{
  char udp_str[65000], sql_str[65000], *p, timestamp[1000];

  if (_timer_id)
    killTimer(_timer_id);

  int nBytes = _udp->readBlock(udp_str, 65000);

  if (strncmp(udp_str, "P3", 2))
    return;

  p = strtok(udp_str, ",");
  p = strtok(NULL, ",");
  strcpy(timestamp, p);
  sprintf(sql_str, "INSERT INTO raf_lrt VALUES ('%s',%s);", timestamp, strtok(NULL, "\n"));

  newPostgresConnection();
  PGresult * res;
  res = PQexec(_conn, sql_str);
  std::cerr << PQerrorMessage(_conn);
  PQclear(res);

  std::cout << sql_str << std::endl;

  sprintf(sql_str, "UPDATE global_attributes SET value='%s.999' WHERE key='EndTime';", timestamp);
  res = PQexec(_conn, sql_str);
  std::cerr << PQerrorMessage(_conn);
  PQclear(res);
  PQfinish(_conn);

//  timer_id = startTimer(360000);
}
