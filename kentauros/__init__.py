"""
kentauros is an automated build system.

at the moment, the following actions are supported:

* getting source code from:

  * local tarball
  * tarball at URL
  * git repository
  * bzr repository

* building source packages:

  * RPM format (.spec necessary, but in theory an unmodified spec should work)

* building binary packages:

  * RPM format (mock necessary)

* uploading source packages to cloud build service:

  * copr for fedora and RHEL/EPEL packages
"""
