# Shopping List

This is the parts list from my cluster with prices (CDN$ in August/September 2015, before taxes and shipping):


* [Raspberry Pi 2 model B](http://ca-en.alliedelec.com/raspberry-pi-raspberry-pi-2-model-b/70465426/), 7 × $48.
* [ADATA 8GB microSDHC](http://www.ncix.com/detail/adata-8gb-microsdhc-micro-secure-36-59749-1928.htm), 7 × $5
* [Kingston 32GB DT Microduo USB](http://www.ncix.com/detail/kingston-32gb-dt-microduo-usb-1d-101086-1834.htm), 7 × $15.
* [8 port Ethernet switch](http://www.ncix.com/detail/tp-link-tl-sg1008d-8-port-unmanaged-0c-34461-1211.htm), $30.
* [7-port powered USB hub](http://www.ncix.com/detail/vantec-7-port-usb-3-0-f0-108766.htm), $47.
* [TP-link TL-WR740N](http://www.ncix.com/detail/tp-link-tl-wr740n-4-port-10-100-c3-52257.htm) router, $21.
* [1 ft Right Angle MicroUSB cable](http://www.newegg.ca/Product/Product.aspx?Item=N82E16812200860), 7 × $6.
* short ethernet cables, 8 × donated.
* [Stanley FatMax Deep Professional Organizer](http://www.canadiantire.ca/en/tools-hardware/tool-storage/small-parts-storage-organization/stanley-fatmax-deep-professional-organizer-0581174p.html?utm_campaign=bazaarvoice&utm_medium=SearchVoice&utm_source=RatingsAndReviews&utm_content=Default), as a case, $33.
* [4-40 threaded rod and nuts](http://www.pacificfasteners.com/), $3
* [3/4" spacers](http://www.rpelectronics.com/60341-c-insulated-spacer-6-hole-3-4-pkg-100.html), $10
* [Four-outlet power bar](http://www.homehardware.ca/en/rec/index.htm/Plumbing-Electrical/Electrical/Extension-Cords/Power-Bars/Power-Bars/4-Plug-Slimline-Strip-Outlet/_/N-2pqfZ67l/Ne-67n/Ntk-All_EN/R-I3665705?Ntt=4+outlest), $13.
* [2.5" corner brace](http://www.homedepot.ca/product/2-1-2-inch-zinc-corner-brace-4pk/821665) (to give a mounting point for the rod+spacer+pi assembly), $2.
* lamp extension cord cut to length with a new plug, donated.
* velcro tape and zip ties (to attach everything to the case and keep it neat) ≈$5.

Total: $682.

## Notes

Important: you need a USB hub that can actually deliver 7 × 5V × [≈1A](http://raspi.tv/2014/how-much-less-power-does-the-raspberry-pi-b-use-than-the-old-model-b) = 35W. That's not every USB hub. This one has a 12V × 3A = 36W transformer and it still browns-out the last node for a few seconds while the other six start.

The Ethernet switch is actually connected to the Pis. The router is connected to the 8th port on the switch to do DHCP, DNS, and provide an internal network. A laptop can be connected to one of the router's ports to work with the cluster. (Or the switch can be connected directly to an outside network.)

I get about double the read-write speed from the USB drive as from the SD card: that's why I went with separate storage.

In the end, my cluster looks like this:

![cluster assembled and running](/images/running2.jpg?raw=true)
