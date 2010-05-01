// -*- C++ -*-

#include <libpq-fe.h>

#include <qhostaddress.h>
#include <qsocketdevice.h>
#include <qsocketnotifier.h>
#include <sys/time.h>

#include <map>
#include <string>

/**
 * Class to read UDP broadcast data from EOL aircraft, reformat the
 * data and insert it into the eol-rt-data exposed host database.
 */
class udp2sql : public QObject
{
  Q_OBJECT;

public:
  typedef std::string string;

  udp2sql();

  void
  setConnectionQualifier(const std::string& qspec)
  {
    _qspec = qspec;
  }

protected slots:
  void	newData();
  void	timerEvent(QTimerEvent *);

protected:
  void  newUDPConnection();
  bool  newPostgresConnection(string platform);
  void  closePostgresConnection();
  void  execute(const char* sql_str);

  void  handleSoundingMessage(string platform, char* buffer);
  void  handleAircraftMessage(string aircraft, char* buffer);

  QSocketDevice * _udp;
  QSocketNotifier * _notify;

  // If a watchdog timer is desired.
  int _timer_id;

  PGconn * _conn;

  // Special qualifier to add to connection string, such as to specify
  // host=<host> and port=<port>.  The user and database will always
  // be specified explicitly, and this string will be appended.
  string _qspec;

};

