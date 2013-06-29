%if 0%{?rhel} == 5
%define _sharedstatedir /var/lib
%endif

Summary:        Dynamic Kernel Module Support Framework
Name:           dkms
Version:        2.2.0.3
Release:        10%{dist}
License:        GPLv2+
Group:          System Environment/Base
BuildArch:      noarch
URL:            http://linux.dell.com/dkms
BuildRoot:      %{_tmppath}/%{name}-%{version}.%{release}-root-%(%{__id_u} -n)

Source0:        http://linux.dell.com/%{name}/permalink/%{name}-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}_autoinstaller.init
Patch0:         %{name}-git.patch

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
Requires(post):         systemd-sysv
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
%setup -q -n dkms
%patch0 -p1

%build

%install
rm -rf %{buildroot}
make install-redhat DESTDIR=%{buildroot} \
    SBIN=%{buildroot}%{_sbindir} \
    VAR=%{buildroot}%{_sharedstatedir}/%{name} \
    MAN=%{buildroot}%{_mandir}/man8 \
    ETC=%{buildroot}%{_sysconfdir}/%{name} \
    BASHDIR=%{buildroot}%{_sysconfdir}/bash_completion.d \
    LIBDIR=%{buildroot}%{_libdir}/%{name}

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

%triggerun -- dkms < 2.2.0.3-9
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save %{name}_autoinstaller >/dev/null 2>&1 ||:

# If the package is allowed to autostart:
/bin/systemctl --no-reload enable %{name}.service >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del %{name}_autoinstaller >/dev/null 2>&1 || :
/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :

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
%{_libdir}/%{name}
%{_mandir}/man8/dkms.8*
%{_sbindir}/%{name}
%{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}
%{_sysconfdir}/kernel/postinst.d/%{name}
%{_sysconfdir}/kernel/prerm.d/%{name}
%{_sysconfdir}/bash_completion.d/%{name}

%changelog
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
