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
# verify that chruby is installed
#
if [ ! -d /usr/local/share/chruby ]; then
  echo "chruby does not appear to be installed. Please install chruby"
  exit 1
fi

#
# verify that ruby-install is installed and in $PATH
#
if [ ! -x "$(command -v ruby-install)" ] ; then
  echo "ruby-install is not installed or not in $PATH. Please correct this to continue."
  exit 1
fi

RUBY_VERSION=2.3.3

#
# install ruby
#
ruby-install ruby-$RUBY_VERSION

#
# source chruby in case we just installed it and haven't started a new shell
#   and to make it aware of newly installed ruby version
#
source /usr/local/share/chruby/chruby.sh
source /usr/local/share/chruby/auto.sh

#
# install dependencies
#

sudo yum install -y openssl-devel gcc-c++ libxml2-devel mariadb-devel readline-devel zlib-devel

#
# git clone catalog-maps
#

\cd

git clone git@github.com:ncareol/catalog-maps.git catalog-maps-native

#
# echo version before cd so that chruby auto switches to this version on `cd`
#
echo $RUBY_VERSION > catalog-maps-native/.ruby-version

cd catalog-maps-native

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
