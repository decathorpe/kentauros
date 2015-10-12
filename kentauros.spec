%if %{fedora} > 22
%define debug_package %{nil}
%endif

Summary: small build system, written in python
Name: kentauros
Version: 0.0.1
Release: 1%{?dist}
License: GPLv2
URL: http://github.com/decathorpe/kentauros

Source0: %{name}-%{version}.tar.gz

BuildRequires: python3-devel

Requires: python3
Requires: rpmdevtools
Requires: copr-cli
Requires: bzr
Requires: git
Requires: wget


%description
kentauros is a small build system with little need for configuration.
create a directory named after the project, drop in a .conf and RPM .spec file,
configure copr-cli, and automagic updating, building, uploading to copr works.


%prep
%autosetup


%build
%py3_build


%install
%py3_install


%clean
rm -rf $RPM_BUILD_ROOT


%post
%postun


%files
%{_bindir}/kentauros
%{python3_sitelib}/kentauros
%{python3_sitelib}/kentauros-%{version}-py3.4.egg-info


%changelog
* Mon Oct 12 2015 Fabio Valentini <decathorpe@gmail.com> - 0.0.1-1
- Release 0.0.1.


