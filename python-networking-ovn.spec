# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global drv_vendor OVN
%global pkgname networking-ovn
%global srcname networking_ovn
%global docpath doc/build/html

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pkgname}
Version:        XXX
Release:        XXX
Summary:        %{drv_vendor} OpenStack Neutron driver

License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pkgname}
Source0:        https://tarballs.openstack.org/%{pkgname}/%{pkgname}-%{upstream_version}.tar.gz
Source1:        networking-ovn-metadata-agent.service
#

BuildArch:      noarch

%description
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

%package -n     python%{pyver}-%{pkgname}
Summary:        %{drv_vendor} OpenStack Neutron driver
%{?python_provide:%python_provide python%{pyver}-%{pkgname}}

BuildRequires:  git
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-debtcollector
BuildRequires:  python%{pyver}-mock
BuildRequires:  openstack-macros

# This is required to generate the networking-ovn.ini configuration file
BuildRequires:  python%{pyver}-neutron

BuildRequires:  python%{pyver}-oslo-config
BuildRequires:  python%{pyver}-oslo-log
BuildRequires:  python%{pyver}-openstackdocstheme
BuildRequires:  python%{pyver}-ovsdbapp
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-sphinx


# python-openvswitch is not included in openstack-neutron-common.
# Its needed by networking-ovn.
Requires:       openstack-neutron-common
Requires:       python%{pyver}-babel
Requires:       python%{pyver}-futurist >= 1.2.0
Requires:       python%{pyver}-netaddr
Requires:       python%{pyver}-neutron-lib >= 1.18.0
Requires:       python%{pyver}-oslo-config >= 2:5.2.0
Requires:       python%{pyver}-openvswitch >= 2.8.0
Requires:       python%{pyver}-pbr
Requires:       python%{pyver}-six
Requires:       python%{pyver}-tenacity
Requires:       python%{pyver}-ovsdbapp >= 0.10.0
Requires:       python%{pyver}-pyOpenSSL >= 17.1.0
Requires:       python%{pyver}-sqlalchemy >= 1.2.0

%description -n     python%{pyver}-%{pkgname}
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains %{drv_vendor} networking driver which provides
integration between OpenStack Neutron and OVN.


%package metadata-agent
Summary:        networking-ovn metadata agent
BuildRequires:  systemd
Requires:       python%{pyver}-%{pkgname} = %{version}-%{release}
Requires:       openvswitch >= 2.8.0
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description metadata-agent
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains the agent that implements the metadata proxy so that VM's
can retrieve metadata from OpenStack Nova.

%package migration-tool
Summary:        networking-ovn ML2/OVS to OVN migration tool
Requires:       python%{pyver}-%{pkgname} = %{version}-%{release}

%description migration-tool
This package provides the necessary tools to update an existing ML2/OVS
OpenStack to OVN based backend.

%prep
%autosetup -n %{pkgname}-%{upstream_version} -S git

# Let's handle dependencies ourselves
%py_req_cleanup

# Kill egg-info in order to generate new SOURCES.txt
rm -rf {srcname}.egg-info


%build
export SKIP_PIP_INSTALL=1
%{pyver_build}
%{pyver_bin} setup.py build_sphinx
rm -rf %{docpath}/.{doctrees,buildinfo}

# Generate config file
PYTHONPATH=. oslo-config-generator-%{pyver} --namespace networking_ovn --output-file networking-ovn.ini
PYTHONPATH=. oslo-config-generator-%{pyver} --namespace networking_ovn.metadata.agent --output-file networking-ovn-metadata-agent.ini


%install
%{pyver_install}

# Remove unused files
rm -rf %{buildroot}%{pyver_sitelib}/bin
rm -rf %{buildroot}%{pyver_sitelib}/doc
rm -rf %{buildroot}%{pyver_sitelib}/tools


# Move config file to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn-metadata-agent.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
chmod 640 %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini

# Create configuration directories for all services that can be populated by users with custom *.conf files
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/networking-ovn-metadata-agent

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/networking-ovn-metadata-agent.service

%post metadata-agent
%systemd_post networking-ovn-metadata-agent.service


%preun metadata-agent
%systemd_preun networking-ovn-metadata-agent.service


%postun metadata-agent
%systemd_postun_with_restart networking-ovn-metadata-agent.service

%files -n     python%{pyver}-%{pkgname}
%license LICENSE
%doc %{docpath}
%{pyver_sitelib}/%{srcname}
%{pyver_sitelib}/%{srcname}-*.egg-info
%{_bindir}/neutron-ovn-db-sync-util
%dir %{_sysconfdir}/neutron/plugins/networking-ovn
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/networking-ovn.ini

%files metadata-agent
%license LICENSE
%{_bindir}/networking-ovn-metadata-agent
%{_unitdir}/networking-ovn-metadata-agent.service
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/networking-ovn-metadata-agent.ini
%dir %{_sysconfdir}/neutron/conf.d/networking-ovn-metadata-agent

%files migration-tool
%license LICENSE
%{_bindir}/networking-ovn-migration-mtu
%{_bindir}/ovn_migration.sh
%{_datadir}/ansible/networking-ovn-migration/playbooks/

%changelog
