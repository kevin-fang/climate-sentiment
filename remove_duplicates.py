links = set()

with open('climate_change_sources.txt', 'r') as f:
	urls = f.read().split("index.html")

for item in urls:
	links.add(item + "index.html")


with open('climate_change_sources.txt', 'w') as f:
	for item in links:
		f.write(item + '\n')