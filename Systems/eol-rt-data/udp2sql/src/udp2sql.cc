#include "udp2sql.h"

#include <iostream>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <bzlib.h>
#include <map>
#include <QtCore/QTimerEvent>


using namespace std;

static const int port = 31007;


#include <openssl/ripemd.h>


/* -------------------------------------------------------------------- */
udp2sql::udp2sql()
{
  _conn = 0;
  _timer_id = 0;
  newUDPConnection();
//  newPostgresConnection();
}

/* -------------------------------------------------------------------- */
bool udp2sql::newPostgresConnection(string platform)
{
  string spec="user=ads dbname=real-time-"+platform;
  if (platform == "GAUS")
  {
    spec="user=ads dbname=soundings";
  }
  spec += " " + this->_qspec;
//cout << spec << endl;

  _conn = PQconnectdb(spec.c_str());

  if (PQstatus(_conn) == CONNECTION_BAD)
  {
    cout << "SourceSQL: Connection failed: "
         << "(Check PGHOST, PGDATABASE & PGUSER environment variables.)\n";
    cout << PQerrorMessage(_conn) << endl;
    PQfinish(_conn);
    _conn = 0;
  }
  return (_conn != 0);
}


void
udp2sql::
closePostgresConnection()
{
  if (_conn)
  {
    PQfinish(_conn);
  }
}


void
udp2sql::
execute(const char* sql_str)
{
  PGresult * res;
  res = PQexec(_conn, sql_str);
  cout << PQerrorMessage(_conn);
  PQclear(res);
}


/* -------------------------------------------------------------------- */
void udp2sql::newUDPConnection()
{
  _udp = new QUdpSocket();
  QHostAddress	host;

  host.setAddress("0.0.0.0");	// Inhouse
//host.setAddress("12.47.179.48");	// Reachback.

  cout << "conn = " << _udp->bind(host, port, QUdpSocket::ReuseAddressHint)
       << "\n";
 
  connect(_udp, SIGNAL(readyRead()), this, SLOT(readPendingDatagrams()));
}

/* -------------------------------------------------------------------- */
void udp2sql::timerEvent(QTimerEvent *)
{
  cout << "Resetting connection\n";
//PQfinish(_conn);
//newPostgresConnection();
//  delete _udp;
//  _timer_id = 0;
}


namespace
{
  typedef std::map<std::string,std::string> passwords_t;
  passwords_t passwords;

  void
  init_passwords()
  {
    passwords["test1"] = "this will never work";
  }


  std::string
  get_password(const std::string& id)
  {
    if (passwords.begin() == passwords.end())
    {
      init_passwords();
    }
    passwords_t::iterator it;
    for (it = passwords.begin(); it != passwords.end(); ++it)
    {
      if (it->first == id)
	return it->second;
    }
    return "";
  }

}



void udp2sql::readPendingDatagrams()
{
  while (_udp->hasPendingDatagrams())
  {
    newData();
  }
}


