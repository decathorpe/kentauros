%bcond_without wayland

# S390 doesn't have video cards, but we need swrast for xserver's GLX
# llvm (and thus llvmpipe) doesn't actually work on ppc32
%ifnarch s390 ppc
%define with_llvm 1
%endif

%if 0%{?with_llvm}
%define with_radeonsi 1
%endif

%ifarch s390 s390x ppc
%define with_hardware 0
%define base_drivers swrast
%else
%define with_hardware 1
%define with_vdpau 1
%define with_vaapi 1
%define with_nine 1
%define base_drivers swrast,nouveau,radeon,r200
%endif
%ifarch %{ix86} x86_64
%define platform_drivers ,i915,i965
%define with_ilo    1
%define with_vmware 1
%define with_xa     1
%define with_omx    1
%endif
%ifarch aarch64 %{ix86} x86_64
%define with_opencl 1
%endif
%ifarch %{arm} aarch64
%define with_vc4       1
%define with_freedreno 1
%define with_xa        1
%define with_omx       1
%endif

%define dri_drivers --with-dri-drivers=%{?base_drivers}%{?platform_drivers}

%global sanitize 1

#global rctag rc4

Name:           mesa
Summary:        Mesa graphics libraries
Version:        
Release:        0%{?dist}

License:        MIT
URL:            http://www.mesa3d.org
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool

%if %{with_hardware}
BuildRequires:  kernel-headers
%endif
BuildRequires:  libdrm-devel >= 2.4.42
BuildRequires:  libXxf86vm-devel
BuildRequires:  expat-devel
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  makedepend
BuildRequires:  libselinux-devel
BuildRequires:  libXext-devel
BuildRequires:  libXfixes-devel
BuildRequires:  libXdamage-devel
BuildRequires:  libXi-devel
BuildRequires:  libXmu-devel
BuildRequires:  libxshmfence-devel
BuildRequires:  elfutils
BuildRequires:  python
BuildRequires:  gettext
%if 0%{?with_llvm}
BuildRequires: llvm-devel >= 3.4-7
%if 0%{?with_opencl}
BuildRequires: clang-devel >= 3.0
%endif
%endif
BuildRequires: elfutils-libelf-devel
BuildRequires: libxml2-python
BuildRequires: libudev-devel
BuildRequires: bison flex
%if %{with wayland}
BuildRequires: pkgconfig(wayland-client)
BuildRequires: pkgconfig(wayland-server)
%endif
%if 0%{?with_vdpau}
BuildRequires: libvdpau-devel
%endif
%if 0%{?with_vaapi}
BuildRequires: libva-devel
%endif
BuildRequires: zlib-devel
%if 0%{?with_omx}
BuildRequires: libomxil-bellagio-devel
%endif
%if 0%{?with_opencl}
BuildRequires: libclc-devel opencl-filesystem
%endif
BuildRequires: python-mako
BuildRequires: libstdc++-static

%description
%{summary}.

%package filesystem
Summary:        Mesa driver filesystem
Provides:       mesa-dri-filesystem = %{?epoch:%{epoch}}%{version}-%{release}
Obsoletes:      mesa-dri-filesystem < %{?epoch:%{epoch}}%{version}-%{release}

%description filesystem
%{summary}.

%package libGL
Summary:        Mesa libGL runtime libraries
Requires:       %{name}-libglapi%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libGL
Provides:       libGL%{?_isa}

%description libGL
%{summary}.

%package libGL-devel
Summary:        Mesa libGL development package
Requires:       %{name}-libGL%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libGL-devel
Provides:       libGL-devel%{?_isa}

%description libGL-devel
%{summary}.

%package libEGL
Summary:        Mesa libEGL runtime libraries
Provides:       libEGL
Provides:       libEGL%{?_isa}

%description libEGL
%{summary}.

%package libEGL-devel
Summary:        Mesa libEGL development package
Requires:       %{name}-libEGL%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libEGL-devel
Provides:       libEGL-devel%{?_isa}

%description libEGL-devel
%{summary}.

%package libGLES
Summary:        Mesa libGLES runtime libraries
Requires:       %{name}-libglapi%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libGLES
Provides:       libGLES%{?_isa}

%description libGLES
%{summary}.

%package libGLES-devel
Summary:        Mesa libGLES development package
Requires:       %{name}-libGLES%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libGLES-devel
Provides:       libGLES-devel%{?_isa}

%description libGLES-devel
%{summary}.

