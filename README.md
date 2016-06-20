# Mothership (python)
A redo of mothership using python instead for the server, mainly because I felt like giving it a rewrite (bite me [Joel Spolsky](http://www.joelonsoftware.com/articles/fog0000000069.html))

Actually I rewrote it to avoid writing my own BLE server (or client, I forget how that messed up architecture works) in C again, like I did last time. I would have just used my previous code but it didn't work with this controller it seems, I couldn't subscribe to listen events, at least not right off the bat.

Also, I've been doing a lot of things in python so it's pretty confortable for me, and the useability / speed tradeoff seems quite fair to me.

Other neat features: built-in reflection

What is Mothership
------------------
An idea I had (seemingly a [popular](http://www.illucia.com/) [one](http://toplap.org/foxdot-live-coding-with-python-and-supercollider/) [at](http://gregsurges.com/projects/snakecorral) [that](https://hoxtonowl.com/)) to have the control / tactile pleasure of analog synths while not being prohibitively expensive and having the versatility of a software synth. I decided to write it myself for the challenge, the fun, the glory, and so I could include my own set of features. The modular synth software I wrote myself, I opted for typeless variable passing between effects (ie: whatever you want to pass) and a float buffer (or list in python) for input output. I would rather think of music in terms of samples than say, frequencies, as a lot of music programming languages do.

Right now, I have a hardware module knobber (or a thing with knobs) to edit the module's arguments, which the module may or may not treat the same as inputs (up to it, really). And I've got ideas (but no implementations) for other modules to connect in, like a patcher, or an XY control pad. The module driver code (also in python) just manhandles the "engine" variable and uses it's API to do stuff.

Progress
--------
I'm currently writing the controller UI first so I can box that up and not have to worry about it, I'll get to the jackd server in a bit. The latency should be alright, if not numpy'll do the trick or worst yet...Cython!

Right now, about 90% of a fully working version. It would be nice to have a hardware patcher, but I'd have to build it first.

Setup
-----
You'll most likely need Ubuntu as that's what I always use.

Installing prerequisites:

`sudo apt-get install libffi-dev`

`pip install bitarray JACK-Client`

You'll also have to modify some permissions to use jackd with your user account. Most likely:

`sudo usermod -a -G audio <USER_NAME>` to add yourself to the audio group

as well as following [this](http://jackaudio.org/faq/linux_rt_config.html) guide to setting audio security limits (for realtime)
