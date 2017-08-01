# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi

umask 002

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

export CATALOG_UID=`id -u`
export CATALOG_GID=`getent group eol | cut -d : -f 3`

export CATALOG_PLANE=`echo $AIRCRAFT | cut -d _ -f 1 | awk '{print tolower($0)}'`

# User specific aliases and functions

alias g=git
alias d=docker
alias dc=docker-compose
