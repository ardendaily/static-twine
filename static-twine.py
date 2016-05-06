#!/bin/python
'''

Render published Twine stories to a series of static HTML files. 
Created with intention of bringing Twine games to TOR network without 
introducing possibly-compromising behavior ala disabling JS. Or at least
that's the starting point. We'll see where we get.

Goals:
	Variable setters and getters, so variable-driven fictions (Horse Master)
	work out-of-box. This is later. 

TO-DO:
	Link look-forward. Meaning, if starting passage is called "main", render 
	only "index.html," and all links to "main.html" become links to "index.html"

	Templating system -- boxes, grids, menus, all sorts of other shit.
	More magic passages because 'magic passages' sounds legit
	A less dang ugly demo twine
	Destroy the patriarchy!!


'''		

from bs4 import BeautifulSoup, NavigableString
from sys import argv
import re

class TwineStory:
	def __init__(self, _ifid, _name, _startnode, _has_userscript):
		self.ifid = _ifid
		self.name = _name
		self.start_node = _startnode
		self.node_list = []
		self.header = None
		self.footer = None
		self.has_user_script = _has_userscript #maybe b64 encode to side-step escapes

	def add_node(self,_node):
		self.node_list.append(_node)

	def add_header(self, _header_node):
		self.header = _header_node

	def add_footer(self, _footer_node):
		self.footer = _footer_node

	def render_html(self):
		'''
		Iterates node_list, adds semantically-valid html header, etc.
		'''

		#Find start node and set some defaults
		for i in range(0, len(self.node_list)):
			if self.node_list[i].pid == self.start_node:
				self.node_list[i].filename = "index.html"

		for i in range(0, len(self.node_list)):

			if self.node_list[i].name not in ["header", "footer"]:

				newsoup = BeautifulSoup("", 'html.parser')

				# BeautifulSoup for some things...
				head = newsoup.new_tag("head")
				charset = newsoup.new_tag("meta")
				charset['charset'] = "utf-8"
				head.append(charset)

				title = newsoup.new_tag("title")
				title.string = self.name + " - " + self.node_list[i].name
				head.append(title)

				stylesheet = newsoup.new_tag("link")
				stylesheet['rel'] = "stylesheet"
				stylesheet['type'] = "text/css"
				stylesheet['href'] = "userstyle.css"
				stylesheet['media'] = "screen"
				head.append(stylesheet)

				if self.has_user_script:
					userscript = newsoup.new_tag("script")
					userscript['type'] = "text/javascript"
					userscript['src'] = "userscript.js"
					head.append(userscript)

				# ...direct file access for others, grumble grumble
				file = open(self.node_list[i].filename, 'w')
				file.write('<!DOCTYPE html>\n')
				file.write('<html>\n')
				file.write( head.prettify() )
				file.write('<body>\n')
				
				if self.header != None:
					file.write( self.header.return_html() + "\n\n" )
				
				file.write( self.node_list[i].return_html() )

				if self.footer != None:
					file.write( "\n\n" + self.footer.return_html() )

				file.write('\n</body>')
				file.close()

				print self.node_list[i].filename + " written"

class TwineNode:
	def __init__(self, _name, _pid, _content, _tags=""):
		self.name = _name
		self.filename = filename_convention(_name)
		self.pid = _pid
		self.content = _content
		self.content_html = ''
		self.tags = _tags
		self.is_start_node = False

	def return_html(self):
		'''
		Mutations to raw text:
			Turns all [[hyperlinks]] into <a href=>hyperlinks</a>
			Handles emboldening, striking-through, and italicizing.
			More than two dashes on a line replaced by <hr />
		'''

		regex = re.compile(r'\[\[(.*?)\]\]')
		self.content_html = regex.sub(replace_link, str(self.content))

		regex = re.compile(r'~~(.*?)~~')
		self.content_html = regex.sub(strikethrough, str(self.content_html))

		regex = re.compile(r'\'\'(.*?)\'\'')
		self.content_html = regex.sub(embolden, str(self.content_html))

		regex = re.compile(r'//(.*?)//')
		self.content_html = regex.sub(italicize, str(self.content_html))	

		regex = re.compile(r'-{3,}')
		self.content_html = regex.sub("<hr />", str(self.content_html))	

		regex = re.compile(r'\#{1,6}(.*)')
		self.content_html = regex.sub(header, str(self.content_html))

		return self.content_html


def replace_link(_match):
	#remove square brackets
	match = _match
	regex = re.compile(r'\[|\]')
	match = regex.sub('', match.group(1))

	returnthis = ""

	#build links.
	regex = re.compile(r'->')
	if regex.search(match) == None:
		#case one: [[direct link]]
		fn = filename_convention(match)
		returnthis = '<a href="' + fn + '">' + match + '</a>' 
	else:
		#case two: [[indirect=>link]]
		title,link = match.split("->")
		fn = filename_convention(link)
		returnthis = '<a href="' + fn + '">' + title + '</a>'

	return returnthis

def embolden(_match):
	match = _match
	regex = re.compile(r'\'')
	match = regex.sub('', match.group(1))

	return "<b>" + match + "</b>"

def italicize(_match):
	match = _match
	regex = re.compile(r'~')
	match = regex.sub('', match.group(1))

	return "<em>" + match + "</em>"

def strikethrough(_match):
	match = _match
	regex = re.compile(r'/')
	match = regex.sub('', match.group(1))

	return "<del>" + match + "</del>"

def header(_match):
	match = _match
	regex = re.compile(r'#')
	newstring, count = regex.subn('', match.group())
	return "<h%s>%s</h%s>" % (count, newstring, count)

def filename_convention(_filename):
	'''
	A provided string "Hello, world!" should become 'hello__world_.html'
	'''
	filename = _filename.lower()

	#remove non-letters
	regex = re.compile(r'\W')
	filename = regex.sub(' ', filename)

	#replace spaces with underscores
	regex = re.compile(r' ')
	filename = regex.sub('_', filename)

	return filename + ".html"

def main():

	file = open(argv[1], 'r')
	soup = BeautifulSoup(file.read(), 'html.parser')
	file.close()

	story_data = soup.find('tw-storydata')
	stylesheet = soup.find('style', {"id":"twine-user-stylesheet"})
	userscript = soup.find("script", {"id":"twine-user-script"})
	has_userscript = False

	file = open("userstyle.css", "w")
	file.write("/* preserve whitespace */ \n\nbody { white-space: pre; } \n\n") # preserve whitespace
	file.write(str(stylesheet.contents[0]))
	file.close()
	print "userstyle.css written"

	if len(userscript) > 1:
		file = open("userscript.js", "w")
		file.write(str(userscript.contents[0]))
		file.close()
		has_userscript = True
		print "userscript.js written"

	story = TwineStory( story_data['ifid'],
		story_data['name'],
		story_data['startnode'],
		has_userscript
		)

	for node in soup.findAll('tw-passagedata'):
		if node['name'].lower() == "header":
			story.add_header( TwineNode(
				node['name'],
				node['pid'],
				node.contents[0],
				node['tags'])
			)
		elif node['name'].lower() == "footer":
			story.add_footer( TwineNode(
				node['name'],
				node['pid'],
				node.contents[0],
				node['tags'])
			)
		else: 
			story.add_node( TwineNode( 
				node['name'], 
				node['pid'], 
				node.contents[0], 
				node['tags']
			)
		)

	# Write to disk
	story.render_html()

if __name__ == "__main__":

	if len(argv) > 1:
		main()
	else:
		print "please provide a filename"
		exit(1)