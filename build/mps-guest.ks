%include mps-base.inc.ks
%include pkgs-guest.inc.ks

bootloader --append=" console=tty0 console=ttyS0,115200n8"


%post
# Set hostname
echo "mps-guest" > /etc/hostname
# save package list inside the image
rpm -qa | sort -f -V > /etc/mps-packages
%end

%post --nochroot --erroronfail
. $PWD/.buildconfig || exit 1
[ -z "$BUILD_VER" ] && BUILD_VER="$(date +%Y%m%d%H%M)-unkn"
# set version info in the image
echo "mps-guest build $BUILD_VER" > $INSTALL_ROOT/etc/mps-release
# store the package list in the output directory too
cat $INSTALL_ROOT/etc/mps-packages > $MPSBIN/mps-guest-$BUILD_VER.packages
%end
