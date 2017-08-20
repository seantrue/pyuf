#! /usr/bin/env python3

u"""
markdowndoc.py

Written by Patrick Laban and Geremy Condra

Licensed under GPLv3

Released 28 April 2009

This module contains a simple class to output Markdown-style
pydocs.
"""

from __future__ import absolute_import
import pydoc, inspect, re, __builtin__

class MarkdownDoc(pydoc.TextDoc):

	underline = u"*" * 40

	def process_docstring(self, obj):
		u"""Get the docstring and turn it into a list."""
		docstring = pydoc.getdoc(obj)
		return u'```\n{}\n```\n\n'.format(docstring) if docstring else u''

	def process_class_name(self, name, bases, module):
		u"""Format the class's name and bases."""
		title = u"## class " + self.bold(name)
		if bases:
			# get the names of each of the bases
			base_titles = [pydoc.classname(base, module) for base in bases]
			# if its not just object
			if len(base_titles) > 1:
				# append the list to the title
				title += u"(%s)" % u", ".join(base_titles)
		return title

	def process_subsection(self, name):
		u"""format the subsection as a header"""
		return u"### " + name

	def docclass(self, cls, name=None, mod=None):
		u"""Produce text documentation for the class object cls."""

		# the overall document, as a line-delimited list
		document = []

		# get the object's actual name, defaulting to the passed in name
		name = name or cls.__name__

		# get the object's bases
		bases = cls.__bases__

		# get the object's module
		mod = cls.__module__

		# get the object's MRO
		mro = [pydoc.classname(base, mod) for base in inspect.getmro(cls)]

		# get the object's classname, which should be printed
		classtitle = self.process_class_name(name, bases, mod)
		document.append(classtitle)
		document.append(self.underline)

		# get the object's docstring, which should be printed
		docstring = self.process_docstring(cls)
		document.append(docstring)

		# get all the attributes of the class
		attrs = []
		for name, kind, classname, value in pydoc.classify_class_attrs(cls):
			if pydoc.visiblename(name):
				attrs.append((name, kind, classname, value))

		# sort them into categories
		data, descriptors, methods = [], [], []
		for attr in attrs:
			if attr[1] == u"data" and not attr[0].startswith(u"_"):
				data.append(attr)
			elif attr[1] == u"data descriptor" and not attr[0].startswith(u"_"):
				descriptors.append(attr)
			elif u"method" in attr[1] and not attr[2] is __builtin__.object:
				methods.append(attr)

		if data:
			# start the data section
			document.append(self.process_subsection(self.bold(u"data")))
			document.append(self.underline)

			# process your attributes
			for name, kind, classname, value in data:
				if hasattr(value, u'__call__') or inspect.isdatadescriptor(value):
					doc = getdoc(value)
				else: 
					doc = None
				document.append(self.docother(getattr(cls, name), name, mod, maxlen=70, doc=doc) + u'\n')

		if descriptors:
			# start the descriptors section
			document.append(self.process_subsection(self.bold(u"descriptors")))
			document.append(self.underline)

			# process your descriptors
			for name, kind, classname, value in descriptors:
				document.append(self._docdescriptor(name, value, mod))

		if methods:
			# start the methods section
			document.append(self.process_subsection(self.bold(u"methods")))
			document.append(self.underline)

			# process your methods
			for name, kind, classname, value in methods:
				document.append(self.document(getattr(cls, name), name, mod, cls))

		return u"\n".join(document)		

	def bold(self, text):
		u""" Formats text as bold in markdown. """
		if text.startswith(u'_') and text.endswith(u'_'):
			return u"__\%s\__" %text
		elif text.startswith(u'_'):
			return u"__\%s__" %text
		elif text.endswith(u'_'):
			return u"__%s\__" %text
		else:
			return u"__%s__" %text

	def indent(self, text, prefix=u''):
		u"""Indent text by prepending a given prefix to each line."""
		return u"```\n{}\n```".format(text) if text else text
    
	def section(self, title, contents):
		u"""Format a section with a given heading."""
		clean_contents = self.indent(contents).rstrip()
		return u"# " + self.bold(title) + u'\n\n' + clean_contents + u'\n\n'

	def docroutine(self, object, name=None, mod=None, cl=None):
		u"""Produce text documentation for a function or method object."""
		realname = object.__name__
		name = name or realname
		note = u''
		skipdocs = 0
		if inspect.ismethod(object):
			object = object.im_func
		if name == realname:
			title = self.bold(realname)
		else:
			if (cl and realname in cl.__dict__ and cl.__dict__[realname] is object):
				skipdocs = 1
			title = self.bold(name) + u' = ' + realname
		if inspect.isfunction(object):
			args, varargs, varkw, defaults, kwonlyargs, kwdefaults, ann = inspect.getargspec(object)
			argspec = inspect.formatargspec(
				args, varargs, varkw, defaults, kwonlyargs, kwdefaults, ann,
				formatvalue=self.formatvalue,
				formatannotation=inspect.formatannotationrelativeto(object))
			if realname == u'<lambda>':
				title = self.bold(name) + u' lambda '
				# XXX lambda's won't usually have func_annotations['return']
				# since the syntax doesn't support but it is possible.
				# So removing parentheses isn't truly safe.
				argspec = argspec[1:-1] # remove parentheses
		else:
			argspec = u'(...)'
		decl = u"#### " + u"def " + title + argspec + u':' + u'\n' + note

		if skipdocs:
			return decl + u'\n'
		else:
			doc = pydoc.getdoc(object) or u''
			return decl + u'\n' + (doc and self.indent(doc).rstrip() + u'\n')

	def docother(self, object, name=None, mod=None, parent=None, maxlen=None, doc=None):
		u"""Produce text documentation for a data object."""
		line = u"#### " + object.__name__ + u"\n"
		line += super(MarkdownDoc, self).docother(object, name, mod, parent, maxlen, doc)
		return line + u"\n"

	def _docdescriptor(self, name, value, mod):
		results = u""
		if name: results += u"#### " + self.bold(name) + u"\n"
		doc = pydoc.getdoc(value) or u""
		if doc: results += doc + u"\n"
		return results
