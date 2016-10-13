#!/bin/bash

# Execute command and redirect its stdout/stderr to log files.
# Dump log to stdout if command failed.
# Example usage:
#   logged_exec tmp/syslinux-install-deps.log yum-builddep -y syslinux.spec || exit 1
logged_exec() {
	LOG_FILE="$1"
	CMD="$2"
	shift 2

	echo -e "\n---------------------\n$CMD $@" >> "$LOG_FILE"
	"$CMD" "$@" >> "$LOG_FILE" 2>&1
	RET=$?

	if [ $RET -ne 0 ]; then
		buildenv_log "buildenv" "Executing '$CMD' failed"
		echo
		echo "Command '$CMD $@' failed! Here's log file:"
		echo
		cat "$LOG_FILE"
	fi

	return $RET
}

# This file helps debugging the build environment itself.
buildenv_log() {
	PKG=$1
	shift
	echo "`date +%Y-%m-%dT%H:%M:%S.%3N` `printf %-24s "$PKG:"` $@" >> $MPSTMP/buildenv.log
}
buildenv_log_verbose() {
	PKG=$1
	shift
	LINE="`date +%Y-%m-%dT%H:%M:%S.%3N` `printf %-24s "$PKG:"` $@"
	echo "$LINE" 1>&2
	echo "$LINE" >> $MPSTMP/buildenv.log
}


# remove log file
rm_log() {
	PKG=$1
	rm -f $MPSTMP/$PKG.log
}

# Clone package from repository
clone_package() {
	PKG=$1
	# Override package we want to get from tklabs instead of mapcollab repo
	if [ $PKG = "kmod-igb" ]; then
		GIT_URL=https://repo-tav.tklabs.com:8201/scm/qual
	fi
	if [ ! -d $MPSSRC/$PKG ]; then
		buildenv_log_verbose $PKG "Clonning $PKG to $MPSSRC/$PKG..."
		logged_exec $MPSTMP/$PKG.log git clone $GIT_URL/$PKG.git $MPSSRC/$PKG || exit 1
	elif [ -d $MPSSRC/$PKG/.git ] && [ "$OFFLINE" != "1" ]; then
		buildenv_log_verbose $PKG "Updating $PKG..."
		pushd $MPSSRC/$PKG >/dev/null
		logged_exec $MPSTMP/$PKG.log git pull || exit 1
		logged_exec $MPSTMP/$PKG.log git fetch --tags || exit 1
		popd >/dev/null
	fi
}


# return spec file name
package_spec_file() {
	PKG=$1
	pushd $MPSSRC/$PKG >/dev/null
	ls $PKG*.spec | sort | head -n1
	popd >/dev/null
}

# returns list of rpm files of the package currently present in the repo
package_rpm_files() {
	PKG=$1
	REPO=$2
	SILENT=$3
	SPEC=$(package_spec_file $PKG)
	pushd $MPSSRC/$PKG >/dev/null
	for SUBPKG in `rpmspec -q --qf "%{NAME}\n" $SPEC` `rpmspec -q --qf "%{NAME}\n" --target=i686 $SPEC`; do
		find $REPO -type f -regextype posix-extended -regex ".*/${SUBPKG/+/\+}-[^-]+-[^-]+.rpm" ! -name *.src.rpm -print | grep .
		[ $? -ne 0 -a $SILENT -eq 0 ] && buildenv_log_verbose $PKG "no RPMs found for subpackage $SUBPKG"
	done | sort | uniq
	popd >/dev/null
}

# return tito's project name (first part of tag string)
package_project_name() {
	PKG=$1
	SPEC=$(package_spec_file $PKG)
	pushd $MPSSRC/$PKG >/dev/null
	rpm -q --qf '%{name}\n' --specfile $SPEC 2>/dev/null | grep -e '^$' -v | head -1
	popd >/dev/null
}

