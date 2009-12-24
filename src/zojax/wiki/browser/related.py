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
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL

from zojax.content.actions.action import Action
from zojax.wiki.interfaces import IWikiPage, IHistory

from interfaces import _, IRelatedPagesAction


class RelatedPagesAction(Action):
    component.adapts(IWikiPage, interface.Interface)
    interface.implements(IRelatedPagesAction)

    weight = 9
    title = _(u'Related pages')
    permission = 'zope.View'

    @property
    def url(self):
        return '%s/relatedpages.html'%absoluteURL(self.context, self.request)


class RelatedPages(object):

    def update(self):
        wiki = self.context.__parent__
        context = self.context

        self.parent = context.parent

        backlinks = []
        for link in context.backlinks:
            if link in wiki:
                link = wiki[link]
                backlinks.append((link.title, link))
        backlinks.sort()
        self.backlinks = [link for _t, link in backlinks]

        subtopics = []
        for link in removeAllProxies(context).subtopics:
            subtopics.append((link.title, link))
        subtopics.sort()
        self.subtopics = [link for _t, link in subtopics]
