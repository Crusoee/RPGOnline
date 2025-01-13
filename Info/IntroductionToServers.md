Everything you need to know about tick rate, interpolation, lag compensation, etc.
Quality Post
Hi guys,

There is a lot of talk regarding the tick rate and general performance of overwatch and unfortunately with it there is also a large amount of misinformation. I wanted to create a thread that explains the terminology, so that we can add some perspective to the differences that various factors make in terms of how the game plays.

Preamble:

In almost all modern FPS games the server maintains the game state. This is important to prevent cheating, but leads to some of the issues people experience. In a client-server game design, there is always going to be the problem of a difference in game state between the client and server. I.E. The client sees a delayed version of the "True" game state on the server. This will always exist, but there are some things we can do to make it less noticeable.

Netcode

A blanket term used to describe the network programming of a game. It's basically a meaningless blanket term used to describe the network component of game programming. It is not a technical term.

Latency

Also commonly (and incorrectly) referred to as "Ping". This is the time it takes for a packet to travel from your client computer, to the server, and back (round trip time or RTT). The reason people often call it "Ping" is that there was a tool built in the 80s called ping that was used to test for latency using something called an ICMP echo. The "ping" command still lives on today in most operating systems. In other words, a ping is a test, that uses an ICMP echo, to measure latency. Note that the one-way travel time of a packet is not always equal to 1/2 of the RTT, but for simplicity's sake we will assume that. From here out I will refer to RTT latency as just latency, and one way packet latency as 1/2Latency.*

Tick rate

Tick rate is the frequency with which the server updates the game state. This is measured in Hertz. When a server has a tick rate of 64, it means that it is capable of sending packets to clients at most 64 times per second. These packets contain updates to the game state, including things like player and object locations. The length of a tick is just its duration in milliseconds. For example, 64 tick would be 15.6ms, 20 tick would be 50ms, 10 tick 100ms, etc.

Client Update Rate

The rate at which the client is willing to receive updates from the server. For example, if the client update rate is 20, and the server tick rate is 64, the client might as well be playing on a 20 tick server. This is often configured locally, but in some games cannot be changed.

Framerate

The number of frames per second your client is capable of rendering video at. Usually notated as FPS.

Refresh Rate

The number of times per second your Monitor updates what your video card rendered on the monitor. Measures in Hertz (times per second). If you have a framerate of 30 for example, your monitor will show each frame twice on a 60Hz monitor. If you had a framerate of 120 on a 60Hz monitor, the monitor can realistically only display 60 frames per second. Most monitors are 60Hz or 120Hz.

Interpolation

Interpolation is a technology which smooths movements of objects in the game (e.g. players). Essentially what interpolation is doing, is smoothing out the movement of an object moving between two known points. The interpolation delay is typically equal to 2 ticks, but can vary.

For example, if a player is running in a straight line, and at the time of "Tick 1" they were at 0.5m, and at "Tick 2" they were at 1m, the interpolation feature, would make it appear on the client, as if they moved smoothly from 0.5m to 1m away from their starting location. The server however, only ever really "sees" the player at those two locations, never in between them. Without interpolation, games would appear very choppy, as the client would only see objects in the game move whenever they received an update from the server. Interpolation occurs exclusively on the client side.

Interpolation essentially slows the rate at which the entire game is being rendered to your computer, by a value of time typically equal to 2 ticks (however some games allow you to tweak this, like CSGO) This is what people are talking about when they refer to their "rates". They mean Update Rate, and Interpolation delay. CSGO for example has a default interpolation period of 100ms. correction: CSGO uses 2x the update rate, or 31ms if update rate is 64Hz, 100ms is the default for cs source I think.

Extrapolation

This is another client-side technique that can be used to compensate for lag. Essentially the client extrapolates the position of objects rather than delaying the entire client render. This method is generally inferior to Interpolation, especially for FPS games since players movements are not predictable.

"Hit Box"

A 3D model of the character that represents areas considered a valid "hit". You cannot see a hitbox, you can only see the player model. Hitboxes may be larger or smaller, or inaccurate in some ways, depending on the programming of the game. This can make a much larger difference than tick rate regarding perceived hits and misses.

Lag Compensation

Lag compensation is a function on the server which attempts to reduce the perception of client delay. Here is a pretty decent video explanation: https://www.youtube.com/watch?v=6EwaW2iz4iA

Without lag compensation (or with poor lag compensation), you would have to lead your target in order to hit them, since your client computer is seeing a delayed version of the game world. Essentially what lag compensation is doing, is interpreting the actions it receives from the client, such as firing a shot, as if the action had occurred in the past.

The difference between the server game state and the client game state or "Client Delay" as we will call it can be summarized as: ClientDelay = (1/2*Latency)+InterpolationDelay

An example of lag compensation in action:

