# Xevion.dev

## Purpose

The purpose of my site, [https://xevion.dev](https://xevion.dev), is to display my site, learn Flask and other web development frameworks, and overall get some real experience.
I'll display my previous projects, as well as play with how Python and Flask work, using SQLite Databases and more.
I won't be putting up anything on there that I won't be putting on GitHub, as I want to put a separate repository on my profile and update both my site and my repository at the same time (maybe use some kind of crazy webhooks stuff to have them automatically update?).

## Hosting Method

My site is hosted via a cheap droplet on DigitalOcean, so far my experience with them has been pretty ok, but the ticketing system and support you get from them - I don't recommend trying unless your problem is simple. It took my issue literal hours to actually end up in their system, you have to wait for them to approve your question.

I hope to try out different services, like AWS to host my servers next, but otherwise, their tutorial section for their server stuff is brilliant, I highly recommend taking a look if you want to host anything, whether you're hosting through them, or another service entirely.

I'm currently using NameCheap to get my domain, although Google Domains offered a slightly cheaper option for my domain, and there are quite a lot of buttons and useless stuff in the NameCheap control panel, which I don't appreciate in the slightest.

For my SSL, I used the [certbot](https://certbot.eff.org/) HTTPS tool to get my SSL Certificate through Let's Encrypt, and while I was having issues (some pretty newb level ones, honestly), the Let's Encrypt community helped me with a lightning fast response time.

I was hoping to get a Hastebin server through node at a URL under root, i.e. `https://xevion.dev/hastebin/` so I could play around with a node application, but I've been unsuccessful in getting nginx to play nicely, or perhaps it's just nodes/pm2's fault. I don't really know as I'm bad at server level stuff at the moment.

## Features in Development

* Signup page
    * Some kind of sign-up page would be nice, but I'll need to create some kind of administration role setup so only I can do things while registered users will not be able to do much more than post or view stuff on my site.
    * Late Addendum: Users probably will not need a profile, so I hope to discontinue any progress on inter-user interaction, focusing more on myself and the interaction between the users and my site's services (all zero of them).
* Projects Page
    * Integrate with GitHub so that code, images etc. are automatically updated. Needs a lot of thinking to come up with a smart, automatically updating, featureful way so that anything I work on can be properly displayed on the website beauitfully.
* FTBHot Mini-project
    * I'd like to integrate a interesting Embed for Discord to pull the /hot posts from the subreddit /r/feedthebeast.
* YouTube MP3s (and other services)
    * To integrate with my Expression 2 scripts, I'm attempting to create a YouTube to MP3 API for servicing my Garry's Mod experience. Mostly a chance to start updating my site with new stuff, properly finish things I never got around to last time.
    * Once I properly integrate it with a simple database system for keeping track of files, proxies, URLs, services (YouTube, Spotify, Soundcloud etc.), I'd be highly interested in completing my script to lease to people for in-game payment.
* Features Page
    * At some point, once I complete more features, I need a way to show people how to use them, where they are etc.
    * So far, all my features are completely hidden, my code is a maze of functions that most people won't care to read.
* Better spotify-explicit integration
    * More graphs, better graph export/filenames to user