#
# Conditional build:
%bcond_without	apidocs		# HTML documentation
%bcond_with	sdp		# SDP support (requires infiniband patches to linux-libc-headers)
%bcond_without	static_libs	# static library
%bcond_without	tools		# ublk tool
#
Summary:	Uesrspace block driver (ublk)
Summary(pl.UTF-8):	Sterownik urządzeń blokowych w przestrzeni użytkownika (ublk)
Name:		ublksrv
Version:	1.5
Release:	1
License:	LGPL v2 or MIT (library), GPL v2 or MIT (tool), GPL v2 (qcow2 target)
Group:		Libraries
#Source0Download: https://github.com/ublk-org/ublksrv/tags
Source0:	https://github.com/ublk-org/ublksrv/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	15a18cd78656d7a30d81a600d6eee8ae
URL:		https://github.com/ublk-org/ublksrv
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
%{?with_apidocs:BuildRequires:	doxygen}
# for nbd client
BuildRequires:	gnutls-devel >= 2.12.0
BuildRequires:	libiscsi-devel >= 1.20.1
BuildRequires:	libnfs-devel >= 6.0.2-2
BuildRequires:	libstdc++-devel >= 6:4.7
# -std=c++20 -fcoroutines
%{?with_tools:BuildRequires:	libstdc++-devel >= 6:10}
BuildRequires:	libtool >= 2:2
BuildRequires:	liburing-devel >= 2.2
BuildRequires:	pkgconfig
BuildRequires:	rpm-build >= 4.6
Requires:	%{name}-libs = %{version}-%{release}
Obsoletes:	ubdsrv < 1.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is the userspace daemon part (ublksrv) of the ublk framework.

%description -l pl.UTF-8
Ten pakiet zawiera część serwerową (ublksrv) przestrzeni użytkownika
szkieletu ublk.

%package libs
Summary:	ublk server library
Summary(pl.UTF-8):	Biblioteka serwera ublk
Group:		Libraries
Requires:	liburing >= 2.2
Obsoletes:	ubdsrv-libs < 1.1

%description libs
ublk server library.

%description libs -l pl.UTF-8
Biblioteka serwera ublk.

%package devel
Summary:	Header files for ublksrv library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki ublksrv
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	liburing-devel >= 2.2
Obsoletes:	ubdsrv-devel < 1.1

%description devel
Header files for ublksrv library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki ublksrv.

%package static
Summary:	Static ublksrv library
Summary(pl.UTF-8):	Statyczna biblioteka ublksrv
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
Obsoletes:	ubdsrv-static < 1.1

%description static
Static ublksrv library.

%description static -l pl.UTF-8
Statyczna biblioteka ublksrv.

%package apidocs
Summary:	API documentation for ublksrv library
Summary(pl.UTF-8):	Dokumentacja API biblioteki ublksrv
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for ublksrv library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki ublksrv.

%prep
%setup -q

%{__sed} -i -e 's,/usr/bin/chown,/bin/chown,' utils/ublk_chown*.sh

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	%{?with_sdp:--enable-sdp} \
	%{!?with_static_libs:--disable-static}

%{__make} %{!?with_tools:-C lib}

%if %{with apidocs}
%{__make} doxygen_doc
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with tools}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
%else
%{__make} -C lib install \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} -C include install \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} install-pkgconfigDATA \
	DESTDIR=$RPM_BUILD_ROOT
%endif

# what is the use case?
%{__rm} $RPM_BUILD_ROOT%{_sbindir}/ublk_chown_docker.sh

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%if %{with tools}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/ublk
%attr(755,root,root) %{_sbindir}/ublk.iscsi
%attr(755,root,root) %{_sbindir}/ublk.loop
%attr(755,root,root) %{_sbindir}/ublk.nbd
%attr(755,root,root) %{_sbindir}/ublk.nfs
%attr(755,root,root) %{_sbindir}/ublk.null
%attr(755,root,root) %{_sbindir}/ublk_chown.sh
%attr(755,root,root) %{_sbindir}/ublk_user_id
%{_mandir}/man1/ublk.1*
%endif

%files libs
%defattr(644,root,root,755)
%doc LICENSE README.rst
%attr(755,root,root) %{_libdir}/libublksrv.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libublksrv.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libublksrv.so
%{_includedir}/ublk_cmd.h
%{_includedir}/ublksrv.h
%{_includedir}/ublksrv_aio.h
%{_includedir}/ublksrv_utils.h
%{_pkgconfigdir}/ublksrv.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libublksrv.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc doc/html/*
%endif
