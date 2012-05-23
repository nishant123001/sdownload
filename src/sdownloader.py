import sys
from urllib2 import Request, HTTPError, URLError, urlopen
from httplib import InvalidURL
import urlparse, re, urllib, logging, StringIO, logging
from BeautifulSoup import BeautifulSoup
from optparse import OptionParser, SUPPRESS_HELP

chunk_size = 1024

def clean_url(url):
    """url quotes unicode data out of urls"""
    s = url
    url = url.encode('utf8')
    url = ''.join([urllib.quote(c) if ord(c) >= 127 else c for c in url])
    return url


def fetch_url(url, referer = None, retries = 1, dimension = False):
    cur_try = 0
    print('fetching: %s' % url)
    nothing = None if dimension else (None, None)
    url = clean_url(url)
    #just basic urls
    if not url.startswith('http://'):
        return nothing
    while True:
        try:
            req = Request(url)
            open_req = urlopen(req)

            #if we only need the dimension of the image, we may not
            #need to download the entire thing
            if dimension:
                content = open_req.read(chunk_size)
            else:
                content = open_req.read()
            content_type = open_req.headers.get('content-type')

            if not content_type:
                return nothing

            if 'image' in content_type:
                p = ImageFile.Parser()
                new_data = content
                while not p.image and new_data:
                    p.feed(new_data)
                    new_data = open_req.read(chunk_size)
                    content += new_data

                #return the size, or return the data
                if dimension and p.image:
                    return p.image.size
                elif dimension:
                    return nothing
            elif dimension:
                #expected an image, but didn't get one
                return nothing

            return content_type, content

        except (URLError, HTTPError, InvalidURL), e:
            cur_try += 1
            if cur_try >= retries:
                print('error while fetching: %s referer: %s' % (url, referer))
                print(e)
                return nothing
        finally:
            if 'open_req' in locals():
                open_req.close()

class Songpk(object):
	def __init__(self, url):
		self.url = url
	
	def scrapFPage(self):
		link_html =  fetch_url(self.url)
		self.soup = BeautifulSoup(link_html[1])
		tags = self.soup.findAll(lambda tag:tag.get("class") == "adorangeline")
		print tags

def run(options, args):
	song = Songpk(options.url)
	import rpdb2
	rpdb2.start_embedded_debugger('nky')
	links = song.scrapFPage()

def main(argv):
	options, args = parse_args(argv)
	run(options, args)

def parse_args(argv):
	parser = OptionParser()
	parser.add_option("-u", "--url", action="store", type="string", dest="url",
					  default= '', help=SUPPRESS_HELP)
	options, args = parser.parse_args(argv)

	return (options, args[1:])


if __name__ == "__main__":
	main(sys.argv)
