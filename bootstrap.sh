#!/bin/sh

#
# Bootstrap 0.1.0 for reMarkable (rM2 untested)
# wget -qO- '<URL_to_bootstrap.sh>' | sh -s [packages]...
#

bootstrap_wget() {
  if [ ! -d /home/root/.cache/wget_bin ]
  then
      log INFO "Installing a current wget binary with better and current tls support" \
          "to /home/root/.cache/wget_bin/ for this installation..." \
          ""
      # Bootstrap a current version of wget
      WGET_BINARIES_PATH='http://github.com/LinusCDE/wget-remarkable-pipeline/releases/download/job254'
      WGET_BINARIES_FILENAME='wget-remarkable-pipeline_job245_wget1.20.3.zip'
      WGET_BINARIES_SHA256='84185a5934e34e25794d439c78dc9f1590e4df12fbf369236f6a8749bf14d67f'

      # Download and compare to hash
      wget "$WGET_BINARIES_PATH/$WGET_BINARIES_FILENAME" -O "/home/root/$WGET_BINARIES_FILENAME"
      if ! echo "$WGET_BINARIES_SHA256  /home/root/$WGET_BINARIES_FILENAME" | sha256sum -c -
      then
          echo "FATAL: Invalid hash" >&2
          exit 1
      fi

      # Ensure to /home/root/.cache/wget_bin exists and is empty
      if [ -d /home/root/.cache/wget_bin ]
      then
          rm -rf /home/root/.cache/wget_bin/*
      else
          mkdir -p /home/root/.cache/wget_bin
      fi
      # Unzip to /home/root/.cache/wget_bin and remove downloaded file
      unzip "/home/root/$WGET_BINARIES_FILENAME" -d /home/root/.cache/wget_bin -q
      rm "/home/root/$WGET_BINARIES_FILENAME"

      cat > /home/root/.cache/wget_bin/wget <<EOF
#!/bin/sh
LD_LIBRARY_PATH="/home/root/.cache/wget_bin/dist" /home/root/.cache/wget_bin/dist/wget \$@
EOF

      chmod +x /home/root/.cache/wget_bin/wget
  fi

  # Ensure this binary is used
  if [ `which wget` != '/home/root/.cache/wget_bin/wget' ]; then
    PATH="/home/root/.cache/wget_bin:$PATH"
  fi
}

main() {
  # Allow changing the default branch
  [ ! -z "$TOLTEC_BRANCH" ] || TOLTEC_BRANCH="stable"

  # Select source for remarkable_entware repo
  if [ -z "$REMARKABLE_ENTWARE_REPO_AUTHOR" ]; then
    # Use LinusCDE's fork for the time beeing
    # TODO: Switch to a more official repo when it exists
    REMARKABLE_ENTWARE_REPO_AUTHOR=LinusCDE
  fi

  # Check status of installation and ensure installed
  if [ -d /home/root/.entware ]; then
    if [ -d /opt ] && [ `ls /opt | wc -l` -gt 0 ]; then # non-empty /opt found
      # Entware is installed and active
      log INFO "Entware is installed and active"
    else
      # Installed but not active
      log INFO "Entware is installed but not reenabled"
      entware_reenable
    fi
  else # = not found: /home/root/.entware
    # Not installed at all
    log INFO "Entware is not installed"
    entware_install
  fi

  # Ensure opkg is in PATH
  ensure_opkg_available
  # Ensure wget is installed as opkg package
  ensure_opt_wget_and_ca_certs_installed
  # Add toltec repo if mising
  ensure_toltec_repo_added

  if [ $# -ge 1 ]; then
    install_packages $@ || throw "Failed to install requested packages"
  fi

}


entware_install() {
  bootstrap_wget || throw "bootstrap_wget() failed!"
  (wget -O- "https://raw.githubusercontent.com/$REMARKABLE_ENTWARE_REPO_AUTHOR/remarkable_entware/master/entware_install.sh" | sh) \
    || throw "Failed to download and/or install remarkable_entware."
  log INFO "Entware was installed successfully."
}


entware_reenable() {
  bootstrap_wget || throw "bootstrap_wget() failed!"
  (wget -O- "https://raw.githubusercontent.com/$REMARKABLE_ENTWARE_REPO_AUTHOR/remarkable_entware/master/entware_reenable.sh" | sh) \
    || throw "Failed to download and/or install remarkable_entware."
  log INFO "Entware was reenabled successfully."
}


ensure_opkg_available_from_bashrc() {
  # Run by ensure_opkg_available
  if ! grep '.*PATH=.*/opt/bin.*' /home/root/.bashrc | grep -v '^#' >/dev/null; then
    # Path is not in .bashrc
    echo -e '\n# Path added by bootstrap.sh' >> /home/root/.bashrc
    echo 'PATH="/opt/bin:/opt/sbin:$PATH"' >> /home/root/.bashrc
    log WARN '/opt/bin and /opt/sbin were not added to $PATH in ~/.bashrc. Fixed automatically.'
  fi
}


