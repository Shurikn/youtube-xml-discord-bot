import json
import sys

import discord
import time
import feedparser

configfile = "config.json"

with open(configfile) as json_file:
    configs = json.load(json_file)
configs["last_run"] = time.time()
feed = feedparser.parse(configs["feed_url"])
i = len(feed.entries)-1
to_post = []
while i >= 0:
    entry = feed.entries[i]
    published_time=time.mktime(entry.published_parsed)
    if published_time>configs["last_post_time"]:
        configs["last_post_time"] = published_time
        configs["total_item_posted"] += 1
        to_post.append(entry["link"])
    i -= 1

if len(to_post) > 0:
    client = discord.Client()

    @client.event
    async def on_ready():
        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print("------")
        channel = client.get_channel(configs["channel_id"])
        for link in to_post:
            await channel.send(link)
        with open(configfile, "w") as outfile:
            json.dump(configs, outfile)
            sys.exit()

    client.run(configs["token"])
else:
    with open(configfile, "w") as outfile:
        json.dump(configs, outfile)
        sys.exit()
