%global pkg desktop-file-utils
%global pkgname desktop-file-utils

Summary: Utilities for manipulating .desktop files
Name: desktop-file-utils
Version: 0
Release: 0%{?dist}
URL: https://www.freedesktop.org/software/desktop-file-utils
Source0: https://www.freedesktop.org/software/desktop-file-utils/releases/%{name}-%{version}.tar.xz
Source1: desktop-entry-mode-init.el
License: GPLv2+
Group: Development/Tools

BuildRequires: glib2-devel
BuildRequires: emacs
Requires: emacs-filesystem
Provides: emacs-%{pkg} = %{version}-%{release}
Provides: emacs-%{pkg}-el = %{version}-%{release}
Obsoletes: emacs-%{pkg} < 0.20-3
Obsoletes: emacs-%{pkg}-el < 0.20-3

%description
.desktop files are used to describe an application for inclusion in
GNOME or KDE menus.  This package contains desktop-file-validate which
checks whether a .desktop file complies with the specification at
http://www.freedesktop.org/standards/, and desktop-file-install
which installs a desktop file to the standard directory, optionally
fixing it up in the process.


%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"

mkdir -p $RPM_BUILD_ROOT%{_emacs_sitelispdir}/%{pkg}
mv $RPM_BUILD_ROOT%{_emacs_sitelispdir}/*.el* $RPM_BUILD_ROOT%{_emacs_sitelispdir}/%{pkg}
install -Dpm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_emacs_sitestartdir}/desktop-entry-mode-init.el
touch $RPM_BUILD_ROOT%{_emacs_sitestartdir}/desktop-entry-mode-init.elc

%transfiletriggerin -- %{_datadir}/applications
update-desktop-database

%transfiletriggerpostun -- %{_datadir}/applications
update-desktop-database

%files
%doc AUTHORS COPYING README NEWS
%{_bindir}/*
%{_mandir}/man1/desktop-file-install.1.gz
%{_mandir}/man1/desktop-file-validate.1.gz
%{_mandir}/man1/update-desktop-database.1.gz
%{_mandir}/man1/desktop-file-edit.1.gz
%{_emacs_sitestartdir}/desktop-entry-mode-init.el
%ghost %{_emacs_sitestartdir}/desktop-entry-mode-init.elc
%{_emacs_sitelispdir}/%{pkg}

%changelog

