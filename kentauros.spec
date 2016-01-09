%if %{fedora} > 22
%define debug_package %{nil}
%endif

Summary:        Small build system, written in python
Name:           kentauros
Version:        0.0.4
Release:        1%{?dist}
License:        GPLv2
URL:            http://github.com/decathorpe/kentauros

Source0:        https://github.com/decathorpe/%{name}/archive/%{version}.tar.gz


BuildRequires:  python3-devel

Requires:       python3-kentauros


%description
kentauros is a small build system with little need for configuration.
create a directory named after the project, drop in a .conf and RPM .spec file,
configure copr-cli, and automagic updating, building, uploading to copr works.


%package     -n python3-kentauros
Summary:        Small build system, written in python

Requires:       bzr
Requires:       copr-cli
Requires:       git
Requires:       mock
Requires:	python3-configobj
Requires:       rpmdevtools
Requires:       wget

%description -n python3-kentauros
kentauros is a small build system with little need for configuration.
create a directory named after the project, drop in a .conf and RPM .spec file,
configure copr-cli, and automagic updating, building, uploading to copr works.

This package contains the python3 module only. For the main script, see ktr.


%prep
%setup -q -n %{name}-%{version}


%build
%py3_build


%install
%py3_install

mkdir -p %{buildroot}/%{_localstatedir}/lib/kentauros


%clean
rm -rf %{buildroot}


%files
%{_bindir}/ktr
%{_datadir}/kentauros/
%{_localstatedir}/lib/kentauros/

%files       -n python3-kentauros
%{python3_sitelib}/kentauros
%{python3_sitelib}/kentauros-%{version}-py%{python3_version}.egg-info/


%changelog
* Sat Jan 09 2016 Fabio Valentini <decathorpe@gmail.com> - 0.0.4-1
- Bump version to 0.0.4.

* Wed Dec 30 2015 Fabio Valentini <decathorpe@gmail.com> - 0.0.3-1
- Bump version to 0.0.3.

* Sun Dec 27 2015 Fabio Valentini <decathorpe@gmail.com> - 0.0.2-3
- Fix dep of main package on py3 package.

* Sat Dec 26 2015 Fabio Valentini <decathorpe@gmail.com> - 0.0.2-2
- Fix src.rpm package build with make-srpm.sh.

* Sat Dec 26 2015 Fabio Valentini <decathorpe@gmail.com> - 0.0.2-1
- Bump version for test release.

* Mon Oct 12 2015 Fabio Valentini <decathorpe@gmail.com> - 0.0.1-1
- Release 0.0.1.


