import urllib.request
from bs4 import BeautifulSoup

def make_soup(url):
    opener = urllib.request.FancyURLopener({})
    f = opener.open(url)
    content = f.read()
    soup = BeautifulSoup(content,"lxml")
    return soup

def parse_page(category):
    # Get the category url
    url = "http://www.perkinsrestaurants.com/menu/"+category
    soup = make_soup(url)
    entries = soup.select(".menu-item-wrapper")

    sublinks = []
    for entry in entries:
        sublinks.append("http://www.perkinsrestaurants.com"+entry.contents[1]['href'])


    dishes = []
    for link in sublinks:
        soup = make_soup(link)
        entries = soup.select(".col-xs-12.col-sm-6.col-md-4.menu-listing-custom")
        for i in range(len(entries)):
            try:
                entry_list = entries[i].contents
                if(len(entry_list) == 0):
                    continue
                if (len(entry_list[0].contents) == 0):
                    continue
                name = entry_list[1].text.strip().replace('*','')
                description = entry_list[2].text.strip().replace('*','')
                img = entry_list[0].contents[0]['src'].strip().replace('*','')
                dishes.append(['"'+name+'"','"'+description+'"',"",category,"","",img,"0","1"])
            except:
                pass
    return dishes


if __name__ == "__main__":

    # Parse all dishes
    dishes = []
    dishes += parse_page("breakfast")
    dishes += parse_page("lunch-and-dinner")
    dishes += parse_page("bakery")

    # Print out the dishes
    for dish in dishes:
        print(','.join(dish))