/* -------------------------------------------------------------------- */
void udp2sql::newData()
{
  char udp_str[65000];
  char buffer_space[65000];
  char* buffer = buffer_space;
  memset(udp_str, 0, 65000);
  memset(buffer, 0, 65000);

  if (_timer_id)
    killTimer(_timer_id);

  int nBytes = _udp->readDatagram(udp_str, 65000);
  if (nBytes < 1) 
  {
    cout << "readDatagram() returned " << nBytes << "\n";
    return;
  }

  // Decompress the stream recv'd from the platform.  Using one less than
  // buffer size, plus zeroing the memory in the memset above, ensures that
  // buffer will be null-terminated no matter what bunzip does to it.
  unsigned int bufLen = sizeof(buffer_space) - 1;
  int ret = BZ2_bzBuffToBuffDecompress(buffer, &bufLen, udp_str, nBytes, 0, 0);
  if (ret == BZ_DATA_ERROR_MAGIC)
    memcpy(buffer, udp_str, nBytes);
  else if (ret < 0) {
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
    cout << "Failed to decompress the ground feed stream: " 
         << BZ2_bzerror(&b, &errnum) << endl;
    return;
  }
  else
    cout << "\ndecompressed " << nBytes << " -> " << bufLen << endl;

  // Now see if this message has a digest.
  if (strncmp(buffer, "DIGEST:", 7) == 0)
  {
    buffer += 7;
    // The digest (in hexadecimal format) will be the next 40 bytes, unless
    // there are not enough.
    if (strlen(buffer) < 41)
    {
      cout << "expected digest, but none found: ";
      return;
    }
    string digest = string(buffer, buffer+40);
    cout << "found digest: " << digest << "\n";
    buffer += 41; // skip the newline between digest and id.

    // Next is the id.
    char *idp = buffer;
    while (*buffer != 0 && *buffer != '\n')
    {
      ++buffer;
    }
    string id = string(idp, buffer);
    if (*buffer) ++buffer; // skip newline after id
    cout << "found id: " << id << "\n";
    std::string pwd = get_password(id);
    if (pwd.size() == 0)
    {
      cout << "unrecognized id '" << id << "': ignoring this message!\n";
      return;
    }

    // The rest of the buffer is the message.  Pipe everything back through
    // a digest with the password and see if it matches.
    RIPEMD160_CTX ctx;
    if (! RIPEMD160_Init(&ctx))
    {
      cout << "hash init failed!\n";
      return;
    }
    RIPEMD160_Update(&ctx, id.c_str(), id.length());
    RIPEMD160_Update(&ctx, pwd.c_str(), pwd.length());
    RIPEMD160_Update(&ctx, buffer, strlen(buffer));
    unsigned char md[RIPEMD160_DIGEST_LENGTH];
    if (! RIPEMD160_Final(md, &ctx))
    {
      cout << "final digest computation failed!\n";
      return;
    }

    // Finally, convert this to hex and compare with the incoming digest.
    char hexmd[2*RIPEMD160_DIGEST_LENGTH + 1];
    for (int i = 0; i < RIPEMD160_DIGEST_LENGTH; ++i)
    {
      sprintf(hexmd + 2*i, "%02x", (int)md[i]);
    }
    hexmd[2*RIPEMD160_DIGEST_LENGTH] = 0;
    cout << "expected digest: " << hexmd << "\n";

    if (digest != hexmd)
    {
      cout << "authentication failed for '" << id
	   << "', ignoring message!\n";
      return;
    }

    // This is a valid message.  Use the rest of the buffer as it is.
  }
      
  // Filter out messages from un-expected sources, and pass the
  // uncompressed message to the platform handler.
  string platform;
  if      (strncmp(buffer, "C130", 4) == 0) platform = "C130";
  else if (strncmp(buffer, "GV", 2) == 0)   platform = "GV";
  else if (strncmp(buffer, "P3", 2) == 0)   platform = "P3";
  else if (strncmp(buffer, "DC8", 3) == 0)   platform = "DC8";
  else if (strncmp(buffer, "IWG1", 4) == 0)   platform = "DC8";
  else if (strncmp(buffer, "GAUS:", 5) == 0) platform = "GAUS";
  else return;

  if (platform == "GAUS")
  {
    handleSoundingMessage(platform, buffer);
  }
  else
  {
    handleAircraftMessage(platform, buffer);
  }
}


void
udp2sql::
handleSoundingMessage(string platform, char* buffer)
{
  // Strip the GAUS: header.
  buffer += 5;

  // The rest is the sql to execute.
  if (*buffer and newPostgresConnection(platform))
  {
    execute(buffer);
    closePostgresConnection();
  }
}



void
udp2sql::
handleAircraftMessage(string aircraft, char* buffer)
{
  char* p;
  char timestamp[1000];
  char sql_str[65000];
  char vars[65000];

  memset(sql_str, 0, 65000);
  memset(vars, 0, 65000);

  // break the stream into two usable substrings
  p = strtok(buffer, ",");
  p = strtok(NULL, ",");
  strcpy(timestamp, p);
  p = strtok(NULL, "");
  strcpy(vars, p);

  QString varsStr(vars);

  // trim off '\r' and '\n' characters if present
  varsStr.replace("\r","");
  varsStr.replace("\n","");

  // remove all spaces
  int len = 0;
  while (len != varsStr.length()) {
    len = varsStr.length();
    varsStr.replace(", ",",");
  }
  // instert nulls for all missing values
  len = 0;
  while (len != varsStr.length()) {
    len = varsStr.length();
    varsStr.replace(",,",",null,");
  }
  if (varsStr.endsWith(","))
    varsStr.append("null");

  if (newPostgresConnection(aircraft))
  {
    // create postgres statements
    sprintf(sql_str, "INSERT INTO raf_lrt VALUES ('%s',%s);", timestamp, varsStr.toStdString().c_str());
    cout << sql_str << endl;
    execute(sql_str);
    sprintf(sql_str, 
	    "UPDATE global_attributes SET value='%s.999' WHERE key='EndTime';",
	    timestamp);
//  cout << sql_str << endl;
    execute(sql_str);
    closePostgresConnection();
  }
  //  _timer_id = startTimer(360000);
}