# return most recent tito tag (from which build would be done if no --test is specified)
package_most_recent_tag() {
	PKG=$1
	pushd $MPSSRC/$PKG >/dev/null
	PNAME=$(package_project_name $PKG)
	awk '{ print "'$PNAME'-"$1 ; exit }' ".tito/packages/$PNAME"
	popd >/dev/null
}

# converts package tag to git revision
package_tag_to_rev() {
	PKG=$1
	TAG=$2
	pushd $MPSSRC/$PKG >/dev/null
	TAG_SHA1=$(git ls-remote ./. --tag $TAG | awk '{ print $1 ; exit }')
	git rev-list --max-count=1 "$TAG_SHA1"
	popd >/dev/null
}


# decides if package should be build in test mode
package_do_test_build() {
	PKG=$1
	RET=0
	# do untagged build only if we're doing testing build and HEAD != last_tag
	if [ $TESTBLD -eq 1 ]; then
		pushd $MPSSRC/$PKG >/dev/null
		TAG=$(package_most_recent_tag $PKG 2>/dev/null)
		TAG_REV=$(package_tag_to_rev $PKG $TAG 2>/dev/null)
		HEAD=$(git log --pretty=format:%H --max-count=1 .)
		[ -z "$TAG" -o "$TAG_REV" != "$HEAD" ] && RET=1
		buildenv_log $PKG "* btype: TAG=$TAG"
		buildenv_log $PKG "* btype: HEAD=$HEAD TAG_REV=$TAG_REV"
		buildenv_log $PKG "* btype: PKG_TESTBUILD=$RET"
		popd >/dev/null
	fi
	echo $RET
}

# return package revision which will be build by tito
package_rev() {
	PKG=$1
	PKG_TESTBUILD=$2
	pushd $MPSSRC/$PKG >/dev/null
	if [ $PKG_TESTBUILD -eq 1 ]; then
		REV=$(git log --pretty=format:%H --max-count=1 .)
		buildenv_log $PKG "package_rev: HEAD=$REV"
	else
		TAG=$(package_most_recent_tag $PKG 2>/dev/null)
		REV=$(package_tag_to_rev $PKG $TAG)
		buildenv_log $PKG "package_rev: TAG_REV=$REV TAG=$TAG"
	fi
	echo $REV
	popd >/dev/null
}

