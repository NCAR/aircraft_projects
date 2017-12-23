#!/bin/bash

# set -eux

#
# initializing an acserver for native CatalogMaps
#

if [ `whoami` != 'catalog' ]; then
  echo "ERROR: $0 must be run as 'catalog' user"
  exit 1
fi

if [ ! -f ~/.ssh/id_rsa ]; then
  echo "ERROR: SSH key ~/.ssh/id_rsa does not exist. Please add SSH key."
  exit 1
fi

#
# install rbenv to ~/.rbenv
#

wget -O /tmp/rbenv-v1.1.1.tar.gz https://github.com/rbenv/rbenv/archive/v1.1.1.tar.gz
mkdir ~/.rbenv
cd ~/.rbenv
tar xvf /tmp/rbenv-v1.1.1.tar.gz --strip-components=1
./src/configure && make -C src
echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(~/.rbenv/bin/rbenv init -)"'  >> ~/.bashrc

. ~/.bash_profile

#
# install ruby-build as rbenv plugin
#
mkdir -p "$(rbenv root)"/plugins
git clone https://github.com/rbenv/ruby-build.git "$(rbenv root)"/plugins/ruby-build

# source ~/.bashrc

curl -fsSL https://github.com/rbenv/rbenv-installer/raw/master/bin/rbenv-doctor | bash

#
# install dependencies
#

sudo yum install -y openssl-devel gcc-c++ libxml2-devel mariadb-devel readline-devel zlib-devel

#
# git clone catalog-maps
#

\cd

git clone git@github.com:ncareol/catalog-maps.git catalog-maps-native

echo '2.3.3' > catalog-maps-native/.ruby-version

cd catalog-maps-native

rbenv install -v

gem install bundler

bundle --path vendor --local

cat <<DB > config/database.native.yml

defaults: &defaults
  adapter: mysql2
  encoding: utf8
  database: catalog
  username: docker
  password: docker
  pool: 5
  timeout: 5000
  host: 127.0.0.1
  port: 3306

development:
  <<: *defaults

# Warning: The database defined as "test" will be erased and
# re-generated from your development database when you run "rake".
# Do not set this db to the same as development or production.

test:
  <<: *defaults
  database: catalog_test

production:
  <<: *defaults

DB

cd config

ln -s database.native.yml database.yml

ln -s catalog.acserver.yml catalog.yml
