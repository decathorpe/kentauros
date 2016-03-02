%if %{fedora} > 22
%define debug_package %{nil}
%endif

Summary:        Small build system, written in python
Name:           kentauros
Version:        0.9.1
Release:        1%{?dist}
License:        GPLv2
URL:            http://github.com/decathorpe/kentauros

Source0:        https://github.com/decathorpe/%{name}/archive/%{version}.tar.gz


BuildRequires:  python3-devel

Requires:       bzr, git, wget
Requires:       python3-dateutil
Requires:       rpmdevtools

Suggests:       copr-cli
Suggests:       mock


%description
kentauros is a small build system with little need for configuration.
create a directory named after the project, drop in a .conf and RPM .spec file,
configure copr-cli, and automagic updating, building, uploading to copr works.


%prep
%setup -q -n %{name}-%{version}


%build
%py3_build


%install
%py3_install


%clean
rm -rf %{buildroot}


%files
%{_bindir}/ktr
%{_datadir}/kentauros/

%{python3_sitelib}/kentauros
%{python3_sitelib}/kentauros-%{version}-py%{python3_version}.egg-info/


%changelog
* Wed Mar 02 2016 Fabio Valentini <decathorpe@gmail.com> - 0.9.1-1
- Bump to version 0.9.1.

* Wed Mar 02 2016 Fabio Valentini <decathorpe@gmail.com> - 0.9.0-2
- move copr-cli and mock from Requires: to Suggests:
- copr-cli and mock command presence is checked at runtime

* Sun Feb 28 2016 Fabio Valentini <decathorpe@gmail.com> - 0.9.0-1
- Bump to version 0.9.0.

* Wed Feb 24 2016 Fabio Valentini <decathorpe@gmail.com> - 0.1.0-1
- Bump to version 0.1.0.

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


