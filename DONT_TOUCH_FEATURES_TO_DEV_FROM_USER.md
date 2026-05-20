NEW FEATURES REQUESTS FROM USER
1. 将其程序运行所需的资源与主程序逻辑解耦（decoupling).we don't want to compile and build the whole app hot while it's serving as a webapp. but we can hot update its:
(1) Providers (sites like nyaa.si, tpb.party, etc)
(2) Extraction of [URL to torrents] and [magnetlinks]
(3) Other resources which might have been hard-codedly written within.
 
for maximum flexibility and availability.

2. validity check and seeding quality check
SINCE we'll partially take over the extraction part, so we need to first do a validity check to see what we get are legal in form, to see if it's a legal torrent/a magnet link/ an infohash.

Then the seeding quality check.

3. Sequential downloading for torrent-to-stream feature
4. Seems the old torrenting engine works stable and fine. Don't change it unless it can't satisfies other needs.
5. New feature: download a specific episodic file from a torrent/infohash/megnetlink (or seeds, collectively) for whole season, or for a collection
6. Absolute Transparent debugging info. According to our philosophy, Dev State > Runtime State, and the goal is to make Dev State = Runtime State. So now we make debugging info transparent to the runtime state. And the goal is to let the user know the webapp is working.  