%package dri-drivers
Summary:        Mesa-based DRI drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}

%description dri-drivers
%{summary}.

%if 0%{?with_omx}
%package omx-drivers
Summary:        Mesa-based OMX drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}

%description omx-drivers
%{summary}.
%endif

%if 0%{?with_vdpau}
%package        vdpau-drivers
Summary:        Mesa-based VDPAU drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}

%description vdpau-drivers
%{summary}.
%endif

%package libOSMesa
Summary:        Mesa offscreen rendering libraries
Requires:       %{name}-libglapi%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libOSMesa
Provides:       libOSMesa%{?_isa}

%description libOSMesa
%{summary}.

%package libOSMesa-devel
Summary:        Mesa offscreen rendering development package
Requires:       %{name}-libOSMesa%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}

%description libOSMesa-devel
%{summary}.

%package libgbm
Summary:        Mesa gbm runtime library
Provides:       libgbm
Provides:       libgbm%{?_isa}

%description libgbm
%{summary}.

%package libgbm-devel
Summary:        Mesa libgbm development package
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Provides:       libgbm-devel
Provides:       libgbm-devel%{?_isa}

%description libgbm-devel
%{summary}.

%if %{with wayland}
%package libwayland-egl
Summary:        Mesa libwayland-egl runtime library
Provides:       libwayland-egl
Provides:       libwayland-egl%{?_isa}

%description libwayland-egl
%{summary}.

%package libwayland-egl-devel
Summary:        Mesa libwayland-egl development package
Requires:       %{name}-libwayland-egl%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libwayland-egl-devel
Provides:       libwayland-egl-devel%{?_isa}

%description libwayland-egl-devel
%{summary}.
%endif

%if 0%{?with_xa}
%package libxatracker
Summary:        Mesa XA state tracker
Provides:       libxatracker
Provides:       libxatracker%{?_isa}

%description libxatracker
%{summary}.

%package libxatracker-devel
Summary:        Mesa XA state tracker development package
Requires:       %{name}-libxatracker%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libxatracker-devel
Provides:       libxatracker-devel%{?_isa}

%description libxatracker-devel
%{summary}.
%endif

%package libglapi
Summary:        Mesa shared glapi
Provides:       libglapi
Provides:       libglapi%{?_isa}

%description libglapi
%{summary}.

%if 0%{?with_opencl}
%package libOpenCL
Summary:        Mesa OpenCL runtime library
Requires:       ocl-icd%{?_isa}
Requires:       libclc%{?_isa}
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}
Requires:       opencl-filesystem

%description libOpenCL
%{summary}.

%package libOpenCL-devel
Summary:        Mesa OpenCL development package
Requires:       %{name}-libOpenCL%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}

%description libOpenCL-devel
%{summary}.
%endif

%if 0%{?with_nine}
%package libd3d
Summary:        Mesa Direct3D9 state tracker

%description libd3d
%{summary}.

%package libd3d-devel
Summary:        Mesa Direct3D9 state tracker development package
Requires:       %{name}-libd3d%{?_isa} = %{?epoch:%{epoch}}%{version}-%{release}

%description libd3d-devel
%{summary}.
%endif

%prep
%autosetup


%build
autoreconf -vfi

# C++ note: we never say "catch" in the source.  we do say "typeid" once,
# in an assert, which is patched out above.  LLVM doesn't use RTTI or throw.
#
# We do say 'catch' in the clover and d3d1x state trackers, but we're not
# building those yet.
export CXXFLAGS="%{?with_opencl:-frtti -fexceptions} %{!?with_opencl:-fno-rtti -fno-exceptions}"
export LDFLAGS="-static-libstdc++"
%ifarch %{ix86}
# i do not have words for how much the assembly dispatch code infuriates me
%global asm_flags --disable-asm
%endif

%configure \
    %{?asm_flags} \
    --enable-selinux \
    --enable-gallium-osmesa \
    --with-dri-driverdir=%{_libdir}/dri \
    --enable-egl \
    --disable-gles1 \
    --enable-gles2 \
    --disable-xvmc \
    %{?with_vdpau:--enable-vdpau} \
    %{?with_vaapi:--enable-va} \
    --with-egl-platforms=x11,drm,surfaceless%{?with_wayland:,wayland} \
    --enable-shared-glapi \
    --enable-gbm \
    %{?with_omx:--enable-omx} \
    %{?with_opencl:--enable-opencl --enable-opencl-icd} %{!?with_opencl:--disable-opencl} \
    --enable-glx-tls \
    --enable-texture-float=yes \
    %{?with_llvm:--enable-gallium-llvm} \
    %{?with_llvm:--enable-llvm-shared-libs} \
    --enable-dri \
