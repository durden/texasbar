#Texas Bar
Simple little commandline application to provide a way to search the
[Texas bar website](http://www.texasbar.com/am/Template.cfm?Section=Find_a_Lawyer&Template=/CustomSource/MemberDirectory/Search_Form_Client_Main.cfm) for attorneys.

##Why
My wife was starting an alumni group for [Texas Tech
University](http://www.ttu.edu) law school graduates in Houston, TX.  She was
going to spend hours slowly searching through page after page of HTML to
manually add all possible participants to contact list.  Of course, I'm a nerd
and decided this time was wasteful, so I made a script for it.

###Usage

From command line

    python texasbar/search.py -h
    python texasbar/search.py

From script

    >>> import texasbar
    >>> for result_page in texasbar.search.search():
    >>>     print result_page
