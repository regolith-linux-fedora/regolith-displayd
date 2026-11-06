# Source1 is not in the repository. ext-rpm.sh makes it on the runner while it
# builds the SRPM, with `cargo vendor --locked` against Cargo.lock, so COPR
# builds offline from the SRPM.

Name:           regolith-displayd
Version:        0.3.4
Release:        1%{?dist}
Summary:        Display configuration daemon for the GNOME Settings Displays panel on sway
# regolith-displayd is Apache-2.0 (debian/copyright; its Cargo.toml names no
# license, the blank line in the summary). The rest covers the vendored crates:
# update it from the %%{cargo_license_summary} output in the build log whenever
# Cargo.lock changes.
License:        Apache-2.0 AND BSD-3-Clause AND MIT AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND (MIT OR Apache-2.0 OR BSD-2-Clause) AND (Unlicense OR MIT)
URL:            https://github.com/regolith-linux/regolith-displayd
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  systemd-rpm-macros

Requires:       kanshi
# Not in debian/control: the daemon runs `killall kanshi` to reload kanshi.
# Ubuntu installs psmisc by default; Fedora doesn't.
Requires:       /usr/bin/killall
# Debian recommends gnome-control-center; on Fedora Regolith's own settings
# app comes first.
Recommends:     (regolith-control-center or gnome-control-center)

%description
A daemon that implements Mutter's display configuration D-Bus interface for
sway, so the Displays panel of the settings app works in a sway session. A
second user unit runs the output profile manager with the profiles the
daemon writes.

%prep
%autosetup -a1
%cargo_prep -v vendor

%build
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
# The crate has a library target (src/lib.rs), so %%cargo_install would also
# install its sources under %%{_datadir}/cargo/registry. Install the binary.
install -Dpm 0755 target/rpm/regolith-displayd %{buildroot}%{_bindir}/regolith-displayd
install -Dpm 0755 regolith-displayd-init %{buildroot}%{_bindir}/regolith-displayd-init
install -Dpm 0644 data/regolith-init-displayd.service %{buildroot}%{_userunitdir}/regolith-init-displayd.service
install -Dpm 0644 data/regolith-init-kanshi.service %{buildroot}%{_userunitdir}/regolith-init-kanshi.service
# Debian's postinst (dh_installsystemduser) runs `deb-systemd-helper --user
# enable regolith-init-displayd.service`, which links it into
# regolith-wayland.target.wants for every user. A user preset does the same
# through %%systemd_user_post. The kanshi unit has no [Install] section; the
# displayd unit pulls it in with Requires=.
install -d %{buildroot}%{_userpresetdir}
echo "enable regolith-init-displayd.service" > %{buildroot}%{_userpresetdir}/90-regolith-displayd.preset

%check
%cargo_test

%post
%systemd_user_post regolith-init-displayd.service regolith-init-kanshi.service

%preun
%systemd_user_preun regolith-init-displayd.service regolith-init-kanshi.service

%postun
%systemd_user_postun regolith-init-displayd.service regolith-init-kanshi.service

%files
%license LICENSE.dependencies cargo-vendor.txt
%doc README.md
%{_bindir}/regolith-displayd
%{_bindir}/regolith-displayd-init
%{_userunitdir}/regolith-init-displayd.service
%{_userunitdir}/regolith-init-kanshi.service
%{_userpresetdir}/90-regolith-displayd.preset

%changelog
* Fri Nov 06 2026 Regolith Fedora Port <port@regolith.invalid> - 0.3.4-1
- Initial package
