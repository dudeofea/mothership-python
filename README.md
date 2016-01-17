# Mothership (python)
A redo of mothership using python instead for the server, mainly because I felt like giving it a rewrite (bite me [Joel Spolsky](http://www.joelonsoftware.com/articles/fog0000000069.html))

Actually I rewrote it to avoid writing my own BLE server (or client, I forget how that messed up architecture works) in C again, like I did last time. I would have just used my previous code but it didn't work with this controller it seems, I couldn't subscribe to listen events, at least not right off the bat.

Also, I've been doing a lot of things in python so it's pretty confortable for me, and the useability / speed tradeoff seems quite fair to me.

Other neat features: built-in reflection, Adafruit BLE UART library

Progress
--------
I'm currently writing the controller UI first so I can box that up and not have to worry about it, I'll get to the jackd server in a bit. The latency should be alright, if not numpy'll do the trick or worst yet...Cython!

Right now, about 30%
