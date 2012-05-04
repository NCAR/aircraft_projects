#include "udp2sql.h"

#include <iostream>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <bzlib.h>
#include <map>
#include <QtCore/QTimerEvent>
#include <QtCore/QStringList>

#include <nidas/util/Socket.h>
#include <nidas/util/Inet4Address.h>

using namespace std;

namespace n_u = nidas::util;

static const int port = 31007;


#include <openssl/ripemd.h>


enum DC8VARS {
    DC8,
    DATETIME,
    GGLAT,
    GGLON,
    GGALT,
    WGSALT,
    PALTF,
    HGM232,
    GSF,
    TASX,
    IAS,
    MACH_A,
    VSPD,
    THDG,
    TKAT,
    DRFTA,
    PITCH,
    ROLL,
    SSLIP,
    ATTACK,
    ATX,
    DPXC,
    TTX,
    PSXC,
    QCXC,
    PCAB,
    WSC,
    WDC,
    WIC,
    SOLZE,
    SOLAR_EL_AC,
    SOLAZ,
    SOLAR_AZ_AC,
    VNS_MMS,
    VEW_MMS,
    VUP_MMS,
    COLDCN,
    HOTCN,
    DRYSCATTERING,
    CO,
    CH4,
    WVPPM,
    C02,
    NO,
    NOY,
    O3,
    SP2_INCPARTICLECOUNT,
    HSP2_INCPARTICLECOUNT,
    SO4,
    NO3,
    NH4,
    TOTAL_ORGANIC,
    CHLORIDE,
    MZ43,
    MZ44,
    MZ57,
    MZ60
};


