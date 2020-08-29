if [[ $# < 2 ]]; then
    echo "Missing arguments"
    exit 1
fi

package="$1"
workdir="$2"

if [ -d "$workdir" ]; then
    echo "Working directory already exists!"
    exit 1
fi

srcdir="$workdir"/src
mkdir -p "$srcdir"
pkgdir="$workdir"/pkg
mkdir -p "$pkgdir"

# Load reMarkable toolchain
source /usr/local/oecore-x86_64/environment-setup-cortexa9hf-neon-oe-linux-gnueabi

# Load package info and script
source "$(realpath "$package")"

# Fetch source files
git clone --quiet --recursive "$origin" "$srcdir"
pushd "$srcdir"
git checkout --quiet "$revision"
popd

# Run build script
build

# Run packaging script
package

# Create control file
ctldir="$pkgdir"/CONTROL
ctlfile="$ctldir"/control

mkdir -p "$ctldir"
echo "Package: $pkgname" >> "$ctlfile"
echo "Version: $pkgver" >> "$ctlfile"
echo "Section: $pkgsect" >> "$ctlfile"
echo "Description: $pkgdesc" >> "$ctlfile"
echo "Maintainer: $pkgmaint" >> "$ctlfile"
echo "Architecture: armv7-3.2" >> "$ctlfile"
echo "Priority: optional" >> "$ctlfile"

if [ ! -z "$pkgdeps" ]; then
    echo "Depends: $pkgdeps" >> "$ctlfile"
fi

# Create package
opkg-build "$pkgdir" "$workdir"
