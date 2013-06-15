#include <QtCore/QCoreApplication>
#include "udp2sql.h"
#include <openssl/ssl.h>

int main(int argc, char *argv[])
{
  SSL_library_init();
  QCoreApplication app(argc, argv);

  // Parse arguments list
  int res = udp2sql::parseRunstring(argc,argv);
  if (res)
    return udp2sql::usage(argv[0]);

  udp2sql reader;

  app.exec();
}
