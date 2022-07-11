# mrlazy-bot
A minimalistic and somewhat security-conscious attempt at a home automation bot, via Slack and AWS SQS.

## Summary

```
< mobile, probably >           (         ~~~ AWS Land ~~~       )     [ home, aka on-prem  ]
You --> Slack --(Event API)--> ( API Gateway --> Lambda --> SQS ) <-- [ poller --> actions ]
            ^                                                                        /
             \------------------------------(Slack API)-----------------------------/
```

## Prerequisites

You will need:
- A phone (you probably already got one)
  - With the Slack app
- A Slack org
  - That you can create bots in
  - That you also trust... Assume that anyone in your slack org can perform every action your bot can perform
- An AWS account
  - We'll stay in the free tier, trust me
- An "on-prem" computer
  - Can be a raspberry pi
  - Can be your gaming computer
  - Could even be your home kubernetes...
- [Optional] A terraform cloud account
  - It's free
  - Managing AWS is much easier this way
  
## Why

1. Sometimes I want to do things that can only be done in my home network (e.g. run a bash script as sudo)
2. I want to be able to do these things while I'm on the go (i.e. from my phone please)
3. I ( don't want to | can't ) ( open ports | expose a web server ) from my home. Not even SSH
4. I want to incur minimal cost, stay in the free tier for everything please

## Alternatives considered

__Why not Github Actions self-hosted runner?__

Hey the "on-prem" poller/action looks awfully like a self-hosted runner for github actions. Why not just use that? 

- Not easy for a Slack message to trigger a GHA run
- Still need some kind of event listener (API) to receive Slack Event API calls

__Why not serve the Slack event listener at home/on-prem?__

Choose one or more of the below reasons:
- I don't want to open ports to the internet.
- My ISP does uses a CG-NAT, so I can't open ports to the internet.
- I'm afraid of hackers on the internet
- This is actually for work and I can't get this past security/network/my boss.
- This is actually for work and I can't be bothered to get this past security/network/my boss.

__Why have an on-prem at all? Just put everything on the cloud__

You know the drill:
- I want to keep my data on my own hard drives
- Running a media server on the cloud is expensive/hard/expensive-and-hard
- I happen to have spare computer(s) running at home
- I'm using it to do things on a crypto miner
