#
# new commands for initializing an acserver for CatalogMaps
#

if [ `whoami` != 'catalog' ]; then
  echo "ERROR: $0 must be run as 'catalog' user"
  exit 1
fi

if [ ! -f ~/.ssh/id_rsa ]; then
  echo "ERROR: SSH key ~/.ssh/id_rsa does not exist. Please add SSH key."
  exit 1
fi

if [ ! -f ~/.ssh/ingest_deploy_key_rsa ]; then
  echo "ERROR: SSH key ~/.ssh/ingest_deploy_key_rsa does not exist. Please add SSH key."
  exit 1
fi

#
# verify that CATALOG_PLANE is set
#
if [ -z "$CATALOG_PLANE" ]; then
  echo "ERROR: Environment variable CATALOG_PLANE is not set or is empty. Please set CATALOG_PLANE."
  exit 1
fi

echo "plane: $CATALOG_PLANE"

\cd

#
# git clone maps, ingest
#
for APP in 'ingest' 'maps'; do

  echo "setting up $APP"

  if [ $APP = 'ingest' ] ; then
    REPO=ssh://github-catalog-ingest/ncareol/catalog-$APP.git
  else
    REPO=git@github.com:ncareol/catalog-$APP.git
  fi

  git clone $REPO
  \cd catalog-$APP

  if [ $APP = 'ingest' ] ; then
    git checkout feature-dockerize
    _hook=etc/acserver/post-receive
  else
    git checkout master
    _hook=config/hooks/$CATALOG_PLANE/post-receive
  fi

  #
  # Easy-Deploy hook
  #

  cp -v $_hook .git/hooks/post-receive

  #
  # add '[receive]' section to .git/config
  #
  if ! grep -lq '\[receive\]' .git/config ; then
    echo 'adding [receive] section to .git/config'
    cat <<GITCONFIG >> .git/config
  [receive]
      denyCurrentBranch = ignore
GITCONFIG
  fi

  if [ $APP = 'ingest' ] ; then
    #
    # touch ingest project PID file
    #
    touch tmp/$CATALOG_PLANE-monitor-queue.pid
  fi

  \cd

done

\cd catalog-maps

# link config files
ln -s docker/docker-compose.acserver.yml docker-compose.yml

docker-compose pull
docker-compose build

docker-compose run app bundle --path vendor --local
docker-compose run ingest bundle --path vendor --local

docker-compose run app ./bin/rake map:load[config/map/$CATALOG_PLANE.yml]

docker-compose run app ./bin/rake assets:precompile

sudo systemctl start catalog-maps
