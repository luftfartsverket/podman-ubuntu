%%{!?ldconfig_scriptlets:%global ldconfig_scriptlets() %nil}

%if "%{_vendor}" == "debbuild"
#%define go_bin go
%define go_bin /usr/lib/go-1.23/bin/go
%global go_bin /usr/lib/go-1.23/bin/go

%global _unitdir %{_usr}/lib/systemd/system
%global _userunitdir %{_usr}/lib/systemd/user
%global _tmpfilesdir %{_usr}/lib/tmpfiles.d
%global _systemdgeneratordir %{_prefix}/lib/systemd/system-generators
%global _systemdusergeneratordir %{_prefix}/lib/systemd/user-generators
%define gobuild(o:) GO111MODULE=off %{go_bin} build -buildmode pie -tags=" ${BUILDTAGS:-}" -a -v -x %{?**};
%endif

%global with_debug 1


%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%global provider github
%global provider_tld com
%global project containers
%global repo %{name}
# https://github.com/containers/%%{name}
%global import_path %{provider}.%{provider_tld}/%{project}/%{repo}
%global git0 https://%{import_path}

# dnsname
%global repo_plugins dnsname
# https://github.com/containers/dnsname
%global import_path_plugins %{provider}.%{provider_tld}/%{project}/%{repo_plugins}
%global git_plugins https://%{import_path_plugins}
%global commit_plugins 18822f9a4fb35d1349eb256f4cd2bfd372474d84

# gvproxy
%global repo_gvproxy gvisor-tap-vsock
# https://github.com/containers/gvisor-tap-vsock
%global import_path_gvproxy %%{provider}.%{provider_tld}/%{project}/%{repo_gvproxy}
%global git_gvproxy https://%{import_path_gvproxy}
# select gvisor-tap-vsock version depending on default golang version available on the system.
# still need to include the source code for all versions; unconditionally downloaded below.
# remove conditional when gvisor-tap-vsock's golang version requirements align across supported systems.
%global commit_gvproxy062 9b06a0431d8906868b1962167d4aa90690eed51d
%global commit_gvproxy073 c62637db4d1417408b84340cbe993843a4984b92
# debbuild seems to report debian 13 (trixie/unstable) as version 12 (bookworm/stable); fix the range when debbuild/obs does.
%if 0%{?debian_version} >= 1200 || 0%{?ubuntu_version} >= 2300
%global commit_gvproxy %{commit_gvproxy073}
%else
%global commit_gvproxy %{commit_gvproxy062}
%endif

%global built_tag_strip 5.5.2

Name: podman
Epoch: 4
Version: %{built_tag_strip}
Packager: Podman Debbuild Maintainers <https://github.com/orgs/containers/teams/podman-debbuild-maintainers>
License: Apache-2.0 and BSD-2-Clause and BSD-3-Clause and ISC and MIT and MPL-2.0
Release: 9003~lfv+%{?dist}
Summary: Manage Pods, Containers and Container Images
URL: https://%{name}.io/
Source0: %{git0}/archive/v%{built_tag_strip}.tar.gz
Source1: %{git_plugins}/archive/%{commit_plugins}/%{repo_plugins}-%{commit_plugins}.tar.gz
# download all versions in use; revert when only downloading a single version.
Source2: %{git_gvproxy}/archive/%{commit_gvproxy062}/%{repo_gvproxy}-%{commit_gvproxy062}.tar.gz
Source3: %{git_gvproxy}/archive/%{commit_gvproxy073}/%{repo_gvproxy}-%{commit_gvproxy073}.tar.gz
Provides: %{name}-manpages = %{epoch}:%{version}-%{release}
BuildRequires: go-md2man
BuildRequires: libbtrfs-dev
Requires: catatonit
Requires: iptables
Requires: nftables
%if "%{_vendor}" == "debbuild"
BuildRequires: libsqlite3-dev
BuildRequires: git
BuildRequires: libassuan-dev
BuildRequires: libglib2.0-dev
BuildRequires: libgpg-error-dev
BuildRequires: libgpgme-dev
BuildRequires: libseccomp-dev
BuildRequires: libsystemd-dev
BuildRequires: pkg-config
BuildRequires: golang-1.23-go
BuildRequires: libc6
BuildRequires: gettext-base
Requires: conmon
Requires: golang-github-containers-common
Requires: podman-gvproxy
Requires: slirp4netns
Requires: runc
Requires: uidmap
%endif
Recommends: %{name}-gvproxy = %{epoch}:%{version}-%{release}
Requires: netavark >= 1.0.3-1
Suggests: qemu-user-static

%description
%{name} (Pod Manager) is a fully featured container engine that is a simple
daemonless tool.  %{name} provides a Docker-CLI comparable command line that
eases the transition from other container engines and allows the management of
pods, containers and images.  Simply put: alias docker=%{name}.
Most %{name} commands can be run as a regular user, without requiring
additional privileges.

