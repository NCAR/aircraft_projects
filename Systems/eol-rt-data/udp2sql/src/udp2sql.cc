#include "udp2sql.h"

#include <stdio.h>
#include <string.h>

#include <iostream>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <bzlib.h>
#include <QtCore/QTimerEvent>
#include <QtCore/QStringList>
#include <QtCore/QDateTime>
#include <QtCore/QFile>
#include <QtCore/QTextStream>

#include <nidas/util/Socket.h>
#include <nidas/util/Inet4Address.h>


using namespace std;

namespace n_u = nidas::util;

static const int DropDuration = 2;  // hours
static const int port = 31007;

#include <openssl/ripemd.h>


enum IWG1VARS {
    IWG1,
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
    SOLAR_AZ_AC
};

enum DC8VARS {
    VNS_MMS = 33,
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
    Sulfate_AMS_1um,
    Nitrate_AMS_1um,
    Ammonium_AMS_1um,
    Organic_AMS_1um,
    Chloride_AMS_1um,
    F43,
    F44,
    F57,
    F60
};

enum AOCVARS {
    FLID = 33,
    MISSIONID,
    STORMID,
    MDSHOUR_1,
    MDSMINUTE_1,
    MDSSECOND_1,
    AccZfilterI_GPS_1,
    AccZfilterI_GPS_2,
    ACCZref,
    AccZI_GPS_1,
    AccZI_GPS_2,
    ALTGA_d,
    AltGPS_1,
    AltGPS_2,
    AltGPS_3,
    AltI_GPS_1,
    AltI_GPS_2,
    AltRa_2,
    AltRa1_c,
    AltRa2_c,
    AXBT_1,
    AXBT_2,
    AXBT_3,
    COURSEcorr_d,
    DV_d,
    GPS_AltErr_1,
    GPS_Quality_1,
    GSXref,
    GSYref,
    HT_d,
    HUM_ABS_d,
    HUM_REL_d,
    IASkt_d,
    LicHum_Abs_1,
    LicCO2D_1,
    LicTDM_1,
    LicTTMi_1,
    LicTTMo_1,
    LicPT_1,
    LatGPS_1,
    LatGPS_2,
    LatGPS_3,
    LatI_GPS_1,
    LatI_GPS_2,
    LonGPS_1,
    LonGPS_2,
    LonGPS_3,
    LonI_GPS_1,
    LonI_GPS_2,
    LWC_1,
    MR_d,
    PDALPHA_1,
    PDALPHA_2,
    PDBETA_1,
    PDBETA_2,
    PitchI_1,
    PitchI_2,
    PitchI_GPS_1,
    PitchI_GPS_2,
    PitchI_GPS_3,
    PitchI_GPS_4,
    PitchRate_1,
    PQALPHA_1,
    PQBETA_1,
    PQM_2,
    PQM_3,
    PQM_4,
    PQM_1,
    PSM_2,
    PSM_1,
    PSURF_d,
    PTM_1,
    RollI_1,
    RollI_2,
    RollI_GPS_1,
    RollI_GPS_2,
    RollI_GPS_3,
    RollI_GPS_4,
    SfmrRainRate_R,
    SfmrWS_R,
    SST_1,
    TASkt_d,
    TDM_1,
    TDM_2,
    TDM_3,
    THdgI_GPS_1,
    THdgI_GPS_2,
    THdgI_GPS_3,
    THdgI_GPS_4,
    THETA_d,
    THETAE_d,
    TRadD_1,
    TRadS_1,
    TRadU_1,
    TRKdesired_d,
    TTM_1,
    TTM_2,
    TTM_3,
    TVIRT_d
};

/* -------------------------------------------------------------------- */
udp2sql::~udp2sql()
{
    cout << "exiting" << endl;

    // Clean up
    Py_DECREF(pModule);
    Py_DECREF(pName);

    // Finish the Python Interpreter
    Py_Finalize();
}

