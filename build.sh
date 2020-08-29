error() {
    echo "$1" >&2
    exit 1
}

rtar() {
    tar --sort=name \
        --owner=0 --group=0 --numeric-owner \
        --mtime="1970-01-01T00:00Z" \
        --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
        $@
}

[[ $# < 2 ]] && error "Missing arguments"

package="$1"
workdir="$2"

# Create working directories
[[ -d $workdir ]] && error "Working directory already exists!"

srcdir="$workdir"/src
mkdir -p "$srcdir"

pkgdir="$workdir"/pkg
mkdir -p "$pkgdir"

ctldir="$workdir"/control
mkdir -p "$ctldir"

ardir="$workdir"/ar
mkdir -p "$ardir"

# Load reMarkable toolchain
source /usr/local/oecore-x86_64/environment-setup-cortexa9hf-neon-oe-linux-gnueabi

# Load package info and script
source "$(realpath "$package")"

[[ -z $pkgname ]] && error "Missing or empty “pkgname” variable"
[[ -z $pkgver ]] && error "Missing or empty “pkgver” variable"
[[ -z $license ]] && error "Missing or empty “license” variable"
[[ -z $section ]] && error "Missing or empty “section” variable"
[[ -z $maintainer ]] && error "Missing or empty “maintainer” variable"
[[ -z $arch ]] && arch=armv7-3.2
[[ -z $pkgdesc ]] && error "Missing or empty “description” variable"

# Fetch source files
git clone --quiet --recursive "$origin" "$srcdir"

# Run build script
pushd "$srcdir" > /dev/null
git checkout --quiet "$revision"
build
popd > /dev/null

# Run packaging script
package

# Create archives
pkgar="$ardir"/data.tar.gz
ctlar="$ardir"/control.tar.gz
versionar="$ardir"/debian-binary
arar="$workdir/${pkgname}_${pkgver}_${arch}.ipk"

echo "2.0" >> "$versionar"
rtar --transform="s/^${pkgdir//\//\\\/}/./" -zcf "$pkgar" "$pkgdir"

# Create control file and archive
ctlfile="$ctldir"/control

echo "Package: $pkgname" >> "$ctlfile"
echo "Version: $pkgver" >> "$ctlfile"
[[ ! -z $pkgdeps ]] && echo "Depends: $pkgdeps" >> "$ctlfile"
echo "License: $license" >> "$ctlfile"
echo "Section: $section" >> "$ctlfile"
echo "Maintainer: $maintainer" >> "$ctlfile"
echo "Architecture: $arch" >> "$ctlfile"
echo "Description: $pkgdesc" >> "$ctlfile"

rtar --transform="s/^${ctldir//\//\\\/}/./" -zcf "$ctlar" "$ctldir"
rtar --transform="s/^${ardir//\//\\\/}/./" -zcf "$arar" "$ardir"
