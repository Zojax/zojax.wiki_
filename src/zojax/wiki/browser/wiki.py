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
from zope import component, interface, event, schema
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.container.interfaces import INameChooser

from zojax.richtext.field import RichText
from zojax.content.actions.action import Action
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.layoutform import interfaces, button, Fields, PageletForm

from zojax.wiki.format import generateWikiName
from zojax.wiki.interfaces import _, IWiki, IWikiPage
from zojax.wiki.wikipage import WikiPage
from zojax.wiki.browser.empty import EmptyWikiPage
from zojax.wiki.browser.wikipage import customWidget
from zojax.wiki.browser.interfaces import IManageWikiAction, IAddWikiPageAction


class WikiPublisher(object):
    interface.implements(IBrowserPublisher)
    component.adapts(IWiki, interface.Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        context = self.context

        if name in context:
            return context[name]

        view = queryMultiAdapter((context, request), name=name)
        if view is not None:
            return view

        try:
            if INameChooser(context).checkName(name, WikiPage()):
                return EmptyWikiPage(name, context, request)
        except:
            pass

        raise NotFound(self.context, name, request)

    def browserDefault(self, request):
        return self.context, ('FrontPage',)


class ManageWiki(Action):
    component.adapts(IWikiPage, interface.Interface)
    interface.implements(IManageWikiAction)

    weight = 6
    title = _(u'Manage Wiki')
    contextInterface = IWiki
    permission = 'zojax.ModifyContent'

    @property
    def url(self):
        return '%s/context.html'%absoluteURL(self.context, self.request)


class AddWikiPageAction(Action):
    component.adapts(IWikiPage, interface.Interface)
    interface.implements(IAddWikiPageAction)

    weight = 10
    title = _(u'Add Wiki Page')
    contextInterface = IWiki
    permission = 'zojax.ModifyWikiContent'

    @property
    def url(self):
        return '%s/addwikipage.html'%absoluteURL(self.context, self.request)


class IAddWikiPage(interface.Interface):

    title = schema.TextLine(
        title = _('Title'),
        description = _('Wiki page title.'),
        required = True)

    text = RichText(
        title = _(u'Page text'),
        description = _(u'Wiki page text.'),
        required = True)


class AddWikiPageForm(PageletForm):

    label = _('Add Wiki Page')
    fields = Fields(IAddWikiPage)
    fields['text'].widgetFactory = customWidget
    ignoreContext = True

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

            name = generateWikiName(data['title'])

            wiki = self.context
            try:
                wiki[name] = page
                page.parent = wiki['FrontPage']
                IStatusMessage(self.request).add(_('Wiki page has been added.'))
                self.redirect(u'%s/'%name)
            except Exception, err:
                IStatusMessage(self.request).add(err, 'error')

    @button.buttonAndHandler(_('Cancel'), name='cancel',
                             provides=interfaces.ICancelButton)
    def cancelHandler(self, action):
        self.redirect(u'./')
