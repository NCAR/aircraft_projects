#
# new commands for initializing an acserver for CatalogMaps
#

if [ `whoami` != 'catalog' ]; then
  echo "ERROR: $0 must be run as 'catalog' user"
  exit 1
fi

for CATALOG_SSH_KEY in 'id_rsa' 'ingest_deploy_key_rsa' 'maps_aircraft_assets_deploy_key_rsa'; do
  if [ ! -f ~/.ssh/$CATALOG_SSH_KEY ]; then
    echo "ERROR: SSH key ~/.ssh/$CATALOG_SSH_KEY does not exist. Please add SSH key."
    exit 1
  fi
done

#
# CATALOG_PLANES: set up acserver for both aircraft, to better handle case where acserver switches aircraft
#
CATALOG_PLANES=(c130 gv)

\cd

#
# git clone maps, ingest, maps-aircraft-assets
#
for APP in 'catalog-ingest' 'catalog-maps' 'maps-aircraft-assets'; do

  echo "setting up $APP"

  if [ $APP = 'catalog-ingest' ] ; then
    REPO=ssh://github-catalog-ingest/ncareol/catalog-ingest.git
  elif [ $APP = 'maps-aircraft-assets' ]; then
    REPO=ssh://github-maps-aircraft-assets/NCAR/maps-aircraft-assets.git
  else
    REPO=git@github.com:ncareol/catalog-maps.git
  fi

  git clone $REPO
  \cd $APP

  if [ $APP = 'catalog-ingest' ] ; then
    git checkout feature-dockerize
    _hook=etc/acserver/post-receive
  elif [ $APP = 'maps-aircraft-assets' ]; then
    git checkout master
    _hook=hooks/post-receive
  else
    git checkout master
    _hook=config/hooks/acserver/post-receive
  fi

  #
  # Easy-Deploy hook
  #

  cd .git/hooks
  ln -s ../../$_hook
  cd ../../

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

  if [ $APP = 'catalog-ingest' ] ; then
    #
    # touch ingest project PID file
    #
    for CATALOG_PLANE in "${CATALOG_PLANES[@]}"; do
      touch tmp/$CATALOG_PLANE-monitor-queue.pid
    done
  elif [ $APP = 'maps-aircraft-assets' ]; then
    ./bin/link-assets
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

for CATALOG_PLANE in "${CATALOG_PLANES[@]}"; do
  docker-compose run app ./bin/rake map:load[config/aircraft/$CATALOG_PLANE.yml]
done

docker-compose run app ./bin/rake assets:precompile

sudo systemctl start catalog-maps@app.service
sudo systemctl start catalog-maps@db.service
sudo systemctl start catalog-maps@ingest.service
sudo systemctl start catalog-maps@osm.service

