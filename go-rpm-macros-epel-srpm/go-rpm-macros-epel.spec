# This specfile is licensed under:
# SPDX-License-Identifier: MIT
# License text: https://spdx.org/licenses/MIT.html
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-FileCopyrightText: Fedora Project Authors

%global forgeurl https://pagure.io/go-rpm-macros

Name:           go-rpm-macros-epel
Version:        3.3.0.5
%global tag epel10-%{version}
%global distprefix %{nil}
%forgemeta
#Release:        1%%{?dist}
Release:        0.1%{?dist}
Summary:        Backport of certain Fedora Go RPM macros to EPEL

License:        GPL-3.0-or-later
URL:            %{forgeurl}
#Source0:        %%{forgesource}
Source0:        https://pagure.io/go-rpm-macros/archive/epel10-3.3.0.5/go-rpm-macros-epel9-3.3.0.5.tar.gz
# Downstream README
Source1:        README.md
# golist-symlink subpackage license
Source2:        https://github.com/spdx/license-list-data/raw/master/text/Unlicense.txt

# Require RHEL's macros. We read macros from go-srpm-macros in the specfile.
BuildRequires:  go-srpm-macros
BuildRequires:  go-rpm-macros
Requires:       go-rpm-macros

Requires:       go-srpm-macros-epel = %{version}-%{release}
Requires:       go-rpm-macros-golist-symlink = %{version}-%{release}

%description
go-rpm-macros-epel contains backports of certain Go RPM macros from Fedora.


%package -n     go-srpm-macros-epel
Summary:        Backport of certain Go SRPM macros from Fedora
BuildArch:      noarch
# Explicitly Require go-srpm-macros from RHEL even though they are already part
# of the buildroot. We import its Lua.
Requires:       go-srpm-macros
# Pull in go-rpm-macros-epel if go-rpm-macros is installed.
Requires:       (go-rpm-macros-epel if go-rpm-macros)

%description -n go-srpm-macros-epel
go-srpm-macros-epel contains backports of certain Go SRPM macros from Fedora.


%package -n     go-rpm-macros-golist-symlink
Summary:        Provides symlink to the bundled golist in go-rpm-macros
# The package just provides a symlink.
License:        Unlicense
# Conflict with standard golist in case that gets packaged.
Conflicts:      golist
Requires:       go-rpm-macros

%description    -n go-rpm-macros-golist-symlink
go-rpm-macros-golist-symlink provides a symlink from /usr/bin to
go-rpm-macros's bundled golist, which is installed in
/usr/libexec/go-rpm-macros. This allows the macros that expect to find golist
in $PATH to work properly.

This package is split out and namespaced to allow the upstream golist to be
packaged as golist.


%prep
%autosetup -p1 %{forgesetupargs}
mv README.md README.upstream.md
cp %{S:1} %{S:2} .
%writevars -f rpm/macros.d/macros.zzz-go-srpm-macros-epel golang_arches golang_arches_future gccgo_arches gopath


%install
# Install macros and lua
install -Dpm 0644 rpm/macros.d/macros.* -t %{buildroot}%{_rpmmacrodir}
install -Dpm 0644 rpm/lua/rpm/*.lua -t %{buildroot}%{_rpmluadir}/fedora/rpm
install -Dpm 0644 rpm/lua/srpm/*.lua -t %{buildroot}%{_rpmluadir}/fedora/srpm


# Create symlink for golist-symlink subpackage
mkdir %{buildroot}%{_bindir}
ln -s %{_libexecdir}/go-rpm-macros/golist %{buildroot}%{_bindir}/golist

# Install REAMDE and licenses to a single directory for both subpackages.
install -Dpm 0644 README.md README.upstream.md \
    -t %{buildroot}%{_docdir}/go-rpm-macros-epel
install -Dpm 0644 LICENSE.txt \
    -t %{buildroot}%{_defaultlicensedir}/go-rpm-macros-epel

%ifarch %{go_arches}
%files
%{_rpmmacrodir}/macros.zzz-go-compilers-golang
%{_rpmmacrodir}/macros.zzz-go-rpm-macros-epel
%{_rpmluadir}/fedora/rpm/go_epel.lua
%endif

%files -n       go-srpm-macros-epel
%license %{_defaultlicensedir}/go-rpm-macros-epel
%doc %{_docdir}/go-rpm-macros-epel
%{_rpmmacrodir}/macros.zzz-go-srpm-macros-epel
%{_rpmluadir}/fedora/srpm/go_epel.lua

%files -n       go-rpm-macros-golist-symlink
%doc README.md
%license Unlicense.txt
%{_bindir}/golist


%changelog
* Sat Mar 09 2024 Maxwell G <maxwell@gtmx.me> - 3.3.0.5-1
- Update to 3.3.0.5.

* Mon Dec 18 2023 Maxwell G <maxwell@gtmx.me> - 3.3.0.4-1
- Update to 3.3.0.4.

* Sat Nov 04 2023 Maxwell G <maxwell@gtmx.me> - 3.3.0.2-1
- Update to 3.3.0.2.

* Sun Oct 29 2023 Maxwell G <maxwell@gtmx.me> - 3.3.0-1
- Update to new source git source
- Remove go_mod_vendor.prov from this package. It's already upstream.
- Add -L flag to %%gometa and %%gorpmname
- Add direct dependency on go-rpm-macros-golist-symlink

* Thu Sep 08 2022 Maxwell G <gotmax@e.email> - 1-8
- go-srpm-macros: Explicitly Require go-srpm-macros from RHEL

* Thu Sep 08 2022 Maxwell G <gotmax@e.email> - 1-7
- Install docs into the correct directory

* Wed Sep 07 2022 Maxwell G <gotmax@e.email> - 1-6
- Move go_mod_vendor generator from -srpm-macros to -rpm-macros subpackage

* Sat Sep 03 2022 Maxwell G <gotmax@e.email> - 1-5
- Fix %%goinstall flags definition
- go-srpm-macros-epel: Pull in go-rpm-macros-epel if go-rpm-macros is installed.

* Wed Aug 31 2022 Maxwell G <gotmax@e.email> - 1-4
- Redfine %%goinstallflags
  Relates: rhbz#2098400
- Add support for `%%golang_arches_future` and `%%gometa -f`.
  Relates: rhbz#2121796
- Add go-rpm-macros-golist-symlink
  Relates: rhbz#2100618
