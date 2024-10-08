## START: Set by rpmautospec
## (rpmautospec version 0.6.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 1;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

# Polyfill %%bcond() macro for platforms without it
%if 0%{!?bcond:1}
%define bcond() %[ (%2)\
    ? "%{expand:%%{!?_without_%{1}:%%global with_%{1} 1}}"\
    : "%{expand:%%{?_with_%{1}:%%global with_%{1} 1}}"\
]
%endif

# The pytest-xdist package is not available when bootstrapping or for EL builds
%bcond xdist %{undefined rhel}

# Package the placeholder rpm-macros (moved to redhat-rpm-config in F40)
%if ! (0%{?fedora} >= 40 || 0%{?rhel} >= 10)
%bcond rpmmacropkg 1
%else
%bcond rpmmacropkg 0
%endif

%if ! 0%{?fedora}%{?rhel} || 0%{?fedora} || 0%{?epel} >= 9
%bcond poetry 1
# Appease old Poetry versions (<1.2.0a2)
%if ! 0%{?fedora}%{?rhel} || 0%{?fedora} >= 38 || 0%{?rhel} >= 10
%bcond old_poetry 0
%else
%bcond old_poetry 1
%endif
%else
%bcond poetry 0
%endif

%if ! 0%{?fedora}%{?rhel} || 0%{?fedora} || 0%{?epel} >= 9 || 0%{?rhel} >= 10
%bcond manpage_manual_title 1
%else
%bcond manpage_manual_title 0
%endif

%global srcname rpmautospec

Name: python-%{srcname}
Version: 0.6.5
Release: %autorelease
Summary: Package and CLI tool to generate release fields and changelogs
License: MIT
URL: https://github.com/fedora-infra/%{srcname}
Source0: https://github.com/fedora-infra/%{srcname}/releases/download/%{version}/%{srcname}-%{version}.tar.gz

%if 0%{!?pyproject_files:1}
%global pyproject_files %{_builddir}/%{name}-%{version}-%{release}.%{_arch}-pyproject-files
%endif

BuildArch: noarch
BuildRequires: argparse-manpage
BuildRequires: git
# the langpacks are needed for tests
BuildRequires: glibc-langpack-de
BuildRequires: glibc-langpack-en
BuildRequires: python3-devel >= 3.9.0
# The dependencies needed for testing don’t get auto-generated.
BuildRequires: python3dist(pytest)
%if %{with xdist}
BuildRequires: python3dist(pytest-xdist)
%endif
BuildRequires: python3dist(pyyaml)
BuildRequires: sed

%if %{without poetry}
BuildRequires: python3dist(babel)
BuildRequires: python3dist(pygit2)
BuildRequires: python3dist(rpm)
BuildRequires: python3dist(rpmautospec-core)
BuildRequires: python3dist(setuptools)
%{?python_provide:%python_provide python3-%{srcname}}
%endif

%global _description %{expand:
A package and CLI tool to generate RPM release fields and changelogs.}

%description %_description

%package -n python3-%{srcname}
Summary: %{summary}
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname} %_description

%package -n %{srcname}
Summary:  CLI tool for generating RPM releases and changelogs
Requires: python3-%{srcname} = %{version}-%{release}

%description -n %{srcname}
CLI tool for generating RPM releases and changelogs

%if %{with rpmmacropkg}
%package -n rpmautospec-rpm-macros
Summary: Rpmautospec RPM macros for local rpmbuild
Requires: rpm

%description -n rpmautospec-rpm-macros
This package contains RPM macros with placeholders for building rpmautospec
enabled packages locally.
%endif

%generate_buildrequires
%if %{with poetry}
%pyproject_buildrequires
%endif

%prep
%autosetup -n %{srcname}-%{version}
%if %{with old_poetry}
sed -i \
    -e 's/\[tool\.poetry\.group\.dev\.dependencies\]/[tool.poetry.dev-dependencies]/g' \
    pyproject.toml
%endif

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_linters
sed -i -e '/pytest-cov/d; /addopts.*--cov/d' pyproject.toml

%build
%if %{with poetry}
%pyproject_wheel
%else
%py3_build
%endif

