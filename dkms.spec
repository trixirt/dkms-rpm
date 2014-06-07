%if 0%{?rhel} == 5
%define _sharedstatedir /var/lib
%endif

Summary:        Dynamic Kernel Module Support Framework
Name:           dkms
Version:        2.2.0.3
Release:        22%{dist}
License:        GPLv2+
Group:          System Environment/Base
BuildArch:      noarch
URL:            http://linux.dell.com/dkms
BuildRoot:      %{_tmppath}/%{name}-%{version}.%{release}-root-%(%{__id_u} -n)

Source0:        http://linux.dell.com/%{name}/permalink/%{name}-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}_autoinstaller.init

Patch0:         %{name}-git.patch
Patch1:         %{name}-force-tarball.patch
Patch2:         %{name}-fix-mkrpm.patch
Patch3:         %{name}-man.patch
# Patches coming from ZFS On Linux project for functionality / bugfixes
# https://github.com/zfsonlinux/dkms/tree/master/ubuntu/saucy/debian/patches
Patch4:         %{name}-cleanup-after-removal.patch
Patch5:         %{name}-do-not-fail-on-modules-dir.patch
# https://github.com/zfsonlinux/dkms/tree/master/ubuntu/precise/debian/patches
Patch6:         %{name}-add-POST_BUILD-to-the-dkms_conf_variables-list.patch
Patch7:         %{name}-use-STRIP-0-as-the-default-for-the-STRIP-array.patch
Patch8:         %{name}-add-dependency-logic-for-automatic-builds.patch
Patch9:         %{name}-fix-zfs-autoinstall-failures-for-kernel-upgrades.patch
Patch10:        %{name}-reset-build-dependencies.patch

Requires:       coreutils
Requires:       cpio
Requires:       findutils
Requires:       gawk
Requires:       gcc
Requires:       grep
Requires:       gzip
Requires:       kernel-devel
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires:       kmod
%else
Requires:       module-init-tools
%endif
Requires:       sed
Requires:       tar

%if 0%{?fedora} >= 20 || 0%{?rhel} >= 7
BuildRequires:          systemd
Requires(post):         systemd
Requires(preun):        systemd
Requires(postun):       systemd
%else
Requires(post):         /sbin/chkconfig
Requires(preun):        /sbin/chkconfig
Requires(preun):        /sbin/service
Requires(postun):       /sbin/service
%endif

%description
This package contains the framework for the Dynamic Kernel Module Support (DKMS)
method for installing module RPMS as originally developed by Dell.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%if 0%{?fedora} || 0%{?rhel} >= 6
%patch8 -p1
%patch9 -p1
%patch10 -p1
%endif

%build

%install
rm -rf %{buildroot}
make install-redhat DESTDIR=%{buildroot} \
    SBIN=%{buildroot}%{_sbindir} \
    VAR=%{buildroot}%{_sharedstatedir}/%{name} \
    MAN=%{buildroot}%{_mandir}/man8 \
    ETC=%{buildroot}%{_sysconfdir}/%{name} \
    BASHDIR=%{buildroot}%{_sysconfdir}/bash_completion.d \
    LIBDIR=%{buildroot}%{_prefix}/lib/%{name}

%if 0%{?fedora} >= 20 || 0%{?rhel} >= 7

# Systemd unit files
rm -rf %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

%else

# Initscripts
mkdir -p %{buildroot}%{_initrddir}
install -p -m 755 -D %{SOURCE2} %{buildroot}%{_initrddir}/%{name}_autoinstaller

%endif

%clean
rm -rf %{buildroot}

%if 0%{?fedora} >= 20 || 0%{?rhel} >= 7

%post
%systemd_post %{name}_autoinstaller.service

%preun
%systemd_preun %{name}_autoinstaller.service

%postun
%systemd_postun %{name}_autoinstaller.service

%else

%post
/sbin/chkconfig --add %{name}_autoinstaller
/sbin/chkconfig %{name}_autoinstaller on

%preun
if [ "$1" = 0 ]; then
        /sbin/service %{name}_autoinstaller stop >/dev/null 2>&1 || :
        /sbin/chkconfig --del %{name}_autoinstaller
fi

%postun
if [ "$1" -ge "1" ]; then
        /sbin/service %{name}_autoinstaller condrestart >/dev/null 2>&1 || :
fi

%endif

%files
%defattr(-,root,root)
%doc sample.spec sample.conf AUTHORS COPYING README.dkms
%if 0%{?fedora} >= 20 || 0%{?rhel} >= 7
%{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}_autoinstaller
%endif
%{_prefix}/lib/%{name}
%{_mandir}/man8/dkms.8*
%{_sbindir}/%{name}
%{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}
%{_sysconfdir}/kernel/postinst.d/%{name}
%{_sysconfdir}/kernel/prerm.d/%{name}
%{_sysconfdir}/bash_completion.d/%{name}

%changelog
* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.0.3-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Jan 17 2014 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-21
- Adjust directory extraction due to regenerated tarball upstream.

* Thu Nov 07 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-20
- Exclude build dependency logic for RHEL/CentOS 5.

* Wed Nov 06 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-19
- Add macros to the top of the man page to fix displaying on el5/el6 (#986660).
  Thanks to Darik Horn for the fix.

* Mon Nov 04 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-18
- Add ZFS On Linux patches for additional functionality/bugfixes (#1023598).
  Thanks to Darik Horn and Brian Behlendorf.

* Thu Aug 29 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-17
- Add propert patch for 1002551.

* Thu Aug 29 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-16
- Add patch to fix mkrpm spec file template in #1002551.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.0.3-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 22 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-14
- Remove systemd / SysV conversion as per new packaging guidelines.
- Add patch for #986887 to force tarball creation.

* Mon Jul 22 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-13
- Add fix for #986887; do not use lib64 for storing data as it was in 2.2.0.3-5.

* Sun Jul 21 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-12
- Add patch for #986557.

* Thu Jul 04 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-11
- Make service file more verbose.

* Sat Jun 29 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-10
- Fix SysV/systemd upgrade.

* Wed Jun 26 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-9
- Update systemd requirements.

* Mon Jun 24 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-8
- Do not use kmod on RHEL 5/6.

* Thu Jun 20 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-7
- Update to upstream git.
- Fix SysV init scriptlet and init file.

* Thu May 23 2013 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-6
- Rework spec file completely; remove cruft.
- Trim changelog.
- Rework install parameters, use correct macros.
- Rework file list.
- Add proper SysV and systemd requirements.
- Add correct SysV init script and systemd service file.
- Enable systemd on Fedora 20+ and add it to systemd preset as per
  https://fedorahosted.org/fesco/ticket/1123

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.0.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.0.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun  5 2012 Praveen K Paladugu <praveen_paladugu@dell.com> -2.2.0.3-3
- don't move dkms to dkms.old. This breaks updates

* Wed Feb  8 2012 Kay Sievers <kay@redhat.com> - 2.2.0.3-2
- modutils are for Linux 2.4 and no longer provided; depend on kmod

* Tue Jan 10 2012 Sunil Gupta <Sunil_Gupta2@dell.com> - 2.2.0.3-1
- update to 2.2.0.3
