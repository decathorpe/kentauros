# if git: %%define date YYMMDD
# if git: %%define rev xxx
# if bzr: %%define revno xxx

Summary:        Summary
Name:           YOUR_PACKAGE_NAME
# Version:        $VERSION if building from release tarball
# Version:        $VERSION~git%{date}~%{rev} if building from git master
# Version:        $VERSION~rev%{revno} if building from bzr master
Release:        0%{?dist}
License:
URL:            http://www.example.com

# .tar.gz is the kentauros default. tar.xz is also supported.
Source0: %{name}-%{version}.tar.gz
Source1: %{name}.conf

# Patch0:

# BuildRequires: desktop-file-utils
# BuildRequires: libappstream-util

# Requires:


%description


%prep
%autosetup


%build
# %%cmake
# or
# %%configure

%make_build


%install
%make_install
# %%find_lang %%{name}


%clean
rm -rf %{buildroot}


%check
# desktop-file-validate $RPM_BUILD_ROOT/%{_datadir}/applications/*.desktop
# appstream-util validate-relax --nonet $RPM_BUILD_ROOT/%{_datadir}/appdata/*.appdata.xml


%files


%changelog

