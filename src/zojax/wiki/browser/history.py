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
import cgi
from zope import interface, component
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL

from zojax.table.table import Table
from zojax.table.column import Column
from zojax.content.actions.action import Action
from zojax.formatter.utils import getFormatter
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.wiki.interfaces import IWikiPage, IHistory

from interfaces import _, IWikiPageHistoryAction


class WikiPageHistory(Action):
    component.adapts(IWikiPage, interface.Interface)
    interface.implements(IWikiPageHistoryAction)

    weight = 10
    title = _(u'History')
    permission = 'zope.View'

    @property
    def url(self):
        return '%s/history.html'%absoluteURL(self.context, self.request)


class WikiPageHistoryTable(Table):
    component.adapts(IHistory, interface.Interface, interface.Interface)

    title = u'Wiki Page History'

    cssClass = 'z-table'
    pageSize = 0
    enabledColumns = ('id', 'note', 'editor', 'date')
    msgEmptyTable = _('There are no any history records.')

    def initDataset(self):
        self.dataset = removeAllProxies(self.context).values()


class IdColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, WikiPageHistoryTable)

    name = 'id'
    title = u'Version'
    cssClass = u't-wiki-version'

    def update(self):
        self.url = u'%s/history.html?rev='%(
            absoluteURL(self.table.context.__parent__, self.request))

    def query(self, default=None):
        return self.content.__name__

    def render(self):
        return u'<a href="%s%s">%0.3d</a>'%(
            self.url, self.content.__name__, int(self.content.__name__))


class NoteColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, WikiPageHistoryTable)

    name = 'note'
    title = u'Note'
    cssClass = u't-wiki-note'

    def query(self, default=None):
        return self.content.note or u''

    def render(self):
        return cgi.escape(self.query())


class EditorColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, WikiPageHistoryTable)

    name = 'editor'
    title = _(u'Editor')

    def query(self, default=None):
        principal = self.content.getPrincipal()

        if principal is not None:
            request = self.request
            profile = IPersonalProfile(principal, None)
            if profile is not None:
                return profile.title
        else:
            return principal.title


class DateColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, WikiPageHistoryTable)

    name = 'date'
    title = _(u'Date')

    def query(self, default=None):
        fancyDatetime = getFormatter(self.request, 'fancyDatetime', 'medium')
        return fancyDatetime.format(self.content.date)


class HistoryView(object):

    diff = None
    revision = None

    def renderText(self):
        page = self.context
        wiki = page.__parent__
        request = self.request
        wikiURL = absoluteURL(wiki, request)

        html = u''
        for text in self.revision.cooked:
            html += text.render(wiki, page, request, wikiURL)

        return html

    def update(self):
        context = self.context
        request = self.request

        self.allowEdit = checkPermission('zojax.ModifyWikiContent', context)

        if 'returnToHistory' in request:
            return

        if 'revert' in request:
            rev = request.get('rev', u'')
            if rev not in context.history:
                IStatusMessage(request).add(_("Can't find revision."),'warning')
            else:
                revision = self.context.history[rev]
                revision.revert(request.principal.id)
                IStatusMessage(request).add(_('Wiki page has been reverted.'))
                self.redirect('index.html')
                return

        rev = request.get('rev', u'')
        history = context.history
        if rev in history:
            revId = int(rev)

            self.revId = revId+1
            self.revTotal = len(self.context.history)
            self.revision = self.context.history[rev]

            profile = IPersonalProfile(self.revision.getPrincipal(), None)
            self.principal = getattr(
                profile, 'title', _('Unknown')) or _('Unknown')

            if revId > 0:
                diff = []
                for line in history.diff(revId-1, revId):
                    if line[:2] in ('??', '--', '++'):
                        diff.append(
                            '<span class="wiki-diff-tag">%s</span>'%
                            cgi.escape(line[2:]))
                    elif line[:1] == '+':
                        diff.append(
                            '<span class="wiki-diff-added">%s</span>'%
                            cgi.escape(line[1:]))
                    elif line[:1] == '-':
                        diff.append(
                            '<span class="wiki-diff-removed">%s</span>'%
                            cgi.escape(line[1:]))

                self.diff = u'\n'.join(diff)
