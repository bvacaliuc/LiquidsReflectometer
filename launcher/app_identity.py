#!/usr/bin/python3
"""The launcher's QSettings identity, in one place.

Every settings layer — the per-tab UI preferences this slug persists, and the
reduction- and global-settings layers that follow — must resolve to the same
store. QSettings() derives its path from the QCoreApplication identity, so the
identity has to be established before the first QSettings is constructed. main()
does that for the GUI; tabs call ensure_identity() themselves so a non-GUI entry
point (a script, or a test constructing one tab) resolves the same store rather
than a nameless one.
"""

from qtpy import QtCore

ORG_NAME = "ORNL"
ORG_DOMAIN = "ornl.gov"
APP_NAME = "lr_reduction_new_launcher"

# The pre-identity store had no organization; these are the only keys it held
# that are worth carrying forward.
LEGACY_KEYS = ("overplot_folder", "overplot_xscale")


def ensure_identity():
    """Install the launcher identity if it is not already in place.

    Idempotent and non-clobbering: a test fixture that has installed its own
    throwaway organization keeps it, so calling this from a tab constructor is
    safe under an isolated QSettings root.
    """
    app = QtCore.QCoreApplication
    if app.organizationName() or app.applicationName():
        return
    app.setOrganizationName(ORG_NAME)
    app.setOrganizationDomain(ORG_DOMAIN)
    app.setApplicationName(APP_NAME)


def migrate_legacy_settings():
    """One-shot copy of the two pre-identity keys into the new store.

    Runs only when the new store has neither key, so it never overwrites a
    value the user has since set. Everything else starts fresh — stated in the
    PR body as the migration policy.
    """
    current = QtCore.QSettings()
    if any(current.contains(key) for key in LEGACY_KEYS):
        return
    app = QtCore.QCoreApplication
    org, domain, name = app.organizationName(), app.organizationDomain(), app.applicationName()
    app.setOrganizationName("")
    app.setOrganizationDomain("")
    app.setApplicationName("")
    try:
        legacy = QtCore.QSettings()
        carried = {key: legacy.value(key) for key in LEGACY_KEYS if legacy.contains(key)}
    finally:
        app.setOrganizationName(org)
        app.setOrganizationDomain(domain)
        app.setApplicationName(name)
    if not carried:
        return
    for key, value in carried.items():
        current.setValue(key, value)
    current.sync()
