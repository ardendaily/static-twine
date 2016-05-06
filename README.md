# static-twine.py

an attempt to make twine 2 something that it is not: a wysiwyg-ish website builder. perhaps not a great idea, but certainly a project for me all the same.

## features out of the box

**support for most text styling, including and limited to**

- all sorts of headers (#-######)
- //italics//
- ''emboldening''
- ~~striking-through~~


**it also supports links!**

- [[direct links]]
- [[and indirect->links]]


## but wait there's more

**magic passages**

create a passage named 'header' and it will always appear at the top of any generated page!

create a passage named 'footer' and it will always appear at the bottom of any generated paaaaage!

**userstyle and userscript**

anything appearing in the story stylesheet or story javascript will be appended to your page. for the sake of individual page loadtime, and to practice sanity in all things, these assets are rendered as external files and are properly linked in the `<head>` of all pages. 

## ok great how do i use this monster

`pip install beautifulsoup4 #if you don't have it already` 
`python static-twine.py your-exported-twine-project.html`

you will see pages generated for every individual branch in your project's tree, or nasty error messages if your project is *too complicated*.

## license

WTFPLv2