Player A sees player B approaching a corner.

Player A fires a shot, the client sends the action to the server.

Server receives the action Xms layer, where X is half of Player A's latency.

The server then looks into the past (into a memory buffer), of where player B was at the time player A took the shot. In a basic example, the server would go back (Xms+Player A's interpolation delay) to match what Player A was seeing at the time, but other values are possible depending on how the programmer wants the lag compensation to behave.

The server decides whether the shot was a hit. For a shot to be considered a hit, it must align with a hitbox on the player model. In this example, the server considers it a hit. Even though on Player B's screen, it might look like hes already behind the wall, but the time difference between what player B see's and the time at which the server considers the shot to have taken place is equal to: (1/2PlayerALatency + 1/2PlayerBLatency + TimeSinceLastTick)

In the next "Tick" the server updates both clients as to the outcome. Player A sees the hit indicator (X) on their crosshair, Player B sees their life decrease, or they die.

Note: In an example where two players shoot eachother, and both shots are hits, the game may behave differently. In some games. e.g. CSGO, if the first shot arriving at the server kills the target, any subsequent shots by that player that arrive to the server later will be ignored. In this case, there cannot be any "mutual kills", where both players shoot within 1 tick and both die. In Overwatch, mutual kills are possible. There is a tradeoff here.

If you use the CSGO model, people with better latency have a significant advantage, and it may seem like "Oh I shot that guy before I died, but he didn't die!" in some cases. You may even hear your gun go "bang" before you die, and still not do any damage.

If you use the current Overwatch model, tiny differences in reaction time matter less. I.e. if the server tick rate is 64 for example, if Player A shoots 15ms faster than player B, but they both do so within the same 15.6ms tick, they will both die.

If lag compensation is overtuned, it will result in "I shot behind the target and still hit him"

If it is undertuned, it results in "I need to lead the target to hit them".

What this all means for Overwatch

Generally, a higher tick-rate server will yield a smoother, more accurate interaction between players, but it is important to consider other factors here. If we compare a tick rate of 64 (CSGO matchmaking), with a tick rate of 20 (alleged tick rate of Overwatch Beta servers), the largest delay due to the difference in tick rate that you could possibly perceive is 35ms. The average would be 17.5ms. For most people this isn't perceivable, but experienced gamers who have played on servers of different tick rates, can usually tell the difference between a 10 or 20 tick server and a 64 tick one.

Keep in mind that a higher tickrate server will not change how lag compensation behaves, so you will still experience times where you ran around the corner and died. 64 Tick servers will not fix that.

If you are concerned about the performance of the game, there are a few things you should rule out first, that can make a significant difference:

Your internet connection. The lower the latency the better. This is why its important to play on the servers on which you have the lowest latency. Also any congestion on your home internet connection can cause delays. Lag compensation helps with the "what you are shooting" part, but if you have poor latency, you are much more likely to experience the "I ran behind a corner and still got shot" scenario or the "I shot first and still died" scenario.

If your client has a poor frame-rate (anything lower than or close to your monitor refresh rate), this will increase the delay perceived, often by more than the difference tick rate makes.

Tweak your interpolation if the game allows it. Most games will have a default interpolation period that is at least 2x the duration between ticks, the idea being that if a single packet is lost, a player movement will not stutter on the client screen. If your internet connection is good, and you have zero packet loss, you can safely set the interpolation period roughly equal to the tick duration, but if a packet is delayed, you will see a stutter. In CSGO for example, this will make a larger difference than moving from a 20 tick server to a 64 tick server. If you set this too low, it WILL cause choppiness.

If the game allows you to increase the client update rate, you should do it if you want optimal performance. It comes at the cost of more CPU and bandwidth usage, however on the client side this usually doesn't matter unless your home internet connection has very low bandwidth available.

If you have a monitor refresh rate of 60Hz, then you probably can't tell the difference between a tick rate of 64 and 128, because your monitor can't even display the difference attributable to the tick rate.

One final note:

We don't actually know what the tickrate of the servers is, I saw the thread with the wireshark capture, and it shows the client receiving packets every 50ms. This would indicate 20 tick, but this is only true if the client update rate = the server tick rate. Often the client update rate is a parameter that is set locally in the client that will be sent to the server when the client connects. The server then sends updates at that frequency. The server may actually be running at a higher tick rate, but if the client update rate is set to 20, then the server will only send an update every 50ms.

So before you crucify the developers over 20 tick servers, figure out what the tick rate actually is, and whether the client update rate can be changed in a config

TL;DR; Very few people actually understand "netcode", but are happy to complain about getting killed when they are behind a wall.

Edit: Reddit Gold! Thanks mysterious benefactors!

Edit: A good write up on the difference between 64 tick and 128 tick servers: http://mukunda.com/128tick.html