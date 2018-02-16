====
Rime
====

.. image:: https://img.shields.io/circleci/project/github/ZoidBB/rime/master.svg?style=for-the-badge   :target: 
.. image:: https://img.shields.io/pypi/v/rime.svg?style=for-the-badge   :target: 

---------------------------
What's the reason for Rime?
---------------------------

I'm not a huge fan of many of the other static site generation tools out there, especially not those built in Python. I liked the idea of being able to mix the concept most statigens use, of using flat files to store the majority of data and to manage content -- but I wanted the option of treating things more dynamically when I wanted/needed to.

FrozenFlask was a great tool for generating a static tree from Flask routes, but I really needed more of the magic sauce other staticgens had before it was usable in the way I had intended.

---------------------------
What makes Rime so special?
---------------------------

* Using MongoMock, all content is stored and queryable from within the site as if you were actually using MongoDB/MongoEngine.
* All content is executed as if it were a template, allowing you to build more advanced pages than you could with pure markup. This includes querying for other content, including snapshots of other content, etc -- all dynamically.
* The system is very pluggable. In fact, Rime itself is simply a pluggable static framework on top of which RimeCore implements the flat-file content system. You can use it, replace it, build on top of it, etc.

---------------
What's missing?
---------------

RSS and Taxonomy support will not be in the initial release, and are slated for 0.2.0. Image and image gallery support is not currently planned as part of RimeCore, as there are entirely too many options for how to implement such a thing. Expect such a thing to be released as an external plugin.

------------
Ok now what?
------------

0.1.0 isn't out yet, but it will be soon -- stay tuned.
