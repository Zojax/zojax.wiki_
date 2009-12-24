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
from urllib import quote
from zope import interface

from interfaces import IWikiTextBlock

urlchars = u'[A-Za-z0-9/:@_%~#=&\.\-\?\+\$,]+'
urlendchar  = u'[A-Za-z0-9/]'
url_re = u'["=]?((http|https|ftp|mailto):%s)'%urlchars
url = re.compile(url_re)

bracketedexpr_re = u'\[([^\n\]]+)\]'
bracketedexpr = re.compile(bracketedexpr_re)
protectedLine = re.compile(u'(?m)^!(.*)$')

U = u'A-Z\xc0-\xdf'
L = u'a-z\xe0-\xff'
b = u'(?<![%s0-9])' % (U + L)
wikiname1 = u'(?L)%s[%s]+[%s]+[%s][%s]*[0-9]*' % (b, U, L, U, U + L)
wikiname2 = u'(?L)%s[%s][%s]+[%s][%s]*[0-9]*'  % (b, U, U, L, U + L)
wikilink  = re.compile(u'!?(%s|%s|%s|%s)' %
            (wikiname1, wikiname2, bracketedexpr_re, url_re))
localwikilink = u'!?(%s|%s|%s)' % (wikiname1, wikiname2, bracketedexpr_re)
interwikilink = re.compile(u'!?((?P<local>%s):(?P<remote>%s))' %
                (localwikilink, urlchars + urlendchar))

allowedChars = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'

def generateWikiName(name):
    _name = u''
    for ch in name:
        if ch not in allowedChars:
            _name += ' '
        else:
            _name += ch

    _name = _name.split(u' ')
    if len(_name) > 1:
        _name = [n.strip().capitalize() for n in _name]

    return u''.join(_name)


class Block(object):
    interface.implements(IWikiTextBlock)

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return u"<%s %s>"%(
            self.__class__.__name__, repr(self.text))

    def render(self, wiki, page, request, wikiURL='..'):
        return self.text


class TextBlock(Block):

    def merge(self, text):
        self.text = self.text + text


class WikiLinkBlock(Block):
    """ a wiki name """

    def __init__(self, text):
        if bracketedexpr.match(text):
            name = text[1:-1]
            self.text = text[1:-1]
        else:
            name = text
            self.text = text

        self.name = generateWikiName(name)

    def render(self, wiki, page, request, wikiURL='..'):
        # if a page (or something) of this name exists, link to it
        if self.name in wiki:
            return u'<a href="%s/%s/">%s</a>' % (
                wikiURL, quote(self.name), self.text)

        # otherwise, provide a "?" creation link
        else:
            return u'%s<a href="%s/%s/?parent=%s">?</a>' %(
                self.text, wikiURL, quote(self.name), page.__name__)


class URLBlock(Block):

    def __init__(self, text):
        protocol, text = text.split(':', 1)
        self.protocol = protocol
        self.text = text

    def render(self, wiki, page, request, wikiURL='..'):
        if self.protocol == 'mailto':
            return u'<a href="%s:%s">%s</a>'%(
                self.protocol, quote(self.text), self.text)
        else:
            return u'<a href="%s://%s">%s</a>'%(
                self.protocol, quote(self.text), self.text)


