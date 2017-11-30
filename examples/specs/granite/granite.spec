Name:           granite
Summary:        elementary Development Library
Version:        0.5
Release:        1%{?dist}
License:        LGPLv3+

URL:            https://github.com/elementary/%{name}
Source0:        https://github.com/elementary/%{name}/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  vala

BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0)

# granite provides and needs some generic icons
Requires:       hicolor-icon-theme


%description
An extension to GTK+ that provides several useful widgets and classes
to ease application development.


%package        devel
Summary:        Granite Toolkit development headers
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
An extension to GTK+ that provides several useful widgets and classes
to ease application development.

This package contains the development headers.


%prep
%autosetup


%build
mkdir build && pushd build
%cmake ..
%make_build
popd


%install
pushd build
%make_install
popd

%find_lang granite


%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/granite-demo.desktop


%post
/sbin/ldconfig
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -f granite.lang
%doc AUTHORS README.md
%license COPYING

%{_libdir}/libgranite.so.4
%{_libdir}/libgranite.so.4.0
%{_libdir}/girepository-1.0/Granite-1.0.typelib

%{_datadir}/icons/hicolor/*/actions/appointment.svg
%{_datadir}/icons/hicolor/*/actions/open-menu.svg
%{_datadir}/icons/hicolor/scalable/actions/open-menu-symbolic.svg


%files          devel
%{_bindir}/granite-demo

%{_libdir}/libgranite.so
%{_libdir}/pkgconfig/granite.pc

%{_includedir}/granite/

%{_datadir}/applications/granite-demo.desktop
%{_datadir}/gir-1.0/Granite-1.0.gir
%{_datadir}/vala/vapi/granite.deps
%{_datadir}/vala/vapi/granite.vapi


%changelog

