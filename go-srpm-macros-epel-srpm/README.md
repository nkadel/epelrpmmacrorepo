# go-rpm-macros-epel

The go-rpm-macros-epel contains backported Go RPM macros and generators from
Fedora. It also contains hotfixes for critical bugs in RHEL 9's go-rpm-macros
that were never addressed. The goal is for EPEL Go packaging to work as
similarly as possible to Fedora Go packaging. At the same time, this package
avoids overriding macros from RHEL more than it has to.

This package contains the following backports:

## go-rpm-macros-epel
go-rpm-macros-epel contains backports of certain Go RPM macros from Fedora.

- Redefine %goinstallflags to work around [rhbz#2098400](https://bugzilla.redhat.com/show_bug.cgi?id=2098400).
- Redefine `%gobuild` and `%gotest` with `GO111MODULE=off` set to work around [RHEL-19720](https://issues.redhat.com/browse/RHEL-19720)

## go-srpm-macros-epel

go-srpm-macros-epel contains backports of certain Go SRPM macros from Fedora.

- Change `%gometa` to pull in go-rpm-macros-epel.
  This way, packages don't need to BuildRequire it manually.
- Backport `-L` flag to `%gometa` and `%gorpmname` to support the new naming
  scheme for compat packages.

## go-rpm-macros-golist-symlink

go-rpm-macros-golist-symlink provides a symlink from /usr/bin to
go-rpm-macros's bundled golist, which is installed in
/usr/libexec/go-rpm-macros. This allows the macros that expect to find golist
in $PATH to work properly.

This package is split out and namespaced to allow the upstream golist to be
packaged as golist.

This works around [rhbz#2100618](https://bugzilla.redhat.com/show_bug.cgi?id=2100618).
