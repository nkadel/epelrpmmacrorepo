Name:           epel-rpm-macros
Version:        10
#Release:        14%%{dist}
Release:        0.14%{dist}
Summary:        Extra Packages for Enterprise Linux RPM macros

License:        GPLv2

# This is a EPEL maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.
URL:            https://download.fedoraproject.org/pub/epel
Source0:        macros.epel-rpm-macros
Source1:        macros.zzz-epel-override
Source2:        GPL
#Add source for misc macros below here
# https://src.fedoraproject.org/rpms/redhat-rpm-config/blob/rawhide/f/macros.shell-completions
Source3:        macros.shell-completions


BuildArch:      noarch
Requires:       redhat-release >= %{version}
# For FPC buildroot macros
Requires:       fpc-srpm-macros
# pyproject-rpm-macros in CRB thus not required by python3-devel or python3-rpm-macros
#   https://bugzilla.redhat.com/show_bug.cgi?id=2001034
Requires:       (pyproject-rpm-macros if python3-rpm-macros)
Requires:       ansible-srpm-macros
# Backwards-compatible backport of the new forge-srpm-macros from Fedora that
# avoids conflicts with EL 10's old version
Requires:       forge-srpm-macros
# Provides backports from Fedora's go-rpm-macros and fixes critical
# bugs in RHEL's go-rpm-macros.
# Just like in Fedora, only the minimal -srpm-macros are needed in the buildroot.
# The rest of the macros are pulled in dynamically.
Requires:       go-srpm-macros-epel
# Provides backports from Fedora's rust-srpm-macros
Requires:       rust-srpm-macros-epel
# Provides backport from Fedora's perl-generators related to proposal
# https://fedoraproject.org/wiki/Changes/Perl_replace_MODULE_COMPAT_by_generator
Requires:       (perl-generators-epel if perl-generators)
# Add rpmautospec to the buildroot to mirror Fedora
Requires:       rpmautospec-rpm-macros
Requires:       qt6-srpm-macros

%description
This package contains the Extra Packages for Enterprise Linux (EPEL) RPM
macros for building EPEL packages.

%prep
%setup -cT
install -pm 644 %{SOURCE2} .

%install
#epel rpm macros
install -Dpm 644 %{SOURCE0} \
    %{buildroot}%{_rpmmacrodir}/macros.epel-rpm-macros

install -Dpm 644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/rpm/macros.zzz-epel-override

#Add misc macros below here
install -Dpm 644 %{SOURCE3} \
    %{buildroot}%{_rpmmacrodir}/macros.shell-completions

%files
%license GPL
%{_rpmmacrodir}/macros.epel-rpm-macros
%{_sysconfdir}/rpm/macros.zzz-epel-override
%{_rpmmacrodir}/macros.shell-completions


%changelog
* Fri Jul 19 2024 Nico Kadel-Garcia - 10-0.1
- Initialize from RHEL 9 version


