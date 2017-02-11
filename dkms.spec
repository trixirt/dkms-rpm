%global commit0 de1dca939ac0f72100cb599e0872347f927f940c
%global date 20161202
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Summary:        Dynamic Kernel Module Support Framework
Name:           dkms
Version:        2.3
Release:        2%{?shortcommit0:.%{date}git%{shortcommit0}}%{?dist}
License:        GPLv2+
URL:            http://linux.dell.com/dkms

BuildArch:      noarch

Source0:        https://github.com/dell-oss/%{name}/archive/%{commit0}/%{name}-%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Source1:        %{name}_autoinstaller.init

Requires:       coreutils
Requires:       cpio
Requires:       file
Requires:       findutils
Requires:       gawk
Requires:       gcc
Requires:       grep
Requires:       gzip
Requires:       sed
Requires:       tar
Requires:       which

# The virtual provide 'kernel-devel-uname-r' tries to get the right
# kernel variant  (kernel-PAE, kernel-debug, etc.) devel package
# installed.
# https://bugzilla.redhat.com/show_bug.cgi?id=1420754#c0
# https://bugzilla.redhat.com/show_bug.cgi?id=1421105#c2
Requires: kernel-devel-uname-r
%{?fedora:Suggests: kernel-devel}

%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires:          systemd
Requires:               kmod
Requires(post):         systemd
Requires(preun):        systemd
Requires(postun):       systemd
%else
Requires:               module-init-tools
Requires(post):         /sbin/chkconfig
Requires(preun):        /sbin/chkconfig
Requires(preun):        /sbin/service
Requires(postun):       /sbin/service
%endif

%description
This package contains the framework for the Dynamic Kernel Module Support (DKMS)
method for installing module RPMS as originally developed by Dell.

%prep
%setup -qn %{name}-%{commit0}

%install
rm -rf %{buildroot}

%if 0%{?fedora} || 0%{?rhel} >= 7
make install-redhat-systemd DESTDIR=%{buildroot} \
    LIBDIR=%{buildroot}%{_prefix}/lib/%{name} \
    SYSTEMD=%{buildroot}%{_unitdir}
%else
make install-redhat-sysv DESTDIR=%{buildroot} \
    LIBDIR=%{buildroot}%{_prefix}/lib/%{name}

# Overwrite SysV init script
install -p -m 755 -D %{SOURCE1} %{buildroot}%{_initrddir}/%{name}_autoinstaller
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

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
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc sample.spec sample.conf AUTHORS README.md
%if 0%{?fedora} || 0%{?rhel} >= 7
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
* Sat Feb 11 2017 Simone Caronni <negativo17@gmail.com> - 2.3-2.20161202gitde1dca9
- Require kernel-devel-uname-r in place of kernel-devel and suggest kernel-devel
  for Fedora (#1421106).

* Fri Dec 02 2016 Simone Caronni <negativo17@gmail.com> - 2.3-1.20161101gitede1dca
- Update to latest snapshot.
- Adjust release tag to packaging guidelines.
- Fix scriptlets.

* Fri May 27 2016 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-35.git.eb402f7
- Update to latest sources (#912300).

* Wed May 25 2016 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-34.git.9e0394d
- Update to latest sources (#1334103).

* Tue May 24 2016 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-33.git.4c69692
- Remove RHEL 5 support from SPEC file, latest source code does not work on it.
- Switch to new Github source code repository, adjust to packaging guidelines
  accordingly.
- Adjust Fedora conditionals.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0.3-32.git.7c3e7c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.0.3-31.git.7c3e7c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Feb 25 2015 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-30.git.7c3e7c5
- Add which and file requirements for real.

* Tue Feb 24 2015 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-29.git.7c3e7c5
- Add which and file requirements (#1194652).
- Add license macro.

* Tue Sep 23 2014 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-28.git.7c3e7c5
- Update to latest git, all patches merged upstream.

* Tue Sep 23 2014 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-27.git.2238e7b
- Update to latest git, 99% of the patches merged upstream.
- Simplify SPEC file.
- Fix inter-module dependencies (#1140812).
  Thanks Bruno Faccini.

* Mon Sep 08 2014 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-26
- Further syntax fix (#1139006). Thanks Goffredo Baroncelli.

* Fri Jun 27 2014 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-25
- Enable all patches also for RHEL 5 builds.
- Skip initramfs/initrd rebuild if not requested (#1109601).

* Fri Jun 27 2014 Julien Floret <julien.floret@6wind.com> - 2.2.0.3-24
- Prevent parallel depmod failure with autoinstall (#1113946).

* Tue Jun 17 2014 Simone Caronni <negativo17@gmail.com> - 2.2.0.3-23
- Update shell syntax (#1104253).

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
