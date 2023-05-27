#!/bin/bash -ex

path=${1:-/tmp/deb}
repo=${2:-https://github.com:aldum/bip39-monero-derive.git}
CHROOT=${3:-artix-chroot}
DEBOOTSTRAP=(debootstrap --no-check-certificate)

sudo mkdir -p "$path"
sudo "${DEBOOTSTRAP[@]}" stable "$path" # http://deb.debian.org/debian/
sudo "$CHROOT" "$path" apt update
sudo "$CHROOT" "$path" apt install -y vim git \
  python3 python3-pip python3-venv libpython3.9-dev
sudo "$CHROOT" "$path" /sbin/useradd -m user -s /bin/bash
sudo "$CHROOT" "$path" su -c 'mkdir ~/dev' user
git clone "$repo" "$path/home/user/dev/b39mmc"