/* -------------------------------------------------------------------- */
udp2sql::udp2sql()
{
    cout << "compiled on " << __DATE__ << " at " << __TIME__ << endl;

    _conn = 0;
    _count = 0;
    newUDPConnection();

    _autoDBresetList.push_back("N42RF");
    _autoDBresetList.push_back("N43RF");
    _autoDBresetList.push_back("N49RF");
    _autoDBresetList.push_back("WKA");
    _autoDBresetList.push_back("C130");
    _autoDBresetList.push_back("GV");
    for (int i = 0; i < _autoDBresetList.size(); ++i)
    {
        _timer[_autoDBresetList[i]].start(DropDuration * 3600000, this);
        _newFlight[_autoDBresetList[i]] = 1;
    }

    // Initialize the Python Interpreter
    Py_InitializeEx(0);

    // Build the name object
    pName = PyString_FromString("decrypt");

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append(\"/home/local/Systems/eol-rt-data/udp2sql/src\")");

    // Load the module object
    pModule = PyImport_Import(pName);

    // pDict is a borrowed reference
    pDict = PyModule_GetDict(pModule);

    // pFunc is also a borrowed reference
    pFunc = PyDict_GetItemString(pDict, "decode");

    if (!PyCallable_Check(pFunc))
    {
        cout << "failing" << endl;
        // Clean up
        Py_DECREF(pModule);
        Py_DECREF(pName);

        // Finish the Python Interpreter
        Py_Finalize();
    }
}

