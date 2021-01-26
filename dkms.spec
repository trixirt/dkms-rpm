%global commit0 5ca628c40218d7deb4b94d6c568c078c68b9e1c6
%global date 20200214
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global tag 1

Summary:        Dynamic Kernel Module Support Framework
Name:           dkms
Version:        2.8.4
Release:        2%{?dist}
License:        GPLv2+
URL:            http://linux.dell.com/dkms

BuildArch:      noarch

%if 0%{?tag:1}
Source0:        https://github.com/dell/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
%else
Source0:        https://github.com/dell/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%endif

BuildRequires:  systemd
BuildRequires: make

Requires:       coreutils
Requires:       cpio
Requires:       elfutils-libelf-devel
Requires:       file
Requires:       findutils
Requires:       gawk
Requires:       gcc
Requires:       grep
Requires:       gzip
Requires:       kmod
Requires:       make
Requires:       sed
Requires:       tar
Requires:       which

# The virtual provide 'kernel-devel-uname-r' tries to get the right
# kernel variant  (kernel-PAE, kernel-debug, etc.) devel package
# installed.
# https://bugzilla.redhat.com/show_bug.cgi?id=1420754#c0
# https://bugzilla.redhat.com/show_bug.cgi?id=1421105#c2
Requires:       kernel-devel-uname-r

Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
This package contains the framework for the Dynamic Kernel Module Support (DKMS)
method for installing module RPMS as originally developed by Dell.

%prep
%if 0%{?tag:1}
%autosetup -p1
%else
%autosetup -p1 -n %{name}-%{commit0}
%endif

%install
make install-redhat-systemd \
    DESTDIR=%{buildroot} \
    LIBDIR=%{buildroot}%{_prefix}/lib/%{name} \
    SYSTEMD=%{buildroot}%{_unitdir}

install -p -m 755 -D kernel_install.d_dkms \
    %{buildroot}%{_prefix}/lib/kernel/install.d/40-%{name}.install

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%license COPYING
%doc sample.spec sample.conf AUTHORS README.md
%{_prefix}/lib/%{name}
%{_prefix}/lib/kernel/install.d/40-%{name}.install
%{_mandir}/man8/dkms.8*
%{_sbindir}/%{name}
%{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}
%{_sysconfdir}/kernel/postinst.d/%{name}
%{_sysconfdir}/kernel/prerm.d/%{name}
%{_datadir}/bash-completion/completions/%{name}
%{_unitdir}/%{name}.service

%changelog
* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.8.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Nov 30 2020 Simone Caronni <negativo17@gmail.com> - 2.8.4-1
- Update to 2.8.4.

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.8.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 20 2020 Simone Caronni <negativo17@gmail.com> - 2.8.3-2
- Add make to requirements.

* Wed Jul 15 2020 Simone Caronni <negativo17@gmail.com> - 2.8.3-1
- Update to 2.8.3.

* Thu Jul 02 2020 Simone Caronni <negativo17@gmail.com> - 2.8.2-1
- Update to 2.8.2.
- Add sign helper script sample to docs.

* Wed Feb 19 2020 Martin Jackson <mhjacks@swbell.net> - 2.8.1-4.20200214git5ca628c
- Change mode to 755 for new install.d script.

* Sat Feb 15 2020 Simone Caronni <negativo17@gmail.com> - 2.8.1-3.20200214git5ca628c
- Update to latest snapshot.

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Dec 01 2019 Simone Caronni <negativo17@gmail.com> - 2.8.1-1
- Update to 2.8.1.

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed May 15 2019 Simone Caronni <negativo17@gmail.com> - 2.7.1-1
- Update to 2.7.1.

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed May 09 2018 Simone Caronni <negativo17@gmail.com> - 2.6.1-1
- Update to 2.6.1.

* Tue Mar 06 2018 Simone Caronni <negativo17@gmail.com> - 2.5.0-3.20180306gitb1b9033
- Update to latest snapshot.

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.5.0-2.20180124git215d01a
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 24 2018 Simone Caronni <negativo17@gmail.com> - 2.5.0-1.20180124git215d01a
- Update to latest post 2.5.0 snapshot.
- Trim changelog.
- Remove support for CentOS/RHEL 6, as the last two versions were not compaible
  with it (bash too old, etc.).

* Mon Oct 09 2017 Simone Caronni <negativo17@gmail.com> - 2.4.0-1.20170926git959bd74
- Update to latest commits post 2.4.
- Add elfutils-libelf-devel build requirement.

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3-6.20170523git8c3065c
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue May 23 2017 Simone Caronni <negativo17@gmail.com> - 2.3-5.20170523git8c3065c
- Update to latest snapshot; lots of specific Red Hat/Fedora cleanups (obsolete
  Red Hat/Fedora code, Itanium support, /boot leftovers) and module autoload.

* Wed Apr 05 2017 Simone Caronni <negativo17@gmail.com> - 2.3-4.20170313git974d838
- Update to latest snapshot.
- Do not require wrong kernel-devel variant (#1436840).

* Sat Feb 11 2017 Simone Caronni <negativo17@gmail.com> - 2.3-3.20161202gitde1dca9
- Require kernel-devel-uname-r in place of kernel-devel and suggest kernel-devel
  for Fedora (#1421106).

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3-2.20161202gitde1dca9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

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
