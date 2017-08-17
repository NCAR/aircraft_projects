# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi

umask 002

export PS1="[\u@$AIRCRAFT \W]\$ "

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

export CATALOG_UID=`id -u`
export CATALOG_GID=`id -g`

export CATALOG_PLANE=`echo $AIRCRAFT | cut -d _ -f 1 | awk '{print tolower($0)}'`

# User specific aliases and functions

alias ll='ls -la'
alias g=git
alias d=docker
alias dc=docker-compose
alias cmaps='cd ~/catalog-maps'
alias cingest='cd ~/catalog-ingest'
alias cproducts='cd ~/products'
alias ..='cd ..'
