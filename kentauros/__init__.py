"""
kentauros is an automatable build system.
at the moment, the following is supported:

* getting source code from:

  * local tarball
  * tarball at URL
  * git repository
  * bzr repository

* building source packages:

  * RPM format (.spec neccessary, but in theory an unmodified spec should work)

* building binary packages:

  * RPM format (mock neccessary)

* uploading source packages to cloud build service:

  * copr for fedora and rhel/epel packages
"""