%if %{with_hardware}
    %{?with_xa:--enable-xa} \
    %{?with_nine:--enable-nine} \
    --with-gallium-drivers=%{?with_vmware:svga,}%{?with_radeonsi:radeonsi,}%{?with_llvm:swrast,r600,}%{?with_freedreno:freedreno,}%{?with_vc4:vc4,}%{?with_ilo:ilo,}virgl,r300,nouveau \
%else
    --with-gallium-drivers=%{?with_llvm:swrast,}virgl \
%endif
    %{?dri_drivers}

# libtool refuses to pass through things you ask for in LDFLAGS that it doesn't
# know about, like -static-libstdc++, so...
sed -i 's/-fuse-linker-plugin|/-static-lib*|&/' libtool
sed -i 's/-nostdlib//g' libtool
sed -i 's/^predep_objects=.*$/#&/' libtool
sed -i 's/^postdep_objects=.*$/#&/' libtool
sed -i 's/^postdeps=.*$/#&/' libtool
%make_build MKDEP=/bin/true V=1

%install
%make_install

%if !%{with_hardware}
rm -f %{buildroot}%{_sysconfdir}/drirc
%endif

# libvdpau opens the versioned name, don't bother including the unversioned
rm -f %{buildroot}%{_libdir}/vdpau/*.so

# strip out useless headers
rm -f %{buildroot}%{_includedir}/GL/w*.h

# remove .la files
find %{buildroot} -name '*.la' -delete

# this keeps breaking, check it early.  note that the exit from eu-ftr is odd.
pushd %{buildroot}%{_libdir}
for i in libOSMesa*.so libGL.so ; do
    eu-findtextrel $i && exit 1
done
# check that we really didn't link libstdc++ dynamically
eu-readelf -d mesa_dri_drivers.so | grep -q libstdc && exit 1
popd

%files filesystem
%dir %{_libdir}/dri
%if %{with_hardware}
%if 0%{?with_vdpau}
%dir %{_libdir}/vdpau
%endif
%endif

%post libGL -p /sbin/ldconfig
%postun libGL -p /sbin/ldconfig
%files libGL
%{_libdir}/libGL.so.1
%{_libdir}/libGL.so.1.*
%files libGL-devel
%{_includedir}/GL/gl.h
%{_includedir}/GL/gl_mangle.h
%{_includedir}/GL/glext.h
%{_includedir}/GL/glx.h
%{_includedir}/GL/glx_mangle.h
%{_includedir}/GL/glxext.h
%{_includedir}/GL/glcorearb.h
%{_includedir}/GL/mesa_glinterop.h
%dir %{_includedir}/GL/internal
%{_includedir}/GL/internal/dri_interface.h
%{_libdir}/pkgconfig/dri.pc
%{_libdir}/libGL.so
%{_libdir}/libglapi.so
%{_libdir}/pkgconfig/gl.pc

%post libEGL -p /sbin/ldconfig
%postun libEGL -p /sbin/ldconfig
%files libEGL
%{_libdir}/libEGL.so.1
%{_libdir}/libEGL.so.1.*
%files libEGL-devel
%dir %{_includedir}/EGL
%{_includedir}/EGL/eglext.h
%{_includedir}/EGL/egl.h
%{_includedir}/EGL/eglmesaext.h
%{_includedir}/EGL/eglplatform.h
%{_includedir}/EGL/eglextchromium.h
%dir %{_includedir}/KHR
%{_includedir}/KHR/khrplatform.h
%{_libdir}/pkgconfig/egl.pc
%{_libdir}/libEGL.so

%post libGLES -p /sbin/ldconfig
%postun libGLES -p /sbin/ldconfig
%files libGLES
%{_libdir}/libGLESv2.so.2
%{_libdir}/libGLESv2.so.2.*
%files libGLES-devel
%dir %{_includedir}/GLES2
%{_includedir}/GLES2/gl2platform.h
%{_includedir}/GLES2/gl2.h
%{_includedir}/GLES2/gl2ext.h
%dir %{_includedir}/GLES3
%{_includedir}/GLES3/gl3platform.h
%{_includedir}/GLES3/gl3.h
%{_includedir}/GLES3/gl3ext.h
%{_includedir}/GLES3/gl31.h
%{_libdir}/pkgconfig/glesv2.pc
%{_libdir}/libGLESv2.so

%post libglapi -p /sbin/ldconfig
%postun libglapi -p /sbin/ldconfig
%files libglapi
%{_libdir}/libglapi.so.0
%{_libdir}/libglapi.so.0.*

%post libOSMesa -p /sbin/ldconfig
%postun libOSMesa -p /sbin/ldconfig
%files libOSMesa
%{_libdir}/libOSMesa.so.8*
%files libOSMesa-devel
%dir %{_includedir}/GL
%{_includedir}/GL/osmesa.h
%{_libdir}/libOSMesa.so
%{_libdir}/pkgconfig/osmesa.pc

%post libgbm -p /sbin/ldconfig
%postun libgbm -p /sbin/ldconfig
%files libgbm
%{_libdir}/libgbm.so.1
%{_libdir}/libgbm.so.1.*
%files libgbm-devel
%{_libdir}/libgbm.so
%{_includedir}/gbm.h
%{_libdir}/pkgconfig/gbm.pc

%if %{with wayland}
%post libwayland-egl -p /sbin/ldconfig
%postun libwayland-egl -p /sbin/ldconfig
%files libwayland-egl
%{_libdir}/libwayland-egl.so.1
%{_libdir}/libwayland-egl.so.1.*
%files libwayland-egl-devel
%{_libdir}/libwayland-egl.so
%{_libdir}/pkgconfig/wayland-egl.pc
%endif

%if 0%{?with_xa}
%post libxatracker -p /sbin/ldconfig
%postun libxatracker -p /sbin/ldconfig
%files libxatracker
%if %{with_hardware}
%{_libdir}/libxatracker.so.2
%{_libdir}/libxatracker.so.2.*
%endif

%files libxatracker-devel
%if %{with_hardware}
%{_libdir}/libxatracker.so
%{_includedir}/xa_tracker.h
%{_includedir}/xa_composite.h
%{_includedir}/xa_context.h
%{_libdir}/pkgconfig/xatracker.pc
%endif
%endif

%if 0%{?with_opencl}
%post libOpenCL -p /sbin/ldconfig
%postun libOpenCL -p /sbin/ldconfig
%files libOpenCL
%{_libdir}/libMesaOpenCL.so.*
%{_sysconfdir}/OpenCL/vendors/mesa.icd
%files libOpenCL-devel
%{_libdir}/libMesaOpenCL.so
%endif

%if 0%{?with_nine}
%files libd3d
%dir %{_libdir}/d3d/
%{_libdir}/d3d/*.so.*

%files libd3d-devel
%{_libdir}/pkgconfig/d3d.pc
%{_includedir}/d3dadapter/
%{_libdir}/d3d/*.so
%endif

%files dri-drivers
%if %{with_hardware}
%config(noreplace) %{_sysconfdir}/drirc
%{_libdir}/dri/radeon_dri.so
%{_libdir}/dri/r200_dri.so
%{_libdir}/dri/nouveau_vieux_dri.so
%{_libdir}/dri/r300_dri.so
%if 0%{?with_llvm}
%{_libdir}/dri/r600_dri.so
%if 0%{?with_radeonsi}
%{_libdir}/dri/radeonsi_dri.so
%endif
%endif
%ifarch %{ix86} x86_64
%{_libdir}/dri/i915_dri.so
%{_libdir}/dri/i965_dri.so
%if 0%{?with_ilo}
%{_libdir}/dri/ilo_dri.so
%endif
%endif
%if 0%{?with_vc4}
%{_libdir}/dri/vc4_dri.so
%endif
%if 0%{?with_freedreno}
%{_libdir}/dri/kgsl_dri.so
%{_libdir}/dri/msm_dri.so
%endif
%{_libdir}/dri/nouveau_dri.so
%if 0%{?with_vmware}
%{_libdir}/dri/vmwgfx_dri.so
%endif
%{_libdir}/dri/nouveau_drv_video.so
%if 0%{?with_llvm}
%{_libdir}/dri/r600_drv_video.so
%if 0%{?with_radeonsi}
%{_libdir}/dri/radeonsi_drv_video.so
%endif
%endif
%endif
%if 0%{?with_llvm}
%ifarch %{ix86} x86_64 aarch64
%dir %{_libdir}/gallium-pipe
%{_libdir}/gallium-pipe/*.so
%endif
%{_libdir}/dri/kms_swrast_dri.so
%endif
%{_libdir}/dri/swrast_dri.so
%{_libdir}/dri/virtio_gpu_dri.so

%if %{with_hardware}
%if 0%{?with_omx}
%files omx-drivers
%{_libdir}/bellagio/libomx_mesa.so
%endif
%if 0%{?with_vdpau}
%files vdpau-drivers
%{_libdir}/vdpau/libvdpau_nouveau.so.1*
%{_libdir}/vdpau/libvdpau_r300.so.1*
%if 0%{?with_llvm}
%{_libdir}/vdpau/libvdpau_r600.so.1*
%if 0%{?with_radeonsi}
%{_libdir}/vdpau/libvdpau_radeonsi.so.1*
%endif
%endif
%endif
%endif

%changelog
* Mon Sep  5 2016 Peter Robinson <pbrobinson@fedoraproject.org> 12.0.2-1
- 12.0.2

* Mon Sep  5 2016 Hans de Goede <hdegoede@redhat.com> - 12.0.1-7
- Fix PRIME fd leak

* Tue Aug 23 2016 Adam Jackson <ajax@redhat.com> - 12.0.1-6
- Remove BuildRequires: xorg-x11-server-devel

* Mon Aug 15 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.1-5
- Fix broken deps with OpenCL

* Sun Aug 14 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.1-4
- Fix broken deps

* Sun Aug 14 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.1-3
- Slightly refactor spec
- Drop virtual provides for OCL

* Tue Jul 19 2016 Orion Poplawski <orion@cora.nwra.com> - 12.0.1-2
- Add missing %%{?_isa} to requires in some devel sub-packages (bug #1138463)

* Sun Jul 10 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.1-1
- 12.0.1

* Fri Jul 08 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.0-1
- 12.0.0

* Wed Jun 22 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.0-0.3.rc4
- 12.0.0-rc4

* Mon Jun 20 2016 Adam Jackson <ajax@redhat.com> - 12.0.0-0.3.rc3
- Fix packaging error on s390*

* Mon Jun 20 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.0-0.2.rc3
- 12.0.0-rc3

* Tue Jun 14 2016 Dominik Mierzejewski <rpm@greysector.net> - 12.0.0-0.2.rc2
- add missing dependency for /etc/OpenCL/vendors ownership (RHBZ #1265948)

* Tue Jun 14 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.0-0.1.rc2
- 12.0.0-rc2

* Wed Jun 01 2016 Igor Gnatenko <ignatenko@redhat.com> - 12.0.0-0.1.rc1
- 12.0.0-rc1

* Sun May 01 2016 Igor Gnatenko <ignatenko@redhat.com> - 11.3.0-0.4.gitcbcd7b6
- cbcd7b6

* Thu Apr 14 2016 Igor Gnatenko <ignatenko@redhat.com> - 11.3.0-0.3.git171a570
- 171a570

* Fri Apr 08 2016 Björn Esser <fedora@besser82.io> - 11.3.0-0.2.gitea2bff1
- add virtual Provides for ocl-icd (RHBZ #1317602)

* Sun Mar 20 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.3.0-0.1.gitea2bff1
- 11.3.0 (gitea2bff1)
- Add SWR state-tracker (but disable because build is broken)
- Use gallium-osmesa instead of classic osmesa (RHBZ #1305588)
- Remove very old changelogs

* Sun Mar 20 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.2.0-0.1.rc3.20160320
- Update to 11.2.0-rc3

* Fri Feb 19 2016 Dave Airlie <airlied@redhat.com> 11.2.0-0.devel.11
- rebuild against llvm 3.8.0

* Fri Feb 12 2016 Dave Airlie <airlied@redhat.com> 11.2.0-0.devel.10
- rebuild against new llvm packages

* Thu Feb 11 2016 Adam Jackson <ajax@redhat.com> 11.2.0-0.devel.9
- Fix OpenCL-enabled FTBFS by not forcing clang search path to /usr/lib

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 11.2.0-0.devel.8.24ea81a.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 27 2016 Adam Jackson <ajax@redhat.com> 11.2.0-0.devel.8
- Rebuild for llvm 3.7.1 library split

* Sun Jan 24 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.2.0-0.devel.7.24ea81a
- 24ea81a

* Thu Jan 21 2016 Peter Robinson <pbrobinson@fedoraproject.org> 11.2.0-0.devel.6.5e3edd4
- OpenCL now supported on aarch64

* Sun Jan 10 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.2.0-0.devel.5.5e3edd4
- 5e3edd4

* Thu Jan 07 2016 Adam Jackson <ajax@redhat.com>
- Mangle libtool even harder to get -static-libstdc++ to work

* Tue Dec 29 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.2.0-0.devel.3.70d8dbc
- 70d8dbc

* Wed Dec 02 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.2.0-0.devel.2.56aff6b
- 56aff6b

* Sun Nov 22 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.2.0-0.devel.1.86fc97d
- 86fc97d

* Thu Nov 05 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.13.5ae37ae
- 5ae37ae

* Thu Nov 05 2015 Adam Jackson <ajax@redhat.com> 11.1.0-0.devel.12.3994ef5
- Link with -static-libstdc++ to work around Steam bundling its own copy

* Fri Oct 23 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.11.3994ef5
- 3994ef5
- Enable VirGL driver

* Thu Oct 22 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.10.7182498
- 7182498
- Disable SWR rasterizer

* Wed Oct 21 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.9.4a168ad
- Enable experimental SWR rasterizer

* Wed Oct 14 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.8.4a168ad
- 4a168ad

* Wed Oct 07 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.7.47d1199
- 47d1199

* Sat Sep 26 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.6.9932142
- 9932142

* Wed Sep 16 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.5.47e18a5
- 47e18a5
- Rebuild against llvm 3.7

* Sun Sep 13 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 11.1.0-0.devel.4.d6fbcf6
- d6fbcf6

* Thu Sep 10 2015 Rex Dieter <rdieter@fedoraproject.org> - 11.1.0-0.devel.3.60aea30
- Add brw_meta_fast_clear crash workaround patch (#1259443, fdo#86281)

* Wed Sep 02 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 11.1.0-0.devel.2.60aea30
- 60aea30

* Mon Aug 24 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 11.1.0-0.devel.1.4e5752e
- 4e5752e

* Sun Aug 09 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 11.0.0-0.devel.2.21ccdbd
- 21ccdbd
- add surfaceless EGL platform (RHBZ #1251747)

* Sat Aug 01 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 11.0.0-0.devel.1.6f2d889
- Update to 11.0.0

* Tue Jul 14 2015 Peter Robinson <pbrobinson@fedoraproject.org> 10.7.0-0.devel.4.ea633db
- Use %%license
- Minor spec cleanups

* Tue Jul 14 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.7.0-0.devel.3.ea633db
- ea633db

* Tue Jul 07 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.7.0-0.devel.2.8787141
- Drop unecessary make for s390

* Mon Jun 22 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.7.0-0.devel.1.8787141
- 8787141

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.6.0-0.devel.7.5a55f68.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.6.0-0.devel.7.5a55f68
- add git to BR everywhere

* Sun May 17 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.6.0-0.devel.6.5a55f68
- 5a55f68

* Thu May 07 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.6.0-0.devel.5.51e3453
- 51e3453

* Mon Apr 20 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.6.0-0.devel.4.c1485f4
- c1485f4

* Thu Apr 09 2015 Adam Jackson <ajax@redhat.com> 10.6.0-0.devel.3
- F23 rebuild against llvm 3.6.0

* Fri Feb 27 2015 Rob Clark <rclark@redhat.com - 10.6.0-0.devel.2.f80af89
- enable vc4 on arm

* Mon Feb 23 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.6.0-0.devel.1.f80af89
- f80af89

* Wed Feb 18 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-1.20150218
- 10.5.0

* Fri Jan 02 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.32.6171131
- 6171131

* Fri Jan 02 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.31.c3260f8
- c3260f8

* Fri Jan 02 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.30.290553b
- 290553b

* Thu Jan 01 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.28.b77eaaf
- b77eaaf

* Thu Jan 01 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.26.c633528
- c633528

* Thu Jan 01 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.25.a6f6d61
- a6f6d61

* Wed Dec 31 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.23.be0311c
- be0311c

* Wed Dec 31 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.21.609c3e5
- 609c3e5

* Wed Dec 31 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.19.3ba57ba
- 3ba57ba

* Tue Dec 30 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.17.64dcb2b
- 64dcb2b

* Mon Dec 29 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.15.6c18279
- 6c18279

* Sat Dec 27 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.13.0c7f895
- 0c7f895

* Fri Dec 26 2014 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10.5.0-0.devel.11.cb5a372
- cb5a372

* Sun Dec 21 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.10.git0d7f4c8
- enable ilo gallium driver

* Fri Dec 19 2014 Dan Horák <dan[at]danny.cz> 10.5.0-0.devel.9
- Sync with_{vaapi,vdpau,nine} settings with F21

* Thu Dec 18 2014 Adam Jackson <ajax@redhat.com> 10.5.0-0.devel.8
- Sync ppc build config with F21

* Wed Dec 17 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.7.git0d7f4c8
- fix requirements for d3d

* Sun Dec 14 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.6.git0d7f4c8
- 0d7f4c8

* Sun Dec 14 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.5.git29c7cf2
- Enable VA state-tracker
- Enable Nine state-tracker (Direct3D9 API)

* Thu Dec 11 2014 Adam Jackson <ajax@redhat.com> 10.5.0-0.devel.4
- Restore hardware drivers on ppc64{,le}

* Tue Dec 02 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.3.git29c7cf2
- 29c7cf2

* Sat Nov 22 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.2.git3d9c1a9
- 3d9c1a9

* Wed Nov 19 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.5.0-0.devel.1.git9460cd3
- 9460cd3

* Mon Nov 10 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.8.gitf3b709c
- f3b709c

* Tue Oct 28 2014  10.4-0.devel.7.git1a17098
- rebuild for llvm

* Mon Oct 27 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.6.git1a17098
- 1a17098

* Sat Sep 27 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.5.gitc3f17bb
- c3f17bb18f597d7f606805ae94363dae7fd51582

* Sat Sep 06 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.4.git1f184bc
- apply patch for bigendian from karsten
- fix ppc filelist from karsten

* Sat Sep 06 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.3.git1f184bc
- 1f184bc114143acbcea373184260da777b6c6be1 commit

* Thu Aug 28 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.2.1.80771e47b6c1e47ab55f17311e1d4e227a9eb3d8
- add swrast to dri driver list

* Wed Aug 27 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.2.80771e47b6c1e47ab55f17311e1d4e227a9eb3d8
- 80771e47b6c1e47ab55f17311e1d4e227a9eb3d8 commit

* Sat Aug 23 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.4-0.devel.1.c2867f5b3626157379ef0d4d5bcaf5180ca0ec1f
- 10.4 c2867f5b3626157379ef0d4d5bcaf5180ca0ec1f

* Fri Aug 22 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.3-0.rc1.1.e7f2f2dea5acdbd1a12ed88914e64a38a97432f0
- e7f2f2dea5acdbd1a12ed88914e64a38a97432f0 commit

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.3-0.devel.2.c40d7d6d948912a4d51cbf8f0854cf2ebe916636.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 06 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.3-0.devel.2.c40d7d6d948912a4d51cbf8f0854cf2ebe916636
- c40d7d6d948912a4d51cbf8f0854cf2ebe916636 commit

* Fri Jul 11 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.3-0.devel.1.f381c27c548aa28b003c8e188f5d627ab4105f76
- Rebase to 'master' branch (f381c27c548aa28b003c8e188f5d627ab4105f76 commit)

* Fri Jul 11 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2.3-1.20140711
- 10.2.3 upstream release

* Mon Jul  7 2014 Peter Robinson <pbrobinson@fedoraproject.org> 10.2.2-4.20140625
- Build aarch64 options the same as ARMv7
- Fix PPC conditionals

* Fri Jul 04 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2.2-3.20140625
- Fix up intelInitScreen2 for DRI3 (RHBZ #1115323) (patch from drago01)

* Fri Jun 27 2014 Dave Airlie <airlied@redhat.com> 10.2.2-2.20140625
- add dri3 gnome-shell startup fix from Jasper.

* Wed Jun 25 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2.2-1.20140625
- 10.2.2 upstream release

* Wed Jun 11 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2.1-2.20140608
- drop radeonsi llvm hack

* Sun Jun 08 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2.1-1.20140608
- 10.2.1 upstream release

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.2-0.11.rc5.20140531
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jun 04 2014 Dan Horák <dan[at]danny.cz> - 10.2-0.10.rc5.20140531
- fix build without hardware drivers

* Sat May 31 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.9.rc5.20140531
- 10.2-rc5 upstream release

* Wed May 28 2014 Brent Baude <baude@us.ibm.com> - 10.2-0.8.rc4.20140524
- Removing ppc64le arch from with_llvm

* Wed May 28 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.7.rc4.20140524
- i915: add a missing NULL pointer check (RHBZ #1100967)

* Sat May 24 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.6.rc4.20140524
- 10.2-rc4 upstream release
- add back updated radeonsi hack for LLVM

* Sat May 17 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.5.rc3.20140517
- 10.2-rc3 upstream release

* Sat May 10 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.4.rc2.20140510
- 10.2-rc2 upstream release
- drop radeonsi hack for LLVM

* Tue May 06 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.3.rc1.20140505
- Move gallium-pipe to the correct sub-package (RHBZ #1094588) (kwizart)
- Move egl_gallium.so to the correct location (RHBZ #1094588) (kwizart)
- Switch from with to enable for llvm shared libs (kwizart)

* Mon May 05 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.2.rc1.20140505
- Enable gallium-egl (needed by freedreeno) (RHBZ #1094199) (kwizart)

* Mon May 05 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.1.rc1.20140505
- Enable omx on x86 and arm (RHBZ #1094199) (kwizart)
- Split _with_xa from _with_vmware (RHBZ #1094199) (kwizart)
- Add _with_xa when arch is arm and _with_freedreeno (RHBZ #1094199) (kwizart)

* Mon May 05 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.2-0.rc1.20140505
- 10.2-rc1 upstream release

* Wed Apr 30 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1.1-3.20140430
- Update to today snapshot
- apply as downstream patches for reporting GPU max frequency on r600 (FD.o #73511)

* Sat Apr 19 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1.1-2.20140419
- fix buildrequires llvm 3.4-5 to 3.4-6, because 3.4-5 is not available for F20

* Sat Apr 19 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1.1-1.20140419
- 10.1.1 upstream release

* Tue Apr 15 2014 Adam Jackson <ajax@redhat.com> 10.1-6.20140305
- Disable DRI3 in F20, it requires libxcb bits we haven't backported.

* Wed Mar 26 2014 Adam Jackson <ajax@redhat.com> 10.1-5.20140305
- Initial ppc64le enablement (no hardware drivers or vdpau yet)

* Fri Mar 21 2014 Adam Jackson <ajax@redhat.com> 10.1-4.20140305
- mesa: Don't optimize out glClear if drawbuffer size is 0x0 (fdo #75797)

* Wed Mar 19 2014 Dave Airlie <airlied@redhat.com> 10.1-3.20140305
- rebuild against backported llvm 3.4-5 for radeonsi GL 3.3 support.

* Wed Mar 12 2014 Dave Airlie <airlied@redhat.com> 10.1-2.20140305
- disable r600 llvm compiler (upstream advice)

* Wed Mar 05 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1-1.20140305
- mesa: Bump version to 10.1 (final) (Ian Romanick)
- glx/dri2: fix build failure on HURD (Julien Cristau)
- i965: Validate (and resolve) all the bound textures. (Chris Forbes)
- i965: Widen sampler key bitfields for 32 samplers (Chris Forbes)

* Sat Mar 01 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1-0.rc3.20140301
- 10.1-rc3

* Tue Feb 25 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1-0.rc2.20140225
- really 10.1-rc2

* Sat Feb 22 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.1-0.rc2.20140222
- 10.1-rc2

* Sat Feb 08 2014 Adel Gadllah <adel.gadllah@gmail.com> - 10.1-0.rc1.20140208
- 10.1rc1
- Drop upstreamed patches

* Thu Feb 06 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.0.3-1.20140206
- 10.0.3 upstream release

* Tue Feb 04 2014 Kyle McMartin <kyle@redhat.com> - 10.0.2-6.20140118
- Fix accidentally inverted logic that meant radeonsi_dri.so went missing
  on all architectures instead of just ppc and s390. Sorry!

* Sun Feb 02 2014 Kyle McMartin <kyle@redhat.com> - 10.0.2-5.20140118
- Fix a thinko in previous commit wrt libdrm_nouveau2.

* Sun Feb 02 2014 Kyle McMartin <kyle@redhat.com> - 10.0.2-4.20140118
- Fix up building drivers on AArch64, enable LLVM there.
- Eliminate some F17 cruft from the spec, since we don't support it anymore.
- Conditionalize with_radeonsi on with_llvm instead of ppc,s390 && >F-17.
- Conditionalize libvdpau_radeonsi.so.1* on with_radeonsi instead of simply
  with_llvm to fix a build failure on AArch64.

* Sun Jan 19 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 10.0.2-3.20140118
- Enable OpenCL (RHBZ #887628)
- Enable r600 llvm compiler (RHBZ #1055098)