/* -------------------------------------------------------------------- */
bool udp2sql::newPostgresConnection(string platform)
{
    string spec="user=data dbname=real-time-"+platform;
    if (platform == "GAUS")
    {
        spec="user=data dbname=soundings";
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

/* -------------------------------------------------------------------- */
void udp2sql::closePostgresConnection()
{
    if (_conn)
    {
        PQfinish(_conn);
    }
}

/* -------------------------------------------------------------------- */
int udp2sql::execute(const char* sql_str)
{
    PGresult * res;
    res = PQexec(_conn, sql_str);
    cout << PQerrorMessage(_conn);
    PQclear(res);
    return ( strlen(PQerrorMessage(_conn)) > 0 );
}

/* -------------------------------------------------------------------- */
string udp2sql::extractPQString(PGresult *result, int tuple, int field)
{
    const char* pqstring = PQgetvalue(result, tuple, field);
    if (! pqstring)
        return "";

    int len = strlen(pqstring);
    while (len > 0 &&
            isascii(pqstring[len-1]) &&
            isspace(pqstring[len-1]))
        len--;

    return string(pqstring, len);
}

/* -------------------------------------------------------------------- */
string udp2sql::getGlobalAttribute(PGconn *conn, string attr)
{
    string query = "SELECT value FROM global_attributes WHERE key='";
    query += attr + "'";
    PGresult * res = PQexec(conn, query.c_str());

    int ntuples = PQntuples(res);

    if (ntuples == 0)
    {
        cerr << "No global attribute " << attr << "!\n";
        return "";
    }
    string s = extractPQString(res, 0, 0);
    PQclear(res);
    return s;
}

/* -------------------------------------------------------------------- */
void udp2sql::resetRealTime(string aircraft)
{
    cout << aircraft << " Resetting real-time database" << endl;
    _newFlight[aircraft] = 1;
    return;

    // TODO - utilize setup files sent down via LDM here for the GV and C130 aircraft.

    QFile file( string("/home/local/Systems/eol-rt-data/postgres/"
                "real-time-"+aircraft+".sql").c_str() );
    if (!file.open(QFile::ReadOnly | QFile::Text)) return;
    QTextStream in(&file);
    QString line, longline;

    newPostgresConnection(aircraft);

    QString StartTime = QString( getGlobalAttribute(_conn, "StartTime").c_str() );

    // don't backup empty tables
    if (StartTime.length() == 0) {
        closePostgresConnection();
        cout << aircraft << " Resetting real-time database skipped (no data)" << endl;
        return;
    }
    // trim off the microsecond field from the StartTime (if any) and remove the delimiters
    StartTime.replace(QRegExp("\\.[0-9]+$"), "");
    int len = 0;
    while (len != StartTime.length()) {
        len = StartTime.length();
        StartTime.replace("-","");
        StartTime.replace(":","");
    }
    QStringList tables;
    tables << "variable_list" << "global_attributes" << "raf_lrt";
    for (int i = 0; i < tables.size(); ++i) {
        line = "ALTER TABLE " + tables[i] + " RENAME TO " + tables[i]
            + "_" + StartTime;
        cout << aircraft << " " << line.toStdString() << endl;
        execute(line.toStdString().c_str());
        line = "ALTER INDEX " + tables[i] + "_pkey RENAME TO " + tables[i]
            + "_pkey_" + StartTime;
        cout << aircraft << " " << line.toStdString() << endl;
        execute(line.toStdString().c_str());
    }
    while (!(line = in.readLine()).isNull()) {
        cout << aircraft << " " << line.toStdString() << endl;
        longline += line;
        if ( longline.endsWith(";") ) {
            execute(longline.toStdString().c_str());
            longline = "";
        }
    }
    closePostgresConnection();
}

/* -------------------------------------------------------------------- */
void udp2sql::newUDPConnection()
{
    _udp = new QUdpSocket();
    QHostAddress host;

    host.setAddress("0.0.0.0");        // Inhouse
    //host.setAddress("12.47.179.48"); // Reachback.

    cout << "conn = " << _udp->bind(host, port, QUdpSocket::ReuseAddressHint)
        << "\n";

    connect(_udp, SIGNAL(readyRead()), this, SLOT(readPendingDatagrams()));
}

/* -------------------------------------------------------------------- */
void udp2sql::timerEvent(QTimerEvent *event)
{
    for (int i = 0; i < _autoDBresetList.size(); ++i)
    {
        if (event->timerId() == _timer[_autoDBresetList[i]].timerId())
            resetRealTime(_autoDBresetList[i]);
    }
}

/* -------------------------------------------------------------------- */
namespace
{
    typedef std::map<std::string,std::string> passwords_t;
    passwords_t passwords;

    void
        init_passwords()
        {
            passwords["test1"] = "this will never work";
            passwords["iss1"] = "dc3-4ba";
            passwords["mgaus"] = "dc3-4ba";
            passwords["nssl1"] = "dc3-4ba";
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

/* -------------------------------------------------------------------- */
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
    char decrypted_space[65000];
    char* buffer = buffer_space;
    char* decrypted = decrypted_space;

    memset(udp_str, 0, 65000);
    memset(buffer, 0, 65000);
    memset(decrypted, 0, 65000);

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

    // if BZ_DATA_ERROR_MAGIC is returned then the stream is not compressed;
    // copy the initially read in udp_str into the prossessed buffer string.
    if (ret == BZ_DATA_ERROR_MAGIC)
    {
        memcpy(buffer, udp_str, nBytes);
    }
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
    //  cout << "buffer: " << buffer << endl;
    int AOClen = 0;

    // unencrypt messages from NOAA that begin with AOC
    if (strncmp(buffer, "AOCN42RF", 8) == 0)
        AOClen = 8;
    if (strncmp(buffer, "AOCN43RF", 8) == 0)
        AOClen = 8;
    if (strncmp(buffer, "AOCN49RF", 8) == 0)
        AOClen = 8;
    if (AOClen > 0) {
//      cout << &buffer[AOClen] << endl;

        // utilize imported Python decrypt
        pArgs = PyTuple_New(1);
        pValue = PyString_FromString(&buffer[AOClen]); //(const char *v)
        if (!pValue)
            PyErr_Print();

        PyTuple_SetItem(pArgs, 0, pValue);

        pValue = PyObject_CallObject(pFunc, pArgs);

        if (pArgs != NULL)
        {
            Py_DECREF(pArgs);
        }
        if (pValue != NULL)
        {
            decrypted = PyString_AsString(pValue);
            memset(buffer, 0, 65000);
            memcpy(buffer, decrypted, strlen(decrypted));
//          printf("Return of call : %s\n", buffer);
            Py_DECREF(pValue);
        }
        if (strstr(buffer, "IWG1_NAMES")) // don't process G4 IWG1_NAMES string.
            return;

        // Identify and prune the NOAA aircraft feeds
//      cout << "JDW0 " << buffer << endl;
        QString iwg1(buffer);
        QStringList iwg1List = iwg1.split(',', QString::KeepEmptyParts);
//      cout << "iwg1List[FLID]: " << iwg1List[FLID].toStdString() << endl;
        if (iwg1List[FLID][8] == 'H')
            iwg1List[0] = "N42RF";
        if (iwg1List[FLID][8] == 'I')
            iwg1List[0] = "N43RF";
        if (iwg1List[FLID][8] == 'N')
            iwg1List[0] = "N49RF";

//      iwg1List.removeAt(FLID);    // remove this pseudo ID located inline with the other values

        iwg1List.erase(iwg1List.begin()+FLID, iwg1List.end());

        iwg1 = iwg1List.join(",");
        memset(buffer, 0, 65000);
        memcpy(buffer, iwg1.toStdString().c_str(), iwg1.size());
//      cout << "JDW1 " << buffer << endl;
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
    else if (strncmp(buffer, "WKA", 3) == 0)   platform = "WKA";
    else if (strncmp(buffer, "DC8", 3) == 0)   platform = "DC8";
    else if (strncmp(buffer, "A10", 3) == 0)   platform = "A10";
    else if (strncmp(buffer, "GAUS:", 5) == 0) platform = "GAUS";
    else if (strncmp(buffer, "N42RF", 5) == 0) platform = "N42RF";
    else if (strncmp(buffer, "N43RF", 5) == 0) platform = "N43RF";
    else if (strncmp(buffer, "N49RF", 5) == 0) platform = "N49RF";
    else return;

    QDateTime dt = QDateTime::currentDateTime().toUTC();
    QString datetime = dt.toString("yyyyMMddTHHmmss");
    QString notes;

    // report on transferred amounts
    if (ret == BZ_OK)
        notes = QString("%1 %2 decompressed %3 -> %4").arg(platform.c_str()).arg(datetime).arg(nBytes).arg(bufLen);
    else
        notes = QString("%1 %2 received %3").arg(platform.c_str()).arg(datetime).arg(nBytes);

    if (platform == "GAUS")
    {
        handleSoundingMessage(platform, buffer);
    }
    else
    {
        handleAircraftMessage(platform, buffer, notes);
    }
}

/* -------------------------------------------------------------------- */
void udp2sql::handleSoundingMessage(string platform, char* buffer)
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

/* -------------------------------------------------------------------- */
void udp2sql::handleAircraftMessage(string aircraft, char* buffer, QString notes)
{
    /* TODO purge this?  it was allready trimmed down
       if (aircraft == "N49RF") // For G4 test on 01/09/2013
       {
       char *p = strstr(buffer, "N1");
       if (p)
       {
     *p = '\0';
     for (int i = 0; i < 5; ++i)
     {
     p = strrchr(buffer, ',');
     *p = '\0';
     }
     }
     }
     */
    cout << buffer << "\n";

    QString varsStr(buffer);

    // trim off '\r' and '\n' characters if present
    varsStr.replace("\r","");
    varsStr.replace("\n","");

    // remove all spaces
    int len = 0;
    while (len != varsStr.length()) {
        len = varsStr.length();
        varsStr.replace(", ",",");
    }
    // save a copy for re-broadcast later
    QString varsStrCopy(varsStr);

    // insert NANs for all missing values
    len = 0;
    while (len != varsStr.length()) {
        len = varsStr.length();
        varsStr.replace(",,",",-32767,");
        varsStr.replace(",nan",",-32767");
    }
    if (varsStr.endsWith(","))
        varsStr.append("-32767");

    // break the buffer into usable substrings
    QStringList varList = varsStr.split(",");

    // correct +/- 180 to 0..360 on wind direction
    if (strcmp(aircraft.c_str(), "DC8") == 0)
    {
        QString windDirectionStr = varList[WDC];
        double windDirection = varList[WDC].toDouble();
        //printf("[%s - ", varList[WDC].toAscii().data());
        //printf("%f - ", windDirection);
        if (windDirection < 0.0 && windDirection > -200.0) windDirection += 360.0;
        varList[WDC] = QString::number(windDirection, 'f', 1);
        //printf("%s]\n", varList[WDC].toAscii().data());
    }

    // remove the preceeding "platform,datetime,"
    varList.takeFirst();
    QString datetime = varList.takeFirst();

    // ignore messages that are missing datetime values
    if (datetime == "-32767") {
        //  cout << aircraft << " IGNORED missing datetime" << endl;
        return;
        //  QDateTime dt = QDateTime::currentDateTime().toUTC();
        //  datetime = dt.toString("yyyyMMddTHHmmss");
        //  cout << aircraft << " STUBBED in missing datetime: " << datetime.toStdString() << endl;
    }
    // trim off the microsecond field from the datetime
    datetime.replace(QRegExp("\\.[0-9]+$"), "");
    len = 0;
    while (len != datetime.length()) {
        len = datetime.length();
        datetime.replace("-","");
        datetime.replace(":","");
    }
    // ignore messages with with old datetime stamp
    QDateTime data_datetime = QDateTime::fromString( datetime, "yyyyMMddTHHmmss" );
    //  if ( data_datetime.addSecs(10) < QDateTime::currentDateTime().toUTC() )
    //    return;

    // passed all filters... start logging useful information
    cout << notes.toStdString() << endl;

    // update database entries
    if (newPostgresConnection(aircraft))
    {
        QString sql_str;
        // create postgres statements
        sql_str = "INSERT INTO raf_lrt VALUES ('" + datetime + "'," + varList.join(",") + ");";
        cout << aircraft << " " << sql_str.toStdString() << endl;

        // bail out on failed insert commands like these:
        // ERROR:  duplicate key violates unique constraint "raf_lrt_pkey"
        if (execute(sql_str.toStdString().c_str())) {
            closePostgresConnection();
            return;
        }
        if (_newFlight[aircraft]) {
            _newFlight[aircraft] = 0;
            _cntVacuum[aircraft] = 0;
            sql_str = "UPDATE global_attributes SET value='" + datetime + "' WHERE key='StartTime';";
            cout << aircraft << " " << sql_str.toStdString() << endl;
            execute(sql_str.toStdString().c_str());
        }
        sql_str = "UPDATE global_attributes SET value='" + datetime + ".999' WHERE key='EndTime';";
        cout << aircraft << " " << sql_str.toStdString() << endl;
        execute(sql_str.toStdString().c_str());

        // Vacuum the database at the start of a new flight... then every so often
        if (_cntVacuum[aircraft]++ % 1000 == 0) {
            sql_str = "VACUUM;";
            cout << aircraft << " " << sql_str.toStdString() << endl;
            execute(sql_str.toStdString().c_str());
        }
        closePostgresConnection();

        // restart database drop timer
        _timer[aircraft].start(DropDuration * 3600000, this);
    }

#if 0
    // re-broadcast message to other aircraft
    if (strncmp(aircraft.c_str(), "DC8", 3) == 0) {

        // send every 20 seconds
        if (_count++ % 4) return;

        // break the buffer into usable substrings
        QStringList varListCopy = varsStrCopy.split(",");

        // prune un-needed variables
        varListCopy.removeAt(F60);
        varListCopy.removeAt(F57);
        varListCopy.removeAt(F44);
        varListCopy.removeAt(F43);
        varListCopy.removeAt(Chloride_AMS_1um);
        varListCopy.removeAt(Organic_AMS_1um);
        varListCopy.removeAt(Ammonium_AMS_1um);
        varListCopy.removeAt(Nitrate_AMS_1um);
        varListCopy.removeAt(Sulfate_AMS_1um);
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
        //  varListCopy.removeAt(THDG);
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
#endif
}

/* -------------------------------------------------------------------- */
void udp2sql::reBroadcastMessage(string dest, char* buffer)
{
    n_u::DatagramSocket * _socket;
    n_u::Inet4SocketAddress * _to;

    try {
        _socket = new n_u::DatagramSocket;
        _to = new n_u::Inet4SocketAddress(n_u::Inet4Address::getByName(dest), 33501); //port);
    }
    catch (const n_u::UnknownHostException& e) {
        cout << "reBroadcastMessage:UnknownHostException: " << e.what() << endl;
        return;
    }
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
        cout << "reBroadcastMessage:IOException: " << e.what() << endl;
        return;
    }
    cout << "rebroadcasted to " << dest.c_str() << ": " << buffer << endl;
}
