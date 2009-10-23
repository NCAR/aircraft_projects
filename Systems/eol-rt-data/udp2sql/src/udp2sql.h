#include <libpq-fe.h>

#include <qhostaddress.h>
#include <qsocketdevice.h>
#include <qsocketnotifier.h>
#include <sys/time.h>

#include <map>
#include <string>
using namespace std;

/**
 * Class to read UDP broadcast data from EOL aircraft, reformat the
 * data and insert it into the eol-rt-data exposed host database.
 */
class udp2sql : public QObject
{
  Q_OBJECT

public:
  udp2sql();

protected slots:
  void	newData();
  void	timerEvent(QTimerEvent *);

protected:
  void	newUDPConnection();
  void	newPostgresConnection(string aircraft);

  QSocketDevice * _udp;
  QSocketNotifier * _notify;

  // If a watchdog timer is desired.
  int _timer_id;

  PGconn * _conn;
};

