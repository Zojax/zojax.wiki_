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
from zope import schema, interface
from zojax.portlet.interfaces import _ as pMsg
from zojax.portlet.interfaces import \
    IPortletManagerWithStatus, ENABLED, statusVocabulary


class IWikiRightPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = ('portlet.actions', 'portlet.activity',),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)


class IWikiLeftPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = (),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)
