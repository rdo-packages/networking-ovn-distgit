%global drv_vendor OVN
%global pkgname networking-ovn
%global srcname networking_ovn
%global docpath doc/build/html

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc 1

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

%package -n     python3-%{pkgname}
Summary:        %{drv_vendor} OpenStack Neutron driver
%{?python_provide:%python_provide python3-%{pkgname}}

BuildRequires:  git
BuildRequires:  python3-devel
BuildRequires:  python3-debtcollector
BuildRequires:  python3-mock
BuildRequires:  openstack-macros

# This is required to generate the networking-ovn.ini configuration file
BuildRequires:  python3-neutron

BuildRequires:  python3-oslo-config
BuildRequires:  python3-oslo-log
BuildRequires:  python3-ovsdbapp
BuildRequires:  python3-pbr

%if 0%{?with_doc}
BuildRequires:  python3-openstackdocstheme
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinxcontrib-rsvgconverter
%endif

# python-openvswitch is not included in openstack-neutron-common.
# Its needed by networking-ovn.
Requires:       openstack-neutron-common >= 1:13.0.0
Requires:       python3-babel >= 2.3.4
Requires:       python3-futurist >= 1.2.0
Requires:       python3-netaddr >= 0.7.18
Requires:       python3-neutron-lib >= 1.28.0
Requires:       python3-oslo-config >= 2:5.2.0
Requires:       python3-octavia-lib >= 1.3.1
Requires:       python3-openvswitch >= 2.8.0
Requires:       python3-pbr >= 2.0.0
Requires:       python3-six >= 1.10.0
Requires:       python3-tenacity >= 4.4.0
Requires:       python3-ovsdbapp >= 0.17.0
Requires:       python3-pyOpenSSL >= 17.1.0
Requires:       python3-requests >= 2.14.2
Requires:       python3-sqlalchemy >= 1.2.0
Requires:       python3-tooz >= 1.58.0

%description -n     python3-%{pkgname}
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains %{drv_vendor} networking driver which provides
integration between OpenStack Neutron and OVN.


%package -n     python3-%{pkgname}-metadata-agent
Summary:        networking-ovn metadata agent
%{?python_provide:%python_provide python3-%{pkgname}-metadata-agent}

BuildRequires:  systemd
Requires:       python3-%{pkgname} = %{version}-%{release}
Requires:       openvswitch >= 2.8.0
Requires:       haproxy >= 1.5.0
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description -n     python3-%{pkgname}-metadata-agent
OVN provides virtual networking for Open vSwitch and is a component of the
Open vSwitch project.

This package contains the agent that implements the metadata proxy so that VM's
can retrieve metadata from OpenStack Nova.

%package -n     python3-%{pkgname}-migration-tool
Summary:        networking-ovn ML2/OVS to OVN migration tool
%{?python_provide:%python_provide python3-%{pkgname}-migration-tool}

Requires:       python3-%{pkgname} = %{version}-%{release}

%description -n     python3-%{pkgname}-migration-tool
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
%{py3_build}

%if 0%{?with_doc}
sphinx-build-3 -b html doc/source %{docpath}
rm -rf %{docpath}/.{doctrees,buildinfo}
%endif

# Generate config file
PYTHONPATH=. oslo-config-generator-3 --namespace networking_ovn --output-file networking-ovn.ini
PYTHONPATH=. oslo-config-generator-3 --namespace networking_ovn.metadata.agent --output-file networking-ovn-metadata-agent.ini


%install
%{py3_install}

# Remove unused files
rm -rf %{buildroot}%{python3_sitelib}/bin
rm -rf %{buildroot}%{python3_sitelib}/doc
rm -rf %{buildroot}%{python3_sitelib}/tools


# Move config file to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
mv networking-ovn-metadata-agent.ini %{buildroot}%{_sysconfdir}/neutron/plugins/networking-ovn
chmod 640 %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini

# Create configuration directories for all services that can be populated by users with custom *.conf files
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/networking-ovn-metadata-agent

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/networking-ovn-metadata-agent.service

%post -n python3-%{pkgname}-metadata-agent
%systemd_post networking-ovn-metadata-agent.service


%preun -n python3-%{pkgname}-metadata-agent
%systemd_preun networking-ovn-metadata-agent.service


%postun -n python3-%{pkgname}-metadata-agent
%systemd_postun_with_restart networking-ovn-metadata-agent.service

%files -n python3-%{pkgname}
%license LICENSE
%if 0%{?with_doc}
%doc %{docpath}
%endif
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/%{srcname}-*.egg-info
%{_bindir}/neutron-ovn-db-sync-util
%dir %{_sysconfdir}/neutron/plugins/networking-ovn
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/networking-ovn.ini

%files -n python3-%{pkgname}-metadata-agent
%license LICENSE
%{_bindir}/networking-ovn-metadata-agent
%{_unitdir}/networking-ovn-metadata-agent.service
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/plugins/networking-ovn/networking-ovn-metadata-agent.ini
%dir %{_sysconfdir}/neutron/conf.d/networking-ovn-metadata-agent

%files -n python3-%{pkgname}-migration-tool
%license LICENSE
%{_bindir}/networking-ovn-migration-mtu
%{_bindir}/ovn_migration.sh
%{_datadir}/ansible/networking-ovn-migration/playbooks/

%changelog
