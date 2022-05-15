import feedparser
import re
import datetime
from fuzzywuzzy import fuzz


data_breach_feed = feedparser.parse('https://www.google.com/alerts/feeds/18070363048132599199/7339667243533064652')

# seen = set()
# result = []
# for item in sorted(data):
#     key = int(item)  # or whatever condition
#     if key not in seen:
#         result.append(item)
#         seen.add(key)


seen = set()
array=[]
for item in data_breach_feed.entries:
    key = item.title
    similar = 0
    for i in seen:
        similarity = fuzz.token_set_ratio(key.lower(),i.lower())
        if similar < similarity:
            similar = similarity
    if similar < 90:
        array.append(item)
        seen.add(key)

for i in array:
    print(i.title)


# for item in data_breach_feed.entries:
#     start_substring= "https://www.google.com/url?rct=j&sa=t&url="
#     link=item.link.replace(start_substring,'')
#     end_substring = re.findall(r'\&ct\=ga\&cd=CAIyG.*', link)
#     link=link.replace(end_substring[0],'')
#     published_day=datetime.datetime.strptime(item.published, "%Y-%m-%dT%H:%M:%SZ")
#     print(published_day,item.title,'\n',link,'\n',item.content[0]['value'],'\n\n')
