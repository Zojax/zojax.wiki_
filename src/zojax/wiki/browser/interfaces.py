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
from zojax.wiki.interfaces import _
from zojax.widget.radio.field import RadioChoice
from zojax.content.actions.interfaces import IAction, IManageContentCategory


class IEmptyWikiPage(interface.Interface):
    """ empty wiki page """


class INote(interface.Interface):
    """ note """

    note = schema.Text(
        title = _(u'Modification Note'),
        default = u'',
        required = False)


class IParent(interface.Interface):
    """ parent """

    parent = RadioChoice(
        title = _(u'Parent'),
        description = _(u'Select parent for wiki page.'),
        vocabulary = 'zojax.wiki.pages',
        required = True)


class IManageWikiAction(IAction, IManageContentCategory):
    """ manage wiki """


class IAddWikiPageAction(IAction, IManageContentCategory):
    """ add wiki page action """


class IWikiPageHistoryAction(IAction):
    """ wiki history """


class IRelatedPagesAction(IAction):
    """ related pages """


class IWikiContentsAction(IAction):
    """ wiki contents """
