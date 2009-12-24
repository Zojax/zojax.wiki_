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
from zope import interface, event
from zope.location import Location
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectCreatedEvent
from zojax.layoutform import interfaces, button, Fields, PageletForm
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.wiki.interfaces import _, IWikiPage
from zojax.wiki.wikipage import WikiPage
from zojax.wiki.browser.wikipage import customWidget
from zojax.wiki.browser.interfaces import IEmptyWikiPage


class EmptyWikiPage(Location):
    interface.implements(IEmptyWikiPage)

    def __init__(self, name, context, request):
        self.__name__ = name
        self.__parent__ = context


class EmptyWikiPageForm(PageletForm):

    allow = True
    fields = Fields(IWikiPage)
    fields['text'].widgetFactory = customWidget

    def label(self):
        return _('Wiki Page: ${name}',
                 mapping={'name': self.context.__name__})

    def getContent(self):
        return {'title': self.context.__name__,
                'text': u''}

    @button.buttonAndHandler(_('Create'), name='create',
                             provides=interfaces.IAddButton)
    def createHandler(self, action):
        data, errors = self.extractData()

        if errors:
            IStatusMessage(self.request).add(
                (self.formErrorsMessage,) + errors, 'formError')
        else:
            page = WikiPage(title=data['title'])
            page.text = data['text']
            event.notify(ObjectCreatedEvent(page))

            wiki = self.context.__parent__
            try:
                wiki[self.context.__name__] = page
                page.parent = wiki.get(self.request.get('parent', ''))
                IStatusMessage(self.request).add(_('Wiki page has been added.'))
            except Exception, err:
                IStatusMessage(self.request).add(err, 'error')
                return

            self.redirect('.')

    @button.buttonAndHandler(_('Cancel'), name='cancel',
                             provides=interfaces.ICancelButton)
    def cancelHandler(self, action):
        parent = self.request.get('parent', '')
        self.redirect(
            u'%s/%s/'%(
                absoluteURL(self.context.__parent__, self.request), parent))

    def update(self):
        if checkPermission('zojax.ModifyWikiContent', self.context.__parent__):
            super(EmptyWikiPageForm, self).update()
        else:
            self.allow = False