def parse(text, urls=1):
    markedtext = []
    state = {'lastend':0,'inpre':0,'incode':0,'intag':0,'inanchor':0}
    lastpos = 0

    while 1:
        m = wikilink.search(text, lastpos)
        if m:
            # found some sort of link pattern - check if we should link it
            link = m.group()
            linkstart, linkend = m.span()

            if (link[0]=='!'
                or withinLiteral(linkstart, linkend-1, state, text)):
                # no - ignore it (and strip the !)
                if link[0] == '!':
                    link=link[1:]
                if markedtext and isinstance(markedtext[-1], TextBlock):
                    markedtext[-1].merge(text[lastpos:linkstart] + link)
                else:
                    markedtext.append(TextBlock(text[lastpos:linkstart] + link))
            else:
                # yes - mark it for later
                if markedtext and isinstance(markedtext[-1], TextBlock):
                    markedtext[-1].merge(text[lastpos:linkstart])
                else:
                    markedtext.append(TextBlock(text[lastpos:linkstart]))

                if url.match(link):
                    markedtext.append(URLBlock(link))
                else:
                    markedtext.append(WikiLinkBlock(link))

            lastpos = linkend
        else:
            # no more links - save the final text extent & quit
            if markedtext and isinstance(markedtext[-1], TextBlock):
                markedtext[-1].merge(text[lastpos:])
            else:
                markedtext.append(TextBlock(text[lastpos:]))
            break
    return markedtext


def withinLiteral(upto, after, state, text):
    """
    Check text from state['lastend'] to upto for literal context:

    - within an enclosing '<pre>' preformatted region '</pre>'
    - within an enclosing '<code>' code fragment '</code>'
    - within a tag '<' body '>'
    - within an '<a href...>' tag's contents '</a>'

    We also update the state dict accordingly.
    """
    # XXX This breaks on badly nested angle brackets and <pre></pre>, etc.
    lastend,inpre,incode,intag,inanchor = \
      state['lastend'], state['inpre'], state['incode'], state['intag'], \
      state['inanchor']

    newintag = newincode = newinpre = newinanchor = 0
    text = text.lower()

    # Check whether '<pre>' is currently (possibly, still) prevailing.
    opening = text.rfind(u'<pre', lastend, upto)
    if (opening != -1) or inpre:
        if opening != -1: opening = opening + 4
        else: opening = lastend
        if -1 == text.rfind(u'</pre>', opening, upto):
            newinpre = 1
    state['inpre'] = newinpre

    # Check whether '<code>' is currently (possibly, still) prevailing.
    opening = text.rfind(u'<code', lastend, upto)
    if (opening != -1) or incode:
        if opening != -1: opening = opening + 5
        # We must already be incode, start at beginning of this segment:
        else: opening = lastend
        if -1 == text.rfind(u'</code>', opening, upto):
            newincode = 1
    state['incode'] = newincode

    # Determine whether we're (possibly, still) within a tag.
    opening = text.rfind(u'<', lastend, upto)
    if (opening != -1) or intag:
        # May also be intag - either way, we skip past last <tag>:
        if opening != -1: opening = opening + 1
        # We must already be intag, start at beginning of this segment:
        else: opening = lastend
        if -1 == text.rfind(u'>', opening, upto):
            newintag = 1
    state['intag'] = newintag

    # Check whether '<a href...>' is currently (possibly, still) prevailing.
    #XXX make this more robust
    opening = text.rfind(u'<a ', lastend, upto)
    got_anchor = opening != -1
    # we used to be looking for '<a href', but attribute order can
    # actually be the other way around, e.g. RST generating <a name=...
    href_too = False
    if got_anchor or inanchor: # found or already in anchor
        if got_anchor: # found it here
            # it might just have been <a name...>
            href_too = -1 != text.rfind(u'href', opening, upto)
            # if not href_too: opening = -1
        if opening != -1: opening = opening + 5
        else: opening = lastend
        got_anchor_closing = -1 == text.rfind(u'</a>', opening, upto)
        if href_too and got_anchor_closing:
            newinanchor = 1 # the <a name=... href=...>WikiName</a> case
        elif got_anchor_closing:
            newinanchor = 0 # the <a name>WikiName</a> case
        # this would be: elif got_anchor and not got_anchor_closing:
            # the "<a name>WikiName - no closing" case is handled implicitly
            # newinanchor stays the same as initialized = 0
    state['inanchor'] = newinanchor

    state['lastend'] = after
    return newinpre or newincode or newintag or newinanchor