%{name} uses Buildah(1) internally to create container images.
Both tools share image (not container) storage, hence each can use or
manipulate images (but not containers) created by the other.

%{summary}
%{repo} Simple management tool for pods, containers and images

%package docker
Summary: Emulate Docker CLI using %{name}
BuildArch: noarch
Requires: %{name} = %{epoch}:%{version}-%{release}
Conflicts: docker
Conflicts: docker-latest
Conflicts: docker-ce
Conflicts: docker-ee
Conflicts: moby-engine

%description docker
This package installs a script named docker that emulates the Docker CLI by
executes %{name} commands, it also creates links between all Docker CLI man
pages and %{name}.

%package tests
Summary: Tests for %{name}

Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: bats
Requires: jq
Requires: skopeo
Requires: nmap-ncat
Requires: httpd-tools
Requires: openssl
Requires: socat
Requires: buildah
Requires: gnupg

%description tests
%{summary}

This package contains system tests for %{name}

%package remote
Summary: (Experimental) Remote client for managing %{name} containers

%description remote
Remote client for managing %{name} containers.

This experimental remote client is under heavy development. Please do not
run %{name}-remote in production.

%{name}-remote uses the version 2 API to connect to a %{name} client to
manage pods, containers and container images. %{name}-remote supports ssh
connections as well.

%package plugins
Summary: Plugins for %{name}
Requires: dnsmasq
Recommends: %{name}-gvproxy = %{epoch}:%{version}-%{release}

%description plugins
This plugin sets up the use of dnsmasq on a given CNI network so
that Pods can resolve each other by name.  When configured,
the pod and its IP address are added to a network specific hosts file
that dnsmasq will read in.  Similarly, when a pod
is removed from the network, it will remove the entry from the hosts
file.  Each CNI network will have its own dnsmasq instance.

%package gvproxy
Summary: Go replacement for libslirp and VPNKit

%description gvproxy
A replacement for libslirp and VPNKit, written in pure Go.
It is based on the network stack of gVisor. Compared to libslirp,
gvisor-tap-vsock brings a configurable DNS server and
dynamic port forwarding.

%prep
%autosetup -n %{name}-%{built_tag_strip}
sed -i 's;@@PODMAN@@\;$(BINDIR);@@PODMAN@@\;%{_bindir};' Makefile

# untar dnsname
tar zxf %{SOURCE1}

# untar %%{name}-gvproxy
# download all versions in use; revert when only downloading a single version.
tar zxf %{SOURCE2}
tar zxf %{SOURCE3}

%build
# Disable Go’s automatic toolchain download (needs Internet)
export GOTOOLCHAIN=local

export GOEXPERIMENT=rangefunc
export BUILDTAGS="goexperiment.rangefunc ${BUILDTAGS:-}"

export PATH=/usr/lib/go-1.23/bin:$PATH

export GOFLAGS='-p=2'
export GO111MODULE=off
export GOPATH=$(pwd)/_build:$(pwd)

mkdir _build
cd _build
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../../ src/%{import_path}
cd ..
ln -s vendor src

# build date. FIXME: Makefile uses '/v2/libpod', that doesn't work here?
LDFLAGS="-X %{import_path}/libpod/define.buildInfo=$(date +%s)"
LDFLAGS_PODMAN="-X %{import_path}/libpod/define.buildInfo=$(date +%s) -linkmode=external -buildid= -s -w"

# build rootlessport first
GO111MODULE=off go build -buildmode=pie -tags="${BUILDTAGS:-}" -ldflags "${LDFLAGS_PODMAN}" -a -v -x -o bin/rootlessport %{import_path}/cmd/rootlessport

# build %%{name}

export BUILDTAGS="seccomp exclude_graphdriver_devicemapper $(hack/btrfs_installed_tag.sh) $(hack/btrfs_tag.sh) $(hack/libdm_tag.sh)  $(hack/systemd_tag.sh) $(hack/libsubid_tag.sh)"

GO111MODULE=off go build -buildmode=pie -tags="${BUILDTAGS:-}" -ldflags "${LDFLAGS_PODMAN}" -a -v -x -o bin/%{name} %{import_path}/cmd/%{name}

# build %%{name}-remote
export BUILDTAGS="seccomp exclude_graphdriver_devicemapper exclude_graphdriver_btrfs btrfs_noversion  $(hack/systemd_tag.sh) $(hack/libsubid_tag.sh) remote"
GO111MODULE=off go build -buildmode=pie -tags="${BUILDTAGS:-}" -ldflags "${LDFLAGS_PODMAN}" -a -v -x -o bin/%{name}-remote %{import_path}/cmd/%{name}