# get package tag for stable build
package_tag() {
	PKG_NAME=$1
	PKG_TESTBUILD=$2

	if [ $PKG_TESTBUILD -eq 0 ]; then
		while read PKG PKG_TAG; do
			[[ -z $PKG || $PKG = \#* ]] && continue
			if [ $PKG_NAME == $PKG ]; then
				echo $PKG_TAG
				return
			fi
		done < <(cat $TOPDIR/config/package.tags $TOPDIR/config/kernel.tags)
	fi
	echo ""
}

# return name of "package was already built" marker file name
package_built_marker() {
	PKG=$1
	[ $TESTBLD -eq 1 ] && echo "$MPSTMP/$PKG.testing.built" || echo "$MPSTMP/$PKG.stable.built"
}

# Check if package rpms exists
package_rpm_exists() {
	PKG=$1
	REPO=$2
	RPMLIST=$3
	MARKER=$4

	ALL_RPMS_FOUND=1
	while read RPM; do
		if [ ! -f "$REPO/x86_64/$RPM" -a ! -f "$REPO/noarch/$RPM"  -a ! -f "$REPO/i686/$RPM" -a ! -f "$REPO/$RPM" ]; then
			buildenv_log $PKG "do build? $RPM not found in repo; REBUILD NEEDED"
			ALL_RPMS_FOUND=0
			break
		fi
	done < "$RPMLIST"

	if [ $ALL_RPMS_FOUND -eq 1 ]; then
		buildenv_log $PKG "do build? `basename $MARKER`=$LAST_BUILD_REV; rebuild not needed"
		return 0
	fi
	return 1
}

# Check if the package needs to be built (exit code 0: needs building / 1: does not need)
package_needs_building() {
	PKG=$1
	REPO=$2
	PKG_TESTBUILD=$3
	PKG_CURRENT_REV=$4
	PKG_TAG=$5
	MARKER=$(package_built_marker $PKG)
	RPMLIST=${MARKER/.built/.rpms}

	if [ ! -f $MARKER ]; then
		buildenv_log $PKG "do build? `basename $MARKER` does not exist; 1st BUILD NEEDED"
	elif [ ! -f $RPMLIST ]; then
		buildenv_log $PKG "do build? `basename $RPMLIST` does not exist; (re)BUILD NEEDED"
	else
		LAST_BUILD_REV=`cat $MARKER`
		if [ $PKG_TESTBUILD -eq 0 ] && [ "$PKG_TAG" != "" ]; then
			# check if tag matches and all expected RPMs exists in the repo
			if [ "$LAST_BUILD_REV" == "$PKG_TAG" ] && package_rpm_exists $PKG $REPO $RPMLIST $MARKER; then
				return 1
			fi
		elif [ -n "$LAST_BUILD_REV" -a -n "$PKG_CURRENT_REV" -a "$LAST_BUILD_REV" == "$PKG_CURRENT_REV" ]; then
			# check if all expected RPMs exists in the repo
			if package_rpm_exists $PKG $REPO $RPMLIST $MARKER; then
				return 1
			fi
		else
			buildenv_log $PKG "do build? `basename $MARKER`=$LAST_BUILD_REV; REBUILD NEEDED"
		fi
	fi
	rm -f "$MARKER" "$RPMLIST"
	return 0
}

# install package build dependencies
install_package_deps() {
	PKG=$1
	SPEC="$MPSSRC/$PKG/$(package_spec_file $PKG)"
	if [ -f "$MPSTMP/$PKG.deps" ]; then
		# we've already installed the build deps, but if the spec is newer, do reinstall
		SPEC_DATE=`stat -c "%Z" "$SPEC" || 0`
		DEPS_DATE=`stat -c "%Z" "$MPSTMP/$PKG.deps" || 0`
		buildenv_log $PKG "rechecking build deps: $SPEC_DATE >= $DEPS_DATE?"
		[ $SPEC_DATE -ge $DEPS_DATE ] && rm -f "$MPSTMP/$PKG.deps"
	fi
	if [ ! -f $MPSTMP/$PKG.deps ]; then
		buildenv_log_verbose "$PKG" "Installing $PKG build dependencies..."
		logged_exec $MPSTMP/$PKG.log yum-builddep -y $SPEC || exit 1
		touch $MPSTMP/$PKG.deps
	fi
}

# remove old RPM versions (if exists)
remove_old_builds() {
	PKG=$1
	REPO=$2

	# Get the package list from spec file and remove their RPMs
	package_rpm_files $PKG $REPO 1 | while read RPM; do
		buildenv_log $PKG "* removing old $RPM"
		rm -f "$RPM"
	done
}

# create built-finished marker
package_build_finished() {
	PKG=$1
	PKG_CURRENT_REV=$2
	REPO=$3
	PKG_TESTBUILD=$4
	PKG_TAG=$5

	MARKER="$(package_built_marker $PKG)"
	RPMLIST=${MARKER/.built/.rpms}

	if [ $PKG_TESTBUILD -eq 0 ] && [ "$PKG_TAG" != "" ]; then
		buildenv_log_verbose $PKG "Finished building from $PKG_TAG"
		echo "$PKG_TAG" > $MARKER
	else
		buildenv_log_verbose $PKG "Finished building from $PKG_CURRENT_REV"
		echo "$PKG_CURRENT_REV" > $MARKER
	fi

	rm -f $RPMLIST
	package_rpm_files $PKG $REPO 0 | while read RPM; do
		buildenv_log $PKG "* created new `basename $RPM`"
		basename $RPM >> $RPMLIST
	done
}


# returns list of RPMs which should be installed locally on the host
package_rpms_to_install() {
	PKG=$1
	REPO=$2

	MARKER="$(package_built_marker $PKG)"
	RPMLIST=${MARKER/.built/.rpms}
	# install everything except:
	# - debuginfo
	# - tests
	# - syslinux i686 packages
	for RPM in `egrep -v -- '-debuginfo-|-tests-|^syslinux-.*\.i686\.|^libftdi-c\+\+-' "$RPMLIST"`; do
		find $REPO -type f -name $RPM -print | grep .
		[ $? -ne 0 ] && buildenv_log_verbose $PKG "unable to install $RPM: not found in repo"
	done | sort | uniq
}

# install package RPMs from local repo
install_package_if_required() {
	PKG=$1
	REPO=$2
	SKIPPED=$3

	buildenv_log $PKG "checking if package needs to be (re)installed..."
	RPMS="$(package_rpms_to_install $PKG $REPO)"
	if [[ -n $RPMS ]]; then
		# check if we have anything to install
		FOUND_NOT_INSTALLED_PACKAGE=0
		for RPM in $RPMS; do
			PKG_NAME="`basename $RPM`"
			PKG_NAME="${PKG_NAME%%.rpm}"
			if [ "`rpm -q $PKG_NAME`" != "$PKG_NAME" ]; then
				buildenv_log $PKG "* $PKG_NAME not installed"
				FOUND_NOT_INSTALLED_PACKAGE=1
			else
				buildenv_log $PKG "* $PKG_NAME already installed, skipping"
			fi
		done
		if [ $FOUND_NOT_INSTALLED_PACKAGE -ne 0 ]; then
			if [ "$SKIPPED" = "1" ]; then
				buildenv_log $PKG "Build has been skipped, installing builddeps..."
				install_package_deps $PKG
			fi
			buildenv_log_verbose $PKG "Installing/replacing package $PKG locally..."
			logged_exec $MPSTMP/$PKG.log rpm -Uv --force --nodeps --noscripts --notriggers $RPMS
		fi
	else
		buildenv_log_verbose $PKG "No RPMs to install found" # something is wrong
	fi
}


# ensure all builddep packages are installed locally before making livecd/usb/pxe/rootfs images
install_image_build_deps() {
	DEPS_TO_INSTALL=""
	while read PKG PKG_OPTS; do
		[[ -z $PKG || $PKG = \#* ]] && continue
		if [[ $PKG_OPTS = *imagedep* ]]; then
			# find RPM file sharing the package name
			RPM=$(find $PATH_PACKAGE_REPO -type f -regextype posix-extended -regex ".*/${PKG}-[^-]+-[^-]+.(noarch|x86_64).rpm" -print | grep .)
			[ $? -ne 0 ] && buildenv_log_verbose "livecd" "no RPMs found for package $PKG"
			# check if it's already installed (do not install already installed packages to avoid stupid "nothing to do" error)
			PKG_NAME="`basename $RPM`"
			PKG_NAME="${PKG_NAME%%.rpm}"
			if [ "`rpm -q $PKG_NAME`" != "$PKG_NAME" ]; then
				DEPS_TO_INSTALL="${DEPS_TO_INSTALL} ${RPM}"
			fi
		fi
	done < $TOPDIR/config/package.list

	RET=0
	if [[ -n $DEPS_TO_INSTALL ]]; then
		cat >/etc/yum.repos.d/mps-builder-local.repo <<-EOF
			[mps-builder-local-packages]
			name=MPS Builder Local MPS Packages repo
			baseurl=file://$PATH_PACKAGE_REPO
			enabled=0
			gpgcheck=0
			exclude=syslinux-*
		EOF
		yum clean all
		yum --enablerepo="mps-builder-local-packages" install -y $DEPS_TO_INSTALL
		RET=$?
		rm /etc/yum.repos.d/mps-builder-local.repo
	fi
	return $RET
}