%install
%if %{with poetry}
%pyproject_install
%pyproject_save_files %{srcname}
# Work around poetry not listing license files as such in package metadata.
sed -i -e 's|^\(.*/LICENSE\)|%%license \1|g' %{pyproject_files}
%else
%py3_install
cat << EOF > %{pyproject_files}
%{python3_sitelib}/%{srcname}/
%{python3_sitelib}/*.egg-info/
EOF
%endif

install -d %{buildroot}%{_mandir}/man1
PYTHONPATH=%{buildroot}%{python3_sitelib} argparse-manpage \
%if %{with manpage_manual_title}
    --manual-title "User Commands" \
%endif
    --project-name rpmautospec \
    --module rpmautospec.cli \
    --function get_arg_parser > %{buildroot}%{_mandir}/man1/rpmautospec.1

%if %{with rpmmacropkg}
mkdir -p %{buildroot}%{rpmmacrodir}
install -m 644  rpm/macros.d/macros.rpmautospec %{buildroot}%{rpmmacrodir}/
%endif

%check
%pytest -v \
%if %{with xdist}
--numprocesses=auto
%endif

%files -n python3-%{srcname} -f %{pyproject_files}
%doc README.rst

%files -n %{srcname}
%{_bindir}/rpmautospec
%{_mandir}/man1/rpmautospec.1*

%if %{with rpmmacropkg}
%files -n rpmautospec-rpm-macros
%{rpmmacrodir}/macros.rpmautospec
%endif

%changelog
## START: Generated by rpmautospec
* Tue Jun 18 2024 Nils Philippsen <nils@redhat.com> - 0.6.5-1
- Update to 0.6.5

* Tue Jun 11 2024 Python Maint <python-maint@redhat.com> - 0.6.4-2
- Rebuilt for Python 3.13

* Mon Jun 10 2024 Nils Philippsen <nils@redhat.com> - 0.6.4-1
- Update to 0.6.4
- Install man page

* Fri Jun 07 2024 Python Maint <python-maint@redhat.com> - 0.6.3-2
- Rebuilt for Python 3.13

* Wed Feb 21 2024 Nils Philippsen <nils@redhat.com> - 0.6.3-1
- Update to 0.6.3

* Mon Feb 19 2024 Nils Philippsen <nils@redhat.com> - 0.6.2-1
- Update to 0.6.2

* Fri Feb 09 2024 Nils Philippsen <nils@redhat.com> - 0.6.1-1
- Update to 0.6.1

* Sat Jan 27 2024 Nils Philippsen <nils@redhat.com> - 0.6.0-1
- Update to 0.6.0

* Fri Jan 26 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Mon Jan 22 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Tue Jan 16 2024 Nils Philippsen <nils@redhat.com> - 0.5.1-1
- Update to 0.5.1

* Mon Jan 15 2024 Nils Philippsen <nils@redhat.com> - 0.5.0-1
- Update to 0.5.0

* Thu Jan 11 2024 Nils Philippsen <nils@redhat.com> - 0.4.2-1
- Update to 0.4.2

* Mon Jan 08 2024 Nils Philippsen <nils@redhat.com> - 0.4.1-2
- Update patch for old poetry versions

* Fri Dec 15 2023 Nils Philippsen <nils@redhat.com> - 0.4.1-1
- Update to 0.4.1

* Sun Dec 03 2023 Yaakov Selkowitz <yselkowi@redhat.com> - 0.4.0-2
- Drop unwanted python-pytest-cov dependency

* Thu Nov 30 2023 Nils Philippsen <nils@redhat.com> - 0.4.0-1
- Update to 0.4.0

* Tue Nov 14 2023 Nils Philippsen <nils@redhat.com> - 0.3.8-1
- Update to 0.3.8

* Tue Nov 14 2023 Nils Philippsen <nils@redhat.com> - 0.3.7-1
- Update to 0.3.7

* Tue Nov 14 2023 Nils Philippsen <nils@redhat.com> - 0.3.6-1
- Update to 0.3.6

* Tue Aug 22 2023 Yaakov Selkowitz <yselkowi@redhat.com> - 0.3.5-5
- Disable the macros subpackage in F40+

* Fri Jul 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 0.3.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Wed Jun 14 2023 Python Maint <python-maint@redhat.com> - 0.3.5-3
- Rebuilt for Python 3.12

* Wed May 24 2023 Yaakov Selkowitz <yselkowi@redhat.com> - 0.3.5-2
- Avoid pytest-cov, disable xdist in RHEL builds

* Wed Feb 08 2023 Nils Philippsen <nils@redhat.com> - 0.3.5-1
- Update to 0.3.5

* Wed Feb 08 2023 Nils Philippsen <nils@redhat.com> - 0.3.4-1
- Update to 0.3.4

* Wed Feb 08 2023 Nils Philippsen <nils@redhat.com> - 0.3.3-1
- Update to 0.3.3

* Tue Jan 24 2023 Nils Philippsen <nils@redhat.com> - 0.3.2-1
- Update to 0.3.2

* Fri Jan 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 0.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Fri Nov 11 2022 Nils Philippsen <nils@redhat.com> - 0.3.1-1
- Update to 0.3.1

* Wed Jul 27 2022 Nils Philippsen <nils@redhat.com> - 0.3.0-1
- Update to 0.3.0

* Wed Jun 08 2022 Nils Philippsen <nils@redhat.com>
- Generally BR: python3-pytest-xdist, also on EL9

* Mon May 16 2022 Nils Philippsen <nils@redhat.com> - 0.2.8-1
- Update to 0.2.8
- Don't require python3-pytest-xdist for building on EL9

* Mon May 16 2022 Nils Philippsen <nils@redhat.com> - 0.2.7-1
- Update to 0.2.7

* Mon Apr 25 2022 Nils Philippsen <nils@redhat.com> - 0.2.6-1
- Update to 0.2.6
- Require python3-pytest-xdist for building
- Remove EL7 quirks, pkg isn't built there

* Fri Mar 04 2022 Nils Philippsen <nils@redhat.com>
- require python3-pyyaml for building

* Sun Nov 07 2021 Nils Philippsen <nils@redhat.com>
- require python3-babel and glibc langpacks (the latter for testing)

* Fri Aug 06 2021 Nils Philippsen <nils@redhat.com> - 0.2.5-1
- Update to 0.2.5

* Thu Aug 05 2021 Nils Philippsen <nils@redhat.com> - 0.2.4-1
- Update to 0.2.4

* Wed Jun 16 2021 Nils Philippsen <nils@redhat.com> - 0.2.3-1
- Update to 0.2.3

* Fri Jun 04 2021 Nils Philippsen <nils@redhat.com> - 0.2.2-1
- Update to 0.2.2

* Thu May 27 2021 Nils Philippsen <nils@redhat.com> - 0.2.1-1
- Update to 0.2.1

* Thu May 27 2021 Stephen Coady <scoady@redhat.com> - 0.2.0-1
- Update to 0.2.0

* Thu May 27 2021 Nils Philippsen <nils@redhat.com>
- don't ship obsolete Koji configuration snippet

* Wed May 19 2021 Nils Philippsen <nils@redhat.com>
- remove git-core, fix RPM related dependencies

* Wed May 12 2021 Nils Philippsen <nils@redhat.com>
- depend on python3-pygit2

* Thu Apr 22 2021 Nils Philippsen <nils@redhat.com>
- remove the hub plugin

* Thu Apr 15 2021 Nils Philippsen <nils@redhat.com> - 0.1.5-1
- Update to 0.1.5
- Have lowercase URLs, because Pagure d'oh

* Thu Apr 15 2021 Nils Philippsen <nils@redhat.com> - 0.1.4-1
- Update to 0.1.4
- explicitly BR: python3-setuptools

* Thu Apr 09 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.3-1
- Update to 0.1.3

* Thu Apr 09 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.2-1
- Update to 0.1.2

* Thu Apr 09 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.1-1
- Update to 0.1.1

* Thu Apr 09 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.0-1
- Update to 0.1.0

* Wed Apr 08 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.23-1
- Update to 0.023

* Wed Apr 08 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.22-1
- Update to 0.0.22

* Wed Apr 08 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.21-1
- Update to 0.0.21

* Wed Apr 08 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.20-1
- Update to 0.0.20

* Wed Apr 08 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.19-1
- Update to 0.0.19

* Wed Apr 08 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.18-1
- Update to 0.0.18

* Tue Apr 07 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.17-1
- Update to 0.0.17

* Tue Apr 07 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.16-1
- Update to 0.0.16

* Tue Apr 07 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.15-1
- Update to 0.0.15

* Tue Apr 07 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.14-1
- Update to 0.0.14

* Tue Apr 07 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.13-1
- Update to 0.0.13

* Tue Apr 07 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.12-1
- Update to 0.0.12

* Mon Apr 06 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.11-1
- Update to 0.0.11

* Fri Apr 03 2020 Nils Philippsen <nils@redhat.com> - 0.0.10-1
- Update to 0.0.10

* Fri Apr 03 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.9-1
- Update to 0.0.9

* Fri Apr 03 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.8-1
- Update to 0.0.8

* Fri Apr 03 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.7-1
- Update to 0.0.7

* Thu Apr 02 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.6-1
- Update to 0.0.6

* Tue Mar 31 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.5-1
- Update to 0.0.5

* Tue Mar 31 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.4-1
- Update to 0.0.4

* Tue Mar 31 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.3-1
- Update to 0.0.3

* Tue Mar 31 2020 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.2-1
- Update to 0.0.2

* Wed Mar 18 2020  Adam Saleh <asaleh@redhat.com> - 0.0.1-1
- initial package for Fedora

## END: Generated by rpmautospec
