#include <qapplication.h>

#include "udp2sql.h"

int main(int argc, char *argv[])
{
  QApplication app(argc, argv, false);

  udp2sql reader;

  app.exec();
 
}
