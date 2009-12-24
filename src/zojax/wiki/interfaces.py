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
from zope import interface, schema
from zope.i18nmessageid import MessageFactory

from zojax.richtext.field import RichText
from zojax.content.type.interfaces import IItem, IContent
from zojax.content.space.interfaces import IWorkspace, IWorkspaceFactory

_ = MessageFactory('zojax.wiki')


class IWiki(IItem):
    """ Wiki """

    backlinks = interface.Attribute('Page backlinks.')

    maxOldLines = schema.Int(
        title = _(u'Old lines'),
        description = _(u'Maximum old lines to show.'),
        default = 40,
        required = True)

    maxNewLines = schema.Int(
        title = _(u'New lines'),
        description = _(u'Maximum new lines to show.'),
        default = 40,
        required = True)


class IWikiContents(interface.Interface):
    """ wiki contents """

    def relink(page, links):
        """ relink page """


class IWikiPage(interface.Interface):
    """ Wiki page """

    cooked = interface.Attribute('List of IWikiTextBlock objects')
    history = interface.Attribute('IHistory object')

    parent = interface.Attribute('Page parent')
    subtopics = interface.Attribute('List of page subtopics')
    backlinks = interface.Attribute('Page backlinks')

    title = schema.TextLine(
        title = _('Title'),
        description = _('Wiki page title.'),
        required = False)

    text = RichText(
        title = _(u'Page text'),
        description = _(u'Wiki page text.'),
        required = True)


class IWikiTextBlock(interface.Interface):
    """ formatted text block """

    def render(wiki, page, request):
        """ render text """


class IWikiWorkspace(IWiki, IWorkspace):
    """ wiki workspace """


class IWikiWorkspaceFactory(IWorkspaceFactory):
    """ wiki workspace factory """


class IRevision(interface.Interface):
    """ wiki page revision """

    title = interface.Attribute('Title')
    text = interface.Attribute('Text')
    format = interface.Attribute('Format')
    cooked = interface.Attribute('Cooked text')
    note = interface.Attribute('Note')
    principal = interface.Attribute('Principal')
    date = interface.Attribute('Date')

    def getPrincipal():
        """ return IPrincipal object """


class IHistory(interface.Interface):
    """ container for revisions """

    def add(revision, note, principal):
        """ add revision """

    def diff(revId1, revId2):
        """ generate diff for 2 revisions """
