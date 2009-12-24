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
from pytz import utc
from datetime import datetime
from difflib import SequenceMatcher
from BTrees.Length import Length
from BTrees.IOBTree import IOBTree
from persistent import Persistent
from difflib import SequenceMatcher

from zope import interface, event
from zope.location import Location
from zope.component import getUtility
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.richtext.field import RichTextData

from interfaces import _, IRevision, IHistory


class Revision(Persistent, Location):
    interface.implements(IRevision)

    note = u''
    principal = u''

    def __init__(self, title, text, format, cooked):
        self.title = title
        self.text = text
        self.format = format
        self.cooked = cooked

        self.date = datetime.now(utc)

    def revert(self, principal):
        history = self.__parent__
        page = self.__parent__.__parent__

        revision = Revision(
            page.title, page.text.text, page.text.format, page.cooked)
        history.add(revision, u'Reverted to %s version'%self.__name__, principal)

        page.title = self.title
        page.text = RichTextData(self.text, self.format)
        page.cook()
        event.notify(ObjectModifiedEvent(page))

    def getPrincipal(self):
        try:
            return getUtility(IAuthentication).getPrincipal(self.principal)
        except PrincipalLookupError:
            return None


class History(Persistent, Location):
    interface.implements(IHistory)

    __name__ = u'history'
    title = _('History')

    def __init__(self, page):
        self.__parent__ = page
        self.length = Length(0)
        self.revisions = IOBTree()

    def add(self, revision, note, principal):
        idx = self.length()
        self.length.change(1)

        revision.__name__ = str(idx)
        revision.__parent__ = self
        revision.note = note
        revision.principal = principal

        self.revisions[idx] = revision

    def _abbreviateDiffLines(self, lines, prefix, maxlines=5):
        output = []
        if maxlines and len(lines) > maxlines:
            extra = len(lines) - maxlines
            for i in xrange(maxlines - 1):
                output.append(prefix + lines[i])
            output.append(prefix + "[%d more line%s...]" %
                          (extra, ((extra == 1) and '') or 's')) # not working
        else:
            for line in lines:
                output.append(prefix + line)
        return output

    def diff(self, rid1, rid2, verbose=1):
        """
        generate a plain text diff, optimized for human readability,
        between two revisions of this page, numbering back from the latest.
        Alternately, a and/or b texts can be specified.
        """
        maxOldLines = self.__parent__.__parent__.maxOldLines
        maxNewLines = self.__parent__.__parent__.maxNewLines

        old = [s.strip() for s in self[rid1].text.split(u'\n')]
        new = [s.strip() for s in self[rid2].text.split(u'\n')]
        cruncher = SequenceMatcher(isjunk=lambda x: x in u" \\t", a=old, b=new)

        r = []
        for tag, old_lo, old_hi, new_lo, new_hi in cruncher.get_opcodes():
            if tag == u'replace':
                if verbose: r.append(u'??changed:')
                r = r + self._abbreviateDiffLines(
                    old[old_lo:old_hi], u'-', maxOldLines)
                r = r + self._abbreviateDiffLines(
                    new[new_lo:new_hi], u'+', maxNewLines)
                r.append(u'')
            elif tag == u'delete':
                if verbose: r.append(u'--removed:')
                r = r + self._abbreviateDiffLines(
                    old[old_lo:old_hi], u'-', maxOldLines)
                r.append(u'')
            elif tag == u'insert':
                if verbose: r.append(u'++added:')
                r = r + self._abbreviateDiffLines(
                    new[new_lo:new_hi], u'+', maxNewLines)
                r.append(u'')
            elif tag == u'equal':
                pass

        return [line.strip() for line in r]

    def get(self, key, default=None):
        return self.revisions.get(key, default)

    def keys(self):
        return self.revisions.keys()

    def items(self):
        return self.revisions.items()

    def values(self):
        return self.revisions.values()

    def __iter__(self):
        return iter(self.revisions)

    def __len__(self):
        return self.length()

    def __getitem__(self, key):
        return self.revisions[int(key)]

    def __contains__(self, key):
        try:
            return int(key) in self.revisions
        except:
            return False