/* -------------------------------------------------------------------- */
udp2sql::udp2sql()
{
  _conn = 0;
  _timer_id = 0;
  _count = 0;
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
  if      (strncmp(buffer, "C130", 4) == 0)  platform = "C130";
  else if (strncmp(buffer, "GV", 2) == 0)    platform = "GV";
  else if (strncmp(buffer, "P3", 2) == 0)    platform = "P3";
  else if (strncmp(buffer, "DC8", 3) == 0)   platform = "DC8";
  else if (strncmp(buffer, "GAUS:", 5) == 0) platform = "GAUS";
  else return;

  // report on transferred amounts
  if (ret == BZ_OK)
    cout << "\n" << platform << " decompressed " << nBytes << " -> " << bufLen << endl;
  else
    cout << "\n" << platform << " received " << nBytes << endl;

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
  QString varsStr(buffer);

  // trim off '\r' and '\n' characters if present
//varsStr.replace("\r","");
//varsStr.replace("\n","");

  // remove all spaces
  int len = 0;
  while (len != varsStr.length()) {
    len = varsStr.length();
    varsStr.replace(", ",",");
  }
  // save a copy for re-broadcast later
  QString varsStrCopy(varsStr);

  // update database entries
  if (newPostgresConnection(aircraft))
  {
    // instert NANs for all missing values
    len = 0;
    while (len != varsStr.length()) {
      len = varsStr.length();
      varsStr.replace(",,",",-32767,");
    }
    if (varsStr.endsWith(","))
      varsStr.append("-32767");

    // break the buffer into usable substrings
    QStringList varList = varsStr.split(",");

    // correct +/- 180 to 0..360 on wind direction
    if (strncmp(aircraft.c_str(), "DC8", 3) == 0)
    {
      QString windDirectionStr = varList[WDC];
      double windDirection = varList[WDC].toFloat() + 180.0;
      varList[WDC] = QString::number(windDirection, 'g', 1);
    }
    // remove the preceeding "IWG1,datetime,"
    varList.takeFirst();
    QString datetime = varList.takeFirst();

    // ignore messages that are missing datetime values
    if (datetime == "-32767") {
      cout << "DROPPED missing datetime" << endl;
      closePostgresConnection();
      return;
    }
    // trim off the microsecond field from the datetime
    datetime.replace(QRegExp("\\.[0-9]+$"), "");
    len = 0;
    while (len != datetime.length()) {
      len = datetime.length();
      datetime.replace("-","");
      datetime.replace(":","");
    }
    QString sql_str;
    // create postgres statements
    sql_str = "INSERT INTO raf_lrt VALUES ('" + datetime + "'," + varList.join(",") + ");";
    cout << sql_str.toStdString() << endl;
    execute(sql_str.toStdString().c_str());
    sql_str = "UPDATE global_attributes SET value='" + datetime + ".999' WHERE key='EndTime';",
    cout << sql_str.toStdString() << endl;
    execute(sql_str.toStdString().c_str());
    closePostgresConnection();
  }
  // re-broadcast message to other aircraft
  if (strncmp(aircraft.c_str(), "DC8", 3) == 0) {
  
    // send every 20 seconds
    if (_count++ % 20) return;

    // break the buffer into usable substrings
    QStringList varListCopy = varsStrCopy.split(",");

    // prune un-needed variables
    varListCopy.removeAt(MZ60);
    varListCopy.removeAt(MZ57);
    varListCopy.removeAt(MZ44);
    varListCopy.removeAt(MZ43);
    varListCopy.removeAt(CHLORIDE);
    varListCopy.removeAt(TOTAL_ORGANIC);
    varListCopy.removeAt(NH4);
    varListCopy.removeAt(NO3);
    varListCopy.removeAt(SO4);
    varListCopy.removeAt(HSP2_INCPARTICLECOUNT);
    varListCopy.removeAt(SP2_INCPARTICLECOUNT);
    varListCopy.removeAt(O3);
    varListCopy.removeAt(NOY);
    varListCopy.removeAt(NO);
    varListCopy.removeAt(C02);
    varListCopy.removeAt(WVPPM);
    varListCopy.removeAt(CH4);
    varListCopy.removeAt(CO);
    varListCopy.removeAt(DRYSCATTERING);
    varListCopy.removeAt(HOTCN);
    varListCopy.removeAt(COLDCN);
    varListCopy.removeAt(VUP_MMS);
    varListCopy.removeAt(VEW_MMS);
    varListCopy.removeAt(VNS_MMS);
    varListCopy.removeAt(SOLAR_AZ_AC);
    varListCopy.removeAt(SOLAZ);
    varListCopy.removeAt(SOLAR_EL_AC);
    varListCopy.removeAt(SOLZE);
//  varListCopy.removeAt(WIC);
//  varListCopy.removeAt(WDC);
//  varListCopy.removeAt(WSC);
    varListCopy.removeAt(PCAB);
    varListCopy.removeAt(QCXC);
    varListCopy.removeAt(PSXC);
    varListCopy.removeAt(TTX);
//  varListCopy.removeAt(DPXC);
//  varListCopy.removeAt(ATX);
    varListCopy.removeAt(ATTACK);
    varListCopy.removeAt(SSLIP);
    varListCopy.removeAt(ROLL);
    varListCopy.removeAt(PITCH);
    varListCopy.removeAt(DRFTA);
    varListCopy.removeAt(TKAT);
    varListCopy.removeAt(THDG);
    varListCopy.removeAt(VSPD);
    varListCopy.removeAt(MACH_A);
    varListCopy.removeAt(IAS);
//  varListCopy.removeAt(TASX);
    varListCopy.removeAt(GSF);
    varListCopy.removeAt(HGM232);
//  varListCopy.removeAt(PALTF);
    varListCopy.removeAt(WGSALT);
    varListCopy.removeAt(GGALT);
//  varListCopy.removeAt(GGLON);
//  varListCopy.removeAt(GGLAT);
//  varListCopy.removeAt(DATETIME);
//  varListCopy.removeAt(DC8);

    QString trimmed = varListCopy.join(",");
    
    char temp[65000];
    memset(temp, 0, 65000);
    memcpy(temp, trimmed.toStdString().c_str(), trimmed.length() );
//  reBroadcastMessage("hyper.raf-guest.ucar.edu", temp);
    reBroadcastMessage("rafgv.dyndns.org", temp);
  }

  //  _timer_id = startTimer(360000);
}



void
udp2sql::
reBroadcastMessage(string dest, char* buffer)
{
  n_u::DatagramSocket * _socket;
  n_u::Inet4SocketAddress * _to;

  _socket = new n_u::DatagramSocket;
  _to = new n_u::Inet4SocketAddress(n_u::Inet4Address::getByName(dest), 33501); //port);

  // compress the stream before sending it
  char compressed[32000];
  memset(compressed, 0, 32000);
  unsigned int bufLen = sizeof(compressed);
  int ret = BZ2_bzBuffToBuffCompress( compressed, &bufLen, buffer,
                                      strlen(buffer),9,0,0);
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
    char msg[100];
    sprintf(msg, "Failed to compress the ground feed stream: %s\n", BZ2_bzerror(&b, &errnum) );
    cout << msg;
    return;
  }
  try {
//  _socket->sendto(compressed, bufLen, 0, *_to);
    _socket->sendto(buffer, strlen(buffer), 0, *_to);
  }
  catch (const n_u::IOException& e) {
    fprintf(stderr, "nimbus::GroundFeed: %s\n", e.what());
  }

//printf("\ncompressed %d -> %d\n", strlen(buffer), bufLen);
  printf("rebroadcasting to %s: %s\n", dest.c_str(), buffer);
}
