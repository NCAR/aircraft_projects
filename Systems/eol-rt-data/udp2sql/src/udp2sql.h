// -*- C++ -*-

#include <libpq-fe.h>

#include <qhostaddress.h>
#include <QtCore/QTimerEvent>
#include <QtCore/QBasicTimer>
#include <QtNetwork/QUdpSocket>
#include <sys/time.h>

#include <map>
#include <string>

#undef _XOPEN_SOURCE
#undef _POSIX_C_SOURCE
#include <Python.h>


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
    ~udp2sql();

    void setConnectionQualifier(const std::string& qspec)
    {
        _qspec = qspec;
    }

    static int usage(const char* argv0);
    static int parseRunstring(int argc, char** argv);

    protected slots:
    void newData();
    void readPendingDatagrams();
    void timerEvent(QTimerEvent *);

    protected:
    PyObject *pName, *pModule, *pDict, *pFunc, *pArgs, *pValue;

    string extractPQString(PGresult *result, int tuple, int field);
    string getGlobalAttribute(PGconn *conn, string attr);
    void  resetRealTime(string aircraft);
    void  newUDPConnection();
    bool  newPostgresConnection(string platform);
    void  closePostgresConnection();
    int   execute(const char *sql_str);

    void  handleSoundingMessage(string platform, char* buffer);
    void  handleAircraftMessage(string aircraft, char* buffer, QString notes);
    void  reBroadcastMessage(string dest, char* buffer);

    QUdpSocket * _udp;

    /**
     * This is the list of platforms that will do an auto clear of the DB if there is no new data after
     * several hours.  Usually outside users e.g. NASA DC8 and NOAA G4.
     */
    std::vector<std::string> _autoDBresetList;
    std::map<std::string, QBasicTimer> _timer;
    std::map<std::string, int> _newFlight;

    std::map<std::string, int> _cntVacuum;

    PGconn *_conn;

    int _count;

    /**
     * Special qualifier to add to connection string, such as to specify
     * host=<host> and port=<port>.  The user and database will always
     * be specified explicitly, and this string will be appended.
     */
    string _qspec;

};

