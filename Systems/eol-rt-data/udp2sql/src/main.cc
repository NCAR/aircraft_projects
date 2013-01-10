#include <QtCore/QCoreApplication>
#include "udp2sql.h"
#include <openssl/ssl.h>

int main(int argc, char *argv[])
{
  SSL_library_init();
  QCoreApplication app(argc, argv);

  udp2sql reader;
  if (argc > 1)
  {
    reader.setConnectionQualifier(argv[1]);
  }

  app.exec();
}
