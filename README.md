# MC Bot

## Description

Uses markov chains to generate random sentences, and send them to a Twitch.tv IRC chat. 

## Instructions

Update auth.py with relevant information. See https://dev.twitch.tv/docs/v5/ on how to get a client ID and an OAUTH token. Then execute run.py.

You can add comma-separated words to banned.txt to have the bot ignore messages containing these words. This in turn prevents the bot from generating any messages containing banned words.
