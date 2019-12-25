# Hosting

## Method

My site is hosted via a cheap droplet on DigitalOcean, so far my experience with them has been pretty ok, but the ticketing system and support you get from them - I don't recommend trying unless your problem is simple. It took my issue literal hours to actually end up in their system, you have to wait for them to approve your question.

I hope to try out different services, like AWS to host my servers next, but otherwise, their tutorial section for their server stuff is brilliant, I highly recommend taking a look if you want to host anything, whether you're hosting through them, or another service entirely.

I'm currently using NameCheap to get my domain, although Google Domains offered a slightly cheaper option for my domain, and there are quite a lot of buttons and useless stuff in the NameCheap control panel, which I don't appreciate in the slightest.

For my SSL, I used the [certbot](https://certbot.eff.org/) HTTPS tool to get my SSL Certificate through Let's Encrypt, and while I was having issues (some pretty newb level ones, honestly), the Let's Encrypt community helped me with a lightning fast response time.

I was hoping to get a Hastebin server through node at a URL under root, i.e. `https://xevion.dev/hastebin/` so I could play around with a node application, but I've been unsuccessful in getting nginx to play nicely, or perhaps it's just nodes/pm2's fault. I don't really know as I'm bad at server level stuff at the moment.

## Experience so far

DigitalOcean has proved to be a optimal solution to my requirements. The smallest DO droplet costs $5/month, and while this is somewhat costly to maintain for a student like me, it's proved to be a fantastic solution for my needs. Since my site is rather small and doesn't require much in terms of space, speed, bandiwdth etc., I haven't run into any problems, and based on the numbers I'm getting, I could probably quadruple my traffic without any problems.