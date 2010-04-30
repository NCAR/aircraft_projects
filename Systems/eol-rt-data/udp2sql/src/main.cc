#include <qapplication.h>

#include "udp2sql.h"
#include <openssl/ssl.h>

int main(int argc, char *argv[])
{
  SSL_library_init();
  QApplication app(argc, argv, false);

  udp2sql reader;

  app.exec();
 
}
