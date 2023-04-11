Name:             mandoc
Version:          1.14.6
Release:          2
Summary:          A suite of tools for compiling mdoc and man

License:          ISC
URL:              https://mandoc.bsd.lv/
Source0:          https://mandoc.bsd.lv/snapshots/mandoc-%{version}.tar.gz
Patch0:           0001-add-compile-option.patch

BuildRequires:    gcc
BuildRequires:    make
BuildRequires:    clang
BuildRequires:    zlib-devel

# requirements for %%check
BuildRequires:    perl-interpreter
BuildRequires:    perl(IPC::Open3)

Requires(post):   %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
Requires(preun):  %{_sbindir}/update-alternatives

# The shared library package has been removed per discussion with the
# upstream maintainer.  If using the library, the static library is
# preferred because the API is not stable.
Provides:         libmandoc = %{version}-%{release}
Obsoletes:        libmandoc <= 1.14.5-10

%description
mandoc is a suite of tools compiling mdoc, the roff macro language of choice
for BSD manual pages, and man, the predominant historical language for UNIX
manuals. It is small, ISO C, ISC-licensed, and quite fast. The main component
of the toolset is the mandoc utility program, based on the libmandoc validating
compiler, to format output for UTF-8 and ASCII UNIX terminals, HTML 5,
PostScript, and PDF.

%package -n libmandoc-devel
Summary:        Development libraries and headers for libmandoc

%description -n libmandoc-devel
The mandoc library parses a UNIX manual into an abstract syntax tree (AST).
UNIX manuals are composed of mdoc(7) or man(7), and may be mixed with roff(7),
tbl(7), and eqn(7) invocations.

%prep
%autosetup -p1

%build
# NB: not an autoconf script
# settings are read in through configure.local
echo 'PREFIX=%{_prefix}'   >  configure.local
echo 'BINDIR=%{_bindir}'   >> configure.local
echo 'SBINDIR=%{_sbindir}' >> configure.local
echo 'MANDIR=%{_mandir}'   >> configure.local
echo 'INCLUDEDIR=%{_includedir}' >> configure.local
echo 'LIBDIR=%{_libdir}'   >> configure.local

# with default settings rpmlint complains about cross-directory hardlinks
echo 'LN="ln -sf"' >> configure.local

echo 'MANM_MANCONF=mandoc.conf'          >> configure.local

# override the install permissions so that owner-write bits are set,
# so rpmbuild can do whatever modifications it does post-%%install
echo 'INSTALL_PROGRAM="${INSTALL} -m 0755"' >> configure.local
echo 'INSTALL_LIB="${INSTALL} -m 0755"'     >> configure.local
echo 'INSTALL_MAN="${INSTALL} -m 0644"'     >> configure.local
echo 'INSTALL_DATA="${INSTALL} -m 0644"'    >> configure.local

echo 'INSTALL_LIBMANDOC=1' >> configure.local

echo 'CFLAGS="%{optflags} -fPIC"' >> configure.local
export CC=clang
./configure
%make_build

%install
%make_install

