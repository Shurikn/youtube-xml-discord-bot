import json
import sys

import discord
import time
import feedparser

config_file = "config.json"

with open(config_file) as json_file:
    config = json.load(json_file)

if "config_version" not in config:
    # upgrade the config file from v0 to current version
    print("a")
# if version of the config file exist, check the last version and upgrade to new version

config["last_run"] = time.time()
configs=config["configs"]
to_post = []
config_index=0
for post_config in configs:
    feeds = post_config["feed_urls"]
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        i = len(feed.entries)-1
        while i >= 0:
            entry = feed.entries[i]
            published_time=time.mktime(entry.published_parsed)
            if published_time>config["configs"][config_index]["last_post_time"]:
                config["configs"][config_index]["last_post_time"] = published_time
                config["configs"][config_index]["total_item_posted"] += 1
                to_post.append({"channels":post_config["channel_ids"],"link":entry["link"]})
            i -= 1
    config_index += 1

if len(to_post) > 0:
    client = discord.Client(chunk_guilds_at_startup=False)

    @client.event
    async def on_ready():
        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print("------")
        for entry in to_post:
            for channel_id in entry["channels"]:
                channel = client.get_channel(channel_id)
                await channel.send(entry["link"])
        with open(config_file, 'w') as outfile:
            json.dump(config, outfile)
            sys.exit()

    client.run(config["token"])
else:
    with open(config_file, 'w') as outfile:
        json.dump(config, outfile)
        sys.exit()

