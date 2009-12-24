##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import component
from zope.component import getUtility, queryAdapter
from zojax.catalog.interfaces import ICatalog
from zojax.content.space.interfaces import ISpace, IWorkspaceFactory
from zojax.content.permissions.permission import ContentPermission


class WikiPermission(ContentPermission):

    def isAvailable(self):
        wf = queryAdapter(self.context, IWorkspaceFactory, 'wiki')
        if wf is None or not self.context.isEnabled(wf):
            return

        return super(WikiPermission, self).isAvailable()
