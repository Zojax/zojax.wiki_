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
import re
from rwproperty import setproperty, getproperty

from zope import interface, component
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import ICMFDublinCore
from zope.app.security.interfaces import IAuthentication

from z3c.form.widget import FieldWidget

from zojax.layoutform import Fields
from zojax.wizard.interfaces import ISaveable
from zojax.wizard import WizardStepForm
from zojax.richtext.widget import DefaultRichTextWidget
from zojax.content.forms.interfaces import IContentStep
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.wiki.interfaces import _, IWikiPage
from zojax.wiki.revision import History, Revision
from zojax.wiki.browser.interfaces import INote, IParent


class WikiPage(object):

    def renderText(self):
        page = self.context
        wiki = page.__parent__
        request = self.request

        wikiURL = absoluteURL(wiki, request)

        html = u''
        for text in page.cooked:
            html += text.render(wiki, page, request, wikiURL)

        return html


class WikiPageByline(object):

    author = None
    space = None
    principal = None

    def update(self):
        history = self.context.history
        lenhistory = len(history)

        if lenhistory:
            revision = history[len(history)-1]

            self.date = revision.date
            self.principal = revision.getPrincipal()
        else:
            dc = ICMFDublinCore(self.context)
            self.date = dc.modified
            try:
                self.principal = getUtility(IAuthentication).getPrincipal(
                    dc.creators[0])
            except:
                raise

        profile = IPersonalProfile(self.principal, None)
        if profile is not None:
            self.author = profile.title

            space = profile.space
            if space is not None:
                self.space = '%s/'%absoluteURL(space, self.request)


def customWidget(field, request):
    return FieldWidget(field, DefaultRichTextWidget(request))


class EditWikiPage(WizardStepForm):
    interface.implements(ISaveable, IContentStep)

    name = 'content'
    title = _('Content')
    label = _('Modify Wiki Page')

    fields = Fields(IWikiPage, INote)
    fields['text'].widgetFactory = customWidget

    def applyChanges(self, data):
        request = self.request
        content = removeAllProxies(self.getContent())
        revision = Revision(
            content.title, content.text.text,
            content.text.format, content.cooked)

        changes = super(EditWikiPage, self).applyChanges(data)

        if IWikiPage in changes:
            content.history.add(revision, data['note'], request.principal.id)

        return changes


class EditWikiPageParent(WizardStepForm):
    interface.implements(ISaveable)

    name = 'parent'
    title = _('Parent')
    label = _('Change wiki page parent')

    fields = Fields(IParent)

    def isAvailable(self):
        if self.context.__name__ == u'FrontPage':
            return False
        return super(EditWikiPageParent, self).isAvailable()


class WikiPageNote(object):
    component.adapts(IWikiPage)
    interface.implements(INote)

    note = u''

    def __init__(self, context):
        self.context = context


class WikiPageParent(object):
    component.adapts(IWikiPage)
    interface.implements(IParent)

    def __init__(self, context):
        self.context = context

    @getproperty
    def parent(self):
        return self.context.parent

    @setproperty
    def parent(self, parent):
        self.context.parent = parent
