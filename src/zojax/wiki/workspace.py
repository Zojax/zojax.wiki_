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
from zope import interface, component
from zojax.content.space.interfaces import IContentSpace
from zojax.content.space.workspace import WorkspaceFactory

from wiki import BaseWiki
from interfaces import _, IWikiWorkspace, IWikiWorkspaceFactory


class WikiWorkspace(BaseWiki):
    interface.implements(IWikiWorkspace)

    @property
    def space(self):
        return self.__parent__


class WikiWorkspaceFactory(WorkspaceFactory):
    component.adapts(IContentSpace)
    interface.implements(IWikiWorkspaceFactory)

    name = 'wiki'
    description = _(u'Space wiki.')
    weight = 2000
    factory = WikiWorkspace

    @property
    def title(self):
        if self.isInstalled():
            return self.space['wiki'].title
        else:
            return _(u'Wiki')
