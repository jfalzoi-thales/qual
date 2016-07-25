%include mps-base.inc.ks
%include mps-host.inc.ks
#%include pkgs-base.inc.ks
#%include pkgs-map.inc.ks
%include pkgs-qual.inc.ks

%post
echo "mps-qual" > /etc/hostname
# save package list inside the image
rpm -qa | sort -f -V > /etc/mps-packages
%end

%post --nochroot --erroronfail
. $PWD/.buildconfig || exit 1
[ -z "$BUILD_VER" ] && BUILD_VER="$(date +%Y%m%d%H%M)-unkn"
# set version info in the image
echo "QUAL build $BUILD_VER" > $INSTALL_ROOT/etc/mps-release
# store the package list in the output directory too
cat $INSTALL_ROOT/etc/mps-packages > $MPSBIN/mps-qual-$BUILD_VER.packages
%end
