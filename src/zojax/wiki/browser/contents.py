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
from zojax.wiki.interfaces import _, IWikiPage
from zojax.wiki.browser.interfaces import IWikiContentsAction


class WikiContentsAction(Action):
    component.adapts(IWikiPage, interface.Interface)
    interface.implements(IWikiContentsAction)

    weight = 8
    title = _(u'Wiki contents')
    permission = 'zope.View'

    @property
    def url(self):
        return '%s/contents.html'%absoluteURL(self.context, self.request)


class WikiContents(object):

    def processPage(self, page):
        info = {'url': u'%s/%s/'%(self.wikiURL, page.__name__),
                'title': page.title,
                'current': page.__name__ == self.context.__name__,
                'subtopics': []}

        subtopics = []
        for link in removeAllProxies(page).subtopics:
            subtopics.append((link.title, link))
        subtopics.sort()

        for _t, topic in subtopics:
            info['subtopics'].append(self.processPage(topic))

        return info

    def update(self):
        wiki = self.context.__parent__
        self.wikiURL = absoluteURL(wiki, self.request)

        self.data = [self.processPage(wiki['FrontPage'])]
