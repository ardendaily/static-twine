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