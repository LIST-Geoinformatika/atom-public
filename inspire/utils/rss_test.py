import os
from django.conf import settings
from feedgen.feed import FeedGenerator
from inspire.models import RibolovnaPodzona


def generate_ribolovna_podzona_rss_feed():
    # Initialize the feed generator
    fg = FeedGenerator()

    # Set feed metadata
    fg.id("http://example.com")
    fg.title("Ribolovne zone")
    fg.description("INSPIRE rss feed for ribolovne zone")
    fg.link(href="http://example.com", rel="alternate")
    fg.language("en")

    # Query the RibolovnaPodzona instances
    queryset = RibolovnaPodzona.objects.all()

    # Add entries to the feed
    for obj in queryset:
        fe = fg.add_entry()
        fe.id(f"http://example.com/{obj.pk}")
        fe.title(obj.oznaka)
        fe.summary("")
        fe.link(href=f"http://example.com/entry/{obj.pk}", rel="alternate")
        fe.pubDate(obj.added_on.isoformat())

    # Generate the feed as Atom XML
    atom_feed = fg.atom_str(pretty=True)

    # Save the feed to a file
    rss_dir = settings.RSS_DIR
    rss_fpath = os.path.join(rss_dir, "ribolovne_zone.xml")
    with open(rss_fpath, "wb") as f:
        f.write(atom_feed)

    return rss_fpath