ensure_opkg_available() {
  if ! which opkg >/dev/null 2>&1; then # opkg command not found
    export PATH="/opt/bin/:/opt/sbin/:$PATH"
    messages=`ensure_opkg_available_from_bashrc`
    if [ ! -z "$messages" ]; then
      echo "$messages" # Print the caught output
      log WARN "Please re-connect to your reMarkable after this" \
               "script is finished. Otherwise opkg and other" \
               "installed binaries won't be recognized!"
    fi
  else
    ensure_opkg_available_from_bashrc
  fi
}


ensure_toltec_repo_added() {
  if ! grep "^src/gz\b.*\bhttps://toltec\.delab\.re/" /opt/etc/opkg.conf >/dev/null 2>&1; then
    # No active toltec repo found in opkg.conf
    echo "src/gz toltec https://toltec.delab.re/$TOLTEC_BRANCH" >> /opt/etc/opkg.conf
    opkg update || throw "Failed to update opkg after adding toltec $TOLTEC_BRANCH repo"
    log INFO "Added the toltec $TOLTEC_BRANCH repo to opkg"
  fi
}


ensure_opt_wget_and_ca_certs_installed() {
  # Those packages might miss if someone had already
  # installed entware before.
  packages=""
  [ -d /opt/etc/ssl/certs ] || packages="$packages ca-certificates"
  [ -f /opt/bin/wget ] || packages="$packages wget"

  if [ ! -z "$packages" ]; then
    opkg update && opkg install $packages || throw "Failed to install packages for better https support"
    log INFO "Installed missing recommended packages for better https support"
  fi
}


install_packages() {
  [ $# -eq 0 ] && return

  if [ $# -eq 1 ]; then
    log INFO "Installing package: $1"
  else
    log INFO "Installing packages: $@"
  fi

  opkg install $@
}

log() {
  [ $# -ge 2 ] || throw "log() invalid usage: at least 2 parameters needed. Usage: log <type> <message_line>..."

  log_type="$1"
  fd=1 # To stdout

  case "$log_type" in
    'info'  | 'INFO'  | 'Info' ) colored_prefix='\e[32mINFO:\e[0m  ';;
    'warn'  | 'WARN'  | 'Warn' ) colored_prefix='\e[33mWARN:\e[0m  ';;
    'error' | 'ERROR' | 'Error') colored_prefix='\e[31mERROR:\e[0m '; fd=2;;
    'fatal' | 'FATAL' | 'Fatal') colored_prefix='\e[31mFATAL:\e[0m '; fd=2;;
    * ) throw "log() invalid usage: Unknown type: $log_type";;
  esac

  echo -e "${colored_prefix}$2" >&$fd
  # Extra lines to print indented
  shift 2
  for line in "$@"; do
    echo -e "       $line" >&$fd
  done
}


throw() {
  # Fatal error and quit
  log FATAL "$@" \
      "" \
      "This script failed to install. If you can't solve the above" \
      "reason yourself, create an issue and tag @LinusCDE here: " \
      "https://github.com/toltec-dev/toltec/issues" \
      "(Please also include these error logs to help solving the" \
      "problem faster. Thank you!)"
  exit 1
}


main $@
