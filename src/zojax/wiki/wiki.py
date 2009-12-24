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
from BTrees.OOBTree import OOBTree, OOTreeSet

from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.schema.fieldproperty import FieldProperty
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.intid.interfaces import IIntIdAddedEvent
from zojax.content.type.container import ContentContainer
from zojax.content.type.interfaces import IRenameNotAllowed
from zojax.content.type.interfaces import IUnremoveableContent

from wikipage import WikiPage
from interfaces import IWiki, IWikiContents


class BaseWiki(ContentContainer):
    interface.implements(IWiki, IWikiContents)

    maxOldLines = FieldProperty(IWiki['maxOldLines'])
    maxNewLines = FieldProperty(IWiki['maxNewLines'])

    parents = {}
    links = {}
    backlinks = {}

    def __init__(self, *args, **kw):
        super(BaseWiki, self).__init__(*args, **kw)

        self.links = OOBTree()
        self.backlinks = OOBTree()

    def relink(self, page, links):
        for link in self.links.get(page, ()):
            oldlinks = self.backlinks[link]
            oldlinks.remove(page)
            if not oldlinks:
                del self.backlinks[link]

        self.links[page] = OOTreeSet(links)

        for link in links:
            data = self.backlinks.get(link)
            if data is None:
                data = OOTreeSet()
                self.backlinks[link] = data
            data.insert(page)

    def __delitem__(self, key):
        # remove backlinks
        if key in self.links:
            for link in self.links[key]:
                oldlinks = self.backlinks[link]
                oldlinks.remove(key)
                if not oldlinks:
                    del self.backlinks[link]
            del self.links[key]

        super(BaseWiki, self).__delitem__(key)


class Wiki(BaseWiki):
    """ wiki """


@component.adapter(IWiki, IIntIdAddedEvent)
def wikiCreated(wiki, ev):
    if u'FrontPage' not in wiki:
        page = WikiPage(title=u'FrontPage')
        page.text = u'This is FrontPage of the Wiki.'
        event.notify(ObjectCreatedEvent(page))
        wiki['FrontPage'] = page

        interface.alsoProvides(page, IRenameNotAllowed, IUnremoveableContent)