# Ensure headers do not have the execute bit set
chmod -x %{buildroot}%{_includedir}/*.h

# Rename files for alternative usage
mv %{buildroot}%{_bindir}/man %{buildroot}%{_bindir}/man.mandoc
mv %{buildroot}%{_bindir}/apropos %{buildroot}%{_bindir}/apropos.mandoc
mv %{buildroot}%{_bindir}/whatis %{buildroot}%{_bindir}/whatis.mandoc
mv %{buildroot}%{_bindir}/soelim %{buildroot}%{_bindir}/soelim.mandoc
mv %{buildroot}%{_sbindir}/makewhatis %{buildroot}%{_sbindir}/makewhatis.mandoc
mv %{buildroot}%{_mandir}/man1/apropos.1 %{buildroot}%{_mandir}/man1/apropos.mandoc.1
mv %{buildroot}%{_mandir}/man1/man.1 %{buildroot}%{_mandir}/man1/man.mandoc.1
mv %{buildroot}%{_mandir}/man1/soelim.1 %{buildroot}%{_mandir}/man1/soelim.mandoc.1
mv %{buildroot}%{_mandir}/man1/whatis.1 %{buildroot}%{_mandir}/man1/whatis.mandoc.1
mv %{buildroot}%{_mandir}/man7/man.7 %{buildroot}%{_mandir}/man7/man.mandoc.7
mv %{buildroot}%{_mandir}/man7/roff.7 %{buildroot}%{_mandir}/man7/roff.mandoc.7
mv %{buildroot}%{_mandir}/man7/eqn.7 %{buildroot}%{_mandir}/man7/eqn.mandoc.7
mv %{buildroot}%{_mandir}/man7/tbl.7 %{buildroot}%{_mandir}/man7/tbl.mandoc.7
mv %{buildroot}%{_mandir}/man8/makewhatis.8 %{buildroot}%{_mandir}/man8/makewhatis.mandoc.8

# Touch all the locations that update-alternatives will use
touch %{buildroot}%{_bindir}/man
touch %{buildroot}%{_bindir}/apropos
touch %{buildroot}%{_bindir}/whatis
touch %{buildroot}%{_bindir}/soelim
touch %{buildroot}%{_sbindir}/makewhatis
touch %{buildroot}%{_mandir}/man1/apropos.1
touch %{buildroot}%{_mandir}/man1/man.1
touch %{buildroot}%{_mandir}/man1/soelim.1
touch %{buildroot}%{_mandir}/man1/whatis.1
touch %{buildroot}%{_mandir}/man7/man.7
touch %{buildroot}%{_mandir}/man7/roff.7
touch %{buildroot}%{_mandir}/man7/eqn.7
touch %{buildroot}%{_mandir}/man7/tbl.7
touch %{buildroot}%{_mandir}/man8/makewhatis.8

%check
env LD_LIBRARY_PATH="$PWD" %make_build regress

%postun
if [ $1 -ge 1 ]; then
    if [ "$(readlink %{_sysconfdir}/alternatives/man)" = "%{_bindir}/man.mandoc" ]; then
        %{_sbindir}/alternatives --set man %{_bindir}/man.mandoc
    fi

    if [ "$(readlink %{_sysconfdir}/alternatives/soelim)" = "%{_bindir}/soelim.mandoc" ]; then
        %{_sbindir}/alternatives --set soelim %{_bindir}/soelim.mandoc
    fi

    if [ "$(readlink %{_sysconfdir}/alternatives/roff.7.gz)" = "%{_mandir}/man7/roff.mandoc.7.gz" ]; then
        %{_sbindir}/alternatives --set roff.7.gz %{_mandir}/man7/roff.mandoc.7.gz
    fi

    if [ "$(readlink %{_sysconfdir}/alternatives/man.7.gz)" = "%{_mandir}/man7/man.mandoc.7.gz" ]; then
        %{_sbindir}/alternatives --set man.7.gz %{_mandir}/man7/man.mandoc.7.gz
    fi
fi

%post
%{_sbindir}/update-alternatives --install %{_bindir}/man man %{_bindir}/man.mandoc 200 \
    --slave %{_bindir}/apropos apropos %{_bindir}/apropos.mandoc \
    --slave %{_bindir}/whatis whatis %{_bindir}/whatis.mandoc \
    --slave %{_sbindir}/makewhatis makewhatis %{_sbindir}/makewhatis.mandoc \
    --slave %{_mandir}/man1/apropos.1.gz apropos.1.gz %{_mandir}/man1/apropos.mandoc.1.gz \
    --slave %{_mandir}/man1/man.1.gz man.1.gz %{_mandir}/man1/man.mandoc.1.gz \
    --slave %{_mandir}/man1/whatis.1.gz whatis.1.gz %{_mandir}/man1/whatis.mandoc.1.gz \
    --slave %{_mandir}/man8/makewhatis.8.gz makewhatis.8.gz %{_mandir}/man8/makewhatis.mandoc.8.gz

%{_sbindir}/update-alternatives --install %{_bindir}/soelim soelim %{_bindir}/soelim.mandoc 200 \
    --slave %{_mandir}/man1/soelim.1.gz soelim.1.gz %{_mandir}/man1/soelim.mandoc.1.gz

%{_sbindir}/update-alternatives --install %{_mandir}/man7/roff.7.gz roff.7.gz %{_mandir}/man7/roff.mandoc.7.gz 200 \
    --slave %{_mandir}/man7/eqn.7.gz eqn.7.gz %{_mandir}/man7/eqn.mandoc.7.gz \
    --slave %{_mandir}/man7/tbl.7.gz tbl.7.gz %{_mandir}/man7/tbl.mandoc.7.gz

%{_sbindir}/update-alternatives --install %{_mandir}/man7/man.7.gz man.7.gz %{_mandir}/man7/man.mandoc.7.gz 200

%preun
if [ $1 -eq 0 ]; then
    %{_sbindir}/update-alternatives --remove man %{_bindir}/man.mandoc
    %{_sbindir}/update-alternatives --remove soelim %{_bindir}/soelim.mandoc
    %{_sbindir}/update-alternatives --remove roff.7.gz %{_mandir}/man7/roff.mandoc.7.gz
    %{_sbindir}/update-alternatives --remove man.7.gz %{_mandir}/man7/man.mandoc.7.gz
fi

%files
%license LICENSE
%{_bindir}/demandoc
%{_bindir}/mandoc
%{_bindir}/apropos.mandoc
%ghost %{_bindir}/apropos
%{_bindir}/man.mandoc
%ghost %{_bindir}/man
%{_bindir}/soelim.mandoc
%ghost %{_bindir}/soelim
%{_bindir}/whatis.mandoc
%ghost %{_bindir}/whatis
%{_sbindir}/makewhatis.mandoc
%ghost %{_sbindir}/makewhatis
%{_mandir}/man1/demandoc.1.gz
%{_mandir}/man1/mandoc.1.gz
%{_mandir}/man1/apropos.mandoc.1.gz
%ghost %{_mandir}/man1/apropos.1.gz
%{_mandir}/man1/man.mandoc.1.gz
%ghost %{_mandir}/man1/man.1.gz
%{_mandir}/man1/soelim.mandoc.1.gz
%ghost %{_mandir}/man1/soelim.1.gz
%{_mandir}/man1/whatis.mandoc.1.gz
%ghost %{_mandir}/man1/whatis.1.gz
%{_mandir}/man5/mandoc.conf.5.gz
%{_mandir}/man5/mandoc.db.5.gz
%{_mandir}/man7/eqn.mandoc.7.gz
%ghost %{_mandir}/man7/eqn.7.gz
%{_mandir}/man7/mandoc_char.7.gz
%{_mandir}/man7/man.mandoc.7.gz
%ghost %{_mandir}/man7/man.7.gz
%{_mandir}/man7/mdoc.7.gz
%{_mandir}/man7/roff.mandoc.7.gz
%ghost %{_mandir}/man7/roff.7.gz
%{_mandir}/man7/tbl.mandoc.7.gz
%ghost %{_mandir}/man7/tbl.7.gz
%{_mandir}/man8/makewhatis.mandoc.8.gz
%ghost %{_mandir}/man8/makewhatis.8.gz

%files -n libmandoc-devel
%license LICENSE
%{_libdir}/libmandoc.a
%{_includedir}/eqn.h
%{_includedir}/man.h
%{_includedir}/mandoc.h
%{_includedir}/mandoc_aux.h
%{_includedir}/mandoc_parse.h
%{_includedir}/mdoc.h
%{_includedir}/roff.h
%{_includedir}/tbl.h
%{_mandir}/man3/mandoc.3*
%{_mandir}/man3/mandoc_escape.3*
%{_mandir}/man3/mandoc_malloc.3*
%{_mandir}/man3/mansearch.3*
%{_mandir}/man3/mchars_alloc.3*
%{_mandir}/man3/tbl.3*

%changelog
* Thu Apr 6 2023 changzhangm <chaozhangm@isoftstone.com> - 1.14.6-2
- Update to 1.14.6-2
* Fri Sep 23 2022 chendexi <chendexi@kylinos.cn> - 1.14.6-1
- Initial package

