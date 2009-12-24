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
from BTrees.OOBTree import OOTreeSet
from rwproperty import getproperty, setproperty

from zope import interface, component
from zope.proxy import removeAllProxies, sameProxiedObjects
from zope.app.container.interfaces import IObjectMovedEvent

from zojax.content.type.item import PersistentItem
from zojax.content.type.searchable import ContentSearchableText
from zojax.richtext.field import RichTextProperty
from zojax.richtext.interfaces import IRichTextDataModified

from revision import History
from format import parse, WikiLinkBlock
from interfaces import IWiki, IWikiPage


class WikiPage(PersistentItem):
    interface.implements(IWikiPage)

    cooked = []
    text = RichTextProperty(IWikiPage['text'])

    subtopics = []

    def __init__(self, *args, **kw):
        super(WikiPage, self).__init__(*args, **kw)
        self.history = History(self)
        self.subtopics = OOTreeSet()

    def cook(self):
        if not self.text:
            return

        self.cooked = parse(self.text.cooked)

        wiki = self.__parent__
        if IWiki.providedBy(wiki):
            name = self.__name__
            links = [block.name for block in self.cooked
                     if isinstance(block, WikiLinkBlock) and block.name!=name]

            wiki.relink(name, links)

    @getproperty
    def parent(self):
        return self.__dict__.get('parent')

    @setproperty
    def parent(self, parent):
        parent = removeAllProxies(parent)
        if parent is not None and self.__name__ == parent.__name__:
            return

        oldparent = self.parent
        if oldparent is not None and (self in oldparent.subtopics):
            oldparent.subtopics.remove(self)

        if parent is not None:
            self.__dict__['parent'] = parent
            parent.subtopics.insert(self)
        else:
            if oldparent is None:
                oldparent = self.__parent__[u'FrontPage']

            for subtopic in tuple(self.subtopics):
                subtopic.parent = oldparent

    @property
    def backlinks(self):
        return tuple(self.__parent__.backlinks.get(self.__name__, ()))


@component.adapter(IWikiPage, IRichTextDataModified)
def wikipageChanged(page, ev):
    page.cook()


@component.adapter(IWikiPage, IObjectMovedEvent)
def wikipageMovedHandler(page, ev):
    if ev.oldParent is None:
        # add
        if page.parent == None and page.__name__ != 'FrontPage':
            page.parent = page.__parent__[u'FrontPage']
        page.cook()
        return

    elif ev.oldParent is not None and ev.newParent is not None:
        page.cook()
        return

    page.parent = None


class WikiPageSearchableText(ContentSearchableText):
    component.adapts(IWikiPage)

    def getSearchableText(self):
        return super(WikiPageSearchableText, self).getSearchableText() + \
            u' ' + self.content.text.text
