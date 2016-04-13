#!/bin/python
'''

Render published Twine stories to a series of static HTML files. 
Created with intention of bringing Twine games to TOR network without 
introducing possibly-compromising behavior ala disabling JS. Or at least
that's the starting point. We'll see where we get.

Goals:
	a) Spidered hyperlinks -- get the whole structure to render as separate files
		"Just ship" something that turns Twine stories 
	b) Semantic knowledge -- Twine markup properly renders headers, etc.
	c) Variable setters and getters, so variable-driven fictions (Horse Master)
		work out-of-box. This is later. 

'''		

from bs4 import BeautifulSoup
from sys import argv
import re

class TwineStory:
	def __init__(self, _ifid, _name, _startnode, _stylesheet="", _userscript=""):
		self.ifid = _ifid
		self.name = _name
		self.start_node = _startnode
		self.node_list = []
		self.stylesheet = _stylesheet #maybe b64 encode to side-step escapes
		self.user_script = _userscript #maybe b64 encode to side-step escapes

	def add_node(self,_node):
		self.node_list.append(_node)

	def return_html(self):
		'''
		Iterates node_list, adds semantically-valid html header, etc.
		'''

		for i in range(0, len(self.node_list)):
			file = open(self.node_list[i].name, 'w')
			file.write('''<!DOCTYPE html>
<html> 
	<head>
		<title>''' + self.name + '''</title>
		<style type="text/css">
		body {
				white-space: pre;
			}
''' + self.stylesheet + '''</style>
		<script langauge="javascript">''' + self.user_script + '''</script>
	</head>
	<body>
''' + self.node_list[i].return_html() + '''
	</body>
</html>''')
			file.close()
			print self.node_list[i].name + " written"

class TwineNode:
	def __init__(self, _name, _pid, _content, _tags=""):
		self.name = filename_convention(_name)
		self.pid = _pid
		self.content = _content
		self.content_html = ''
		self.tags = _tags

	def return_html(self):
		'''
		Mutations to raw text:
			Turns all [[hyperlinks]] into <a href=>hyperlinks</a>
			Turns all \t into 2x&nbsp;
		'''

		regex = re.compile(r'\t')
		self.content_html = regex.sub('&nbsp;&nbsp;', self.content)

		regex = re.compile(r'\[\[(.*?)\]\]')
		self.content_html = regex.sub(replace_link, str(self.content_html))

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

def filename_convention(_filename):
	'''
	A provided string "Hello, world!" should become 'hello__world_.html'
	'''

	if _filename == "Start Passage":
		return "index.html"

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
	
	story_data = soup.find('tw-storydata')

	story = TwineStory( story_data['ifid'],
		story_data['name'],
		story_data['startnode'])

	for node in soup.findAll('tw-passagedata'):
		story.add_node( TwineNode( 
			node['name'], 
			node['pid'], 
			node.contents[0], 
			node['tags']))

	story.return_html()

if __name__ == "__main__":

	if len(argv) > 1:
		main()
	else:
		print "please provide a filename"
		exit(1)