# build quadlet
export BUILDTAGS="$BASEBUILDTAGS $(hack/btrfs_installed_tag.sh) $(hack/btrfs_tag.sh)"
GO111MODULE=off go build -buildmode=pie -tags="${BUILDTAGS:-}" -ldflags "${LDFLAGS_PODMAN}" -a -v -x -o bin/quadlet %{import_path}/cmd/quadlet

cd %{repo_plugins}-%{commit_plugins}
mkdir _build
cd _build
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../../ src/%{import_path_plugins}
cd ..
ln -s vendor src
export GOPATH=$(pwd)/_build:$(pwd)
GO111MODULE=off go build -buildmode=pie -tags="${BUILDTAGS:-}" -a -v -x -o bin/dnsname %{import_path_plugins}/plugins/meta/dnsname
cd ..

cd %{repo_gvproxy}-%{commit_gvproxy}
mkdir _build
cd _build
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../../ src/%{import_path_gvproxy}
cd ..
ln -s vendor src
export GOPATH=$(pwd)/_build:$(pwd)
GO111MODULE=off go build -buildmode=pie -tags="${BUILDTAGS:-}" -a -v -x -o bin/gvproxy %{import_path_gvproxy}/cmd/gvproxy
cd ..

export GO111MODULE=auto
%{__make} docs docker-docs

%install
# Disable Go’s automatic toolchain download (needs Internet)
export GOTOOLCHAIN=local
# Set custom path
export PATH=/usr/lib/go-1.23/bin:$PATH
install -dp %{buildroot}%{_unitdir}
PODMAN_VERSION=%{version} %{__make} PREFIX=%{buildroot}%{_prefix} ETCDIR=%{buildroot}%{_sysconfdir} \
       install.bin \
       install.man \
       install.systemd \
       install.completions \
       install.docker \
       install.docker-docs \
       install.remote

sed -i 's;%{buildroot};;g' %{buildroot}%{_bindir}/docker

# install dnsname plugin
cd %{repo_plugins}-%{commit_plugins}
%{__make} PREFIX=%{_prefix} DESTDIR=%{buildroot} install
cd ..

# install gvproxy
cd %{repo_gvproxy}-%{commit_gvproxy}
install -dp %{buildroot}%{_libexecdir}/%{name}
install -p -m0755 bin/gvproxy %{buildroot}%{_libexecdir}/%{name}
cd ..

# do not include docker and podman-remote man pages in main package
for file in `find %{buildroot}%{_mandir}/man[15] -type f | sed "s,%{buildroot},," | grep -v -e remote -e docker`; do
    echo "$file*" >> podman.file-list
done

rm -f %{buildroot}%{_mandir}/man5/docker*.5

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

# PACKIT PACKIT PACKIT PACKIT PACKIT PACKIT PACKIT PACKIT PACKIT PACKIT
# These files will be installed by unreleased versions of %%{name} and upstream is
# not comfy with a patch using packit's fix-spec-files action so let's remove the file here.
# The packager will need to revisit this section on every upstream release.
# See: https://github.com/containers/podman/pull/15457#discussion_r955423853
rm -f %{buildroot}%{_datadir}/user-tmpfiles.d/%{name}-docker.conf

%files -f %{name}.file-list
%license LICENSE
%doc README.md CONTRIBUTING.md install.md transfer.md
%{_bindir}/%{name}
%{_bindir}/%{name}sh
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/rootlessport
%{_libexecdir}/%{name}/quadlet
%{_datadir}/bash-completion/completions/%{name}
# By "owning" the site-functions dir, we don't need to Require zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_%{name}
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/%{name}.fish
%{_unitdir}/%{name}*
%{_userunitdir}/%{name}*
%{_tmpfilesdir}/%{name}.conf
%{_systemdgeneratordir}/%{name}-system-generator
%{_systemdusergeneratordir}/%{name}-user-generator
%{_modulesloaddir}/%{name}-iptables.conf

%files docker
%{_bindir}/docker
%{_mandir}/man1/docker*.1*
%{_tmpfilesdir}/%{name}-docker.conf

%files remote
%license LICENSE
%{_bindir}/%{name}-remote
%{_mandir}/man1/%{name}-remote*.*
%{_datadir}/bash-completion/completions/%{name}-remote
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/%{name}-remote.fish
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_%{name}-remote

%files plugins
%license %{repo_plugins}-%{commit_plugins}/LICENSE
%doc %{repo_plugins}-%{commit_plugins}/{README.md,README_PODMAN.md}
%dir %{_libexecdir}/cni
%{_libexecdir}/cni/dnsname

%files gvproxy
%license %{repo_gvproxy}-%{commit_gvproxy}/LICENSE
%doc %{repo_gvproxy}-%{commit_gvproxy}/README.md
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/gvproxy

%changelog
