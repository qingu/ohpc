#----------------------------------------------------------------------------bh-
# This RPM .spec file is part of the OpenHPC project.
#
# It may have been modified from the default version supplied by the underlying
# release package (if available) in order to apply patches, perform customized
# build/install configurations, and supply additional files to support
# desired integration conventions.
#
#----------------------------------------------------------------------------eh-

%include %{_sourcedir}/OHPC_macros
%{!?PROJ_DELIM: %global PROJ_DELIM -ohpc}

# Base package name
%define pname easybuild
%define PNAME %(echo %{pname} | tr [a-z] [A-Z])

%define vsc_base_ver 2.5.4
%define vsc_install_ver 0.10.15

Summary:   Build and installation framework
Name:      EasyBuild%{PROJ_DELIM}
Version:   2.9.0
Release:   1
License:   GPLv2
Group:     System/Configuration
URL:       http://hpcugent.github.com/easybuild

Source0:   https://pypi.io/packages/source/e/easybuild-easyblocks/easybuild-easyblocks-%{version}.tar.gz
Source1:   https://pypi.io/packages/source/e/easybuild-easyconfigs/easybuild-easyconfigs-%{version}.tar.gz
Source2:   https://pypi.io/packages/source/e/easybuild-framework/easybuild-framework-%{version}.tar.gz
Source3:   https://pypi.io/packages/source/v/vsc-base/vsc-base-%{vsc_base_ver}.tar.gz
Source4:   https://pypi.io/packages/source/v/vsc-install/vsc-install-%{vsc_install_ver}.tar.gz
Source5:   bootstrap_eb.py
Source6:   OHPC_macros
Source7:   easybuild-easyblocks_non-x86.patch
Source8:   bootstrap_eb.py-apply-patch.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: patch
BuildRequires: python
BuildRequires: python-setuptools
Requires: python
#!BuildIgnore: post-build-checks

# Lmod dependency (note that lmod is pre-populated in the OpenHPC OBS build
# environment; if building outside, lmod remains a formal build dependency).
%if !0%{?OHPC_BUILD}
BuildRequires: lmod%{PROJ_DELIM}
%endif

%define debug_package %{nil}

# Default library install path
%define install_path %{OHPC_LIBS}/%{pname}/%version

%description
EasyBuild is a software build and installation framework that allows 
you to manage (scientific) software on High Performance Computing (HPC) 
systems in an efficient way.

%prep
mkdir %{buildroot}

%build

cd %{buildroot}
cp %{_sourcedir}/*py .
%ifnarch x86_64
patch -p0 < %{_sourcedir}/bootstrap_eb.py-apply-patch.patch
%endif

export EASYBUILD_BOOTSTRAP_SKIP_STAGE0=1
export EASYBUILD_BOOTSTRAP_SOURCEPATH=%{_sourcedir}
export EASYBUILD_INSTALLPATH=%{install_path}
export EASYBUILD_VERSION=%{version}
export PATH=${LMOD_DIR}:${PATH}
export PYTHON_VERSION=`python -c 'print ".".join(map(str, __import__("sys").version_info[:2]))'`

python ./bootstrap_eb.py %{buildroot}/%{install_path}

%ifarch aarch64
rm %{buildroot}%{install_path}/modules/base/EasyBuild/%{version}
%endif
rm bootstrap_eb.py*


# OHPC module file
%{__mkdir} -p %{buildroot}%{OHPC_MODULES}/EasyBuild
%{__cat} << EOF > %{buildroot}/%{OHPC_MODULES}/EasyBuild/%{version}
#%Module1.0#####################################################################

proc ModulesHelp { } {

puts stderr " "
puts stderr "This module loads the %{pname} library built with the %{compiler_family} toolchain."
puts stderr "\nVersion %{version}\n"

}
module-whatis "Name: %{pname}"
module-whatis "Version: %{version}"
module-whatis "Category: system tool"
module-whatis "Description: %{summary}"
module-whatis "URL: http://hpcugent.github.com/easybuild/"

set             version                 %{version}
set             home                    \$::env(HOME)

prepend-path    PATH                    %{install_path}/software/EasyBuild/%{version}/bin
prepend-path    PATH                    ${LMOD_DIR}
prepend-path	LD_LIBRARY_PATH         %{install_path}/software/EasyBuild/%{version}/lib
prepend-path	LIBRARY_PATH            %{install_path}/software/EasyBuild/%{version}/lib
module          use                     \$home/.local/easybuild/modules/all

setenv          EBROOTEASYBUILD         %{install_path}/software/EasyBuild/%{version}
setenv          EBVERSIONEASYBUILD      %{version}
setenv          EASYBUILD_MODULES_TOOL  Lmod

prepend-path	PYTHONPATH	    %{install_path}/software/EasyBuild/%{version}/lib/python2.7/site-packages

EOF

%{__cat} << EOF > %{buildroot}/%{OHPC_MODULES}/EasyBuild/.version.%{version}
#%Module1.0#####################################################################
##
## version file for %{pname}-%{version}
##
set     ModulesVersion      "%{version}"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{OHPC_HOME}


%changelog

