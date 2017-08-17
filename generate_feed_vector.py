import feedparser
import re


def get_word_counts(url):
    """Return title and dictionary of words from an RSS feed."""
    # Parse feed
    d = feedparser.parse(url)
    wc = {}

    # Loop over entries
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description

        # Extract list of words
        words = get_words(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
        return d.feed.title, wc


def get_words(html):
    """Strips words from html."""

    # Remove all html tags
    txt = re.compile(r'<[^>]+>').sub('', html)

    # Split words by all non-alpha chars
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    # Convert to lowercase
    return [word.lower() for word in words if word != '']


if __name__ == '__main':
    apcount = {}
    wordcounts = {}
    with open('feedlist.txt') as f:
        for feedurl in f.readlines():
            title, wc = get_word_counts(feedurl)
            wordcounts[title] = wc
            for word, count in wc.items():
                apcount.setdefault(word, 0)
                if count > 1:
                    apcount[word] += 1
    wordlist = []
    for w, bc in apcount.items():
        frac = float(bc) / len(feedlist)
        if frac > 0.1 and frac < 0.5:
            wordlist.append(w)

    out = file('blogdata.txt', 'w')
    out.write('Blog')
    for word in wordlist:
        out.write('\t{word}')
        out.write('\n')
    for blog, wc in wordcounts.items():
        out.write(blog)
        for word in wordlist:
            if word in wc:
                out.write('\t{wc[word]}')
            else:
                out.write('\t0')
        out.write('\n')
