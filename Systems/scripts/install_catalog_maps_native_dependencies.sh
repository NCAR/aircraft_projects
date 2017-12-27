#!/bin/bash

#
# commands for initializing CatalogMaps native
#

if [ `whoami` != 'root' ]; then
  echo "ERROR: $0 must be run as 'root' user"
  exit 1
fi

\cd /tmp

#
# install ruby-install
#

wget -O ruby-install-0.6.1.tar.gz https://github.com/postmodern/ruby-install/archive/v0.6.1.tar.gz
tar -xzvf ruby-install-0.6.1.tar.gz
\cd ruby-install-0.6.1/
sudo make install

\cd /tmp

#
# install chruby
#

wget -O chruby-0.3.9.tar.gz https://github.com/postmodern/chruby/archive/v0.3.9.tar.gz
tar -xzvf chruby-0.3.9.tar.gz
cd chruby-0.3.9/
sudo make install

\cd /tmp

#
# clean up
#
rm -rf ruby-install-0.6.1* chruby-0.3.9*
