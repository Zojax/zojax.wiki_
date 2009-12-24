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
from zope import interface
from zope.proxy import removeAllProxies
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from interfaces import IWiki

empty = SimpleVocabulary(())

def wikiPagesVocabulary(context):
    currentPage = context.__name__

    while not IWiki.providedBy(context):
        context = context.__parent__
        if context is None:
            return empty

    def addWikiPage(page, terms):
        terms.append(SimpleTerm(page, page.__name__, page.title))

        pages = [(page.title, page.__name__, page)
                 for page in page.subtopics if page.__name__ != currentPage]
        pages.sort()
        for _t,_n, page in pages:
            addWikiPage(page, terms)

    context = removeAllProxies(context)

    terms = []
    addWikiPage(context['FrontPage'], terms)

    return SimpleVocabulary(terms)
