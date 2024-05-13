import os

from django.conf import settings
from feedgen.feed import FeedGenerator
from inspire.models import RibolovnaPodzona


class InspireRssFeed:
    def __init__(self):
        self.rss_dir = settings.RSS_DIR

    def ribolovne_zone_to_rss(self, queryset=None):
        if not queryset:
            queryset = RibolovnaPodzona.objects.all()

        # Create a new feed generator
        fg = FeedGenerator()

        # Set the required metadata for the feed
        fg.id("http://example.com")
        fg.title("Ribolovne zone")
        fg.subtitle("")
        fg.description("INSPIRE rss feed for ribolovne zone")
        fg.link(href="http://example.com", rel="alternate")
        fg.language("en")

        # Add an entry to the feed
        for obj in queryset:
            fe = fg.add_entry()
            fe.id("http://example.com/entry1")
            fe.title(obj.oznaka)
            fe.summary("")
            fe.link(href="http://example.com/entry1", rel="alternate")
            fe.pubDate(obj.added_on.isoformat())

        # Generate the feed as Atom XML
        atom_feed = fg.atom_str(pretty=True)

        # Save the feed to a file
        rss_fpath = os.path.join(self.rss_dir, "ribolovne_zone.xml")
        with open(rss_fpath, "wb") as f:
            f.write(atom_feed)

        return rss_fpath

    def generate_all(self):
        self.ribolovne_zone_to_rss()
