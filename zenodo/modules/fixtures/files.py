# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""CLI for Zenodo fixtures."""

from __future__ import absolute_import, print_function

import hashlib
from os import makedirs, stat
from os.path import exists

from flask import current_app
from invenio_db import db
from invenio_files_rest.models import FileInstance, Location, ObjectVersion


def loadlocation(force=False):
    """Load default file store location."""
    try:
        uri = current_app.config['FIXTURES_FILES_LOCATION']
        if uri.startswith('/') and not exists(uri):
            makedirs(uri)
        loc = Location(name='default', uri=uri, default=True, )
        db.session.add(loc)
        db.session.commit()
        return loc
    except Exception:
        db.session.rollback()
        raise


def loaddemofiles(source, force=False):
    """Load demo files."""
    s = stat(source)

    with open(source, 'rb') as fp:
        m = hashlib.md5()
        m.update(fp.read())
        checksum = "md5:{0}".format(m.hexdigest())

    # Create a file instance
    with db.session.begin_nested():
        f = FileInstance.create()
        f.set_uri(source, s.st_size, checksum)

    # Replace all objects associated files.
    ObjectVersion.query.update({ObjectVersion.file_id: str(f.id)})
    db.session.commit()
