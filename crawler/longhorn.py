import urllib.request
from bs4 import BeautifulSoup

def make_soup(url):
    opener = urllib.request.FancyURLopener({})
    f = opener.open(url)
    content = f.read()
    soup = BeautifulSoup(content,"lxml")
    return soup

if __name__ == "__main__":
    soup = make_soup("https://www.longhornsteakhouse.com/menu-listing/lunch")
    a_tags = soup.findAll(id="menuItemId")

    # Get the links for dish detail pages
    links = []
    for tag in a_tags:
        links.append("https://www.longhornsteakhouse.com"+tag['href'])
    links_set = set({})
    links_temp = []
    for link in links:
        if link not in links_set:
            links_temp.append(link)
            links_set.add(link)
    links = links_temp[1:]

    # Get dish info
    for link in links:
        soup = make_soup(link)

        # Get the dish name and img url
        tag = soup.select(".feature-image.menugrd")[0]
        img_tag = tag.contents[1]
        name = img_tag['title'].replace('*','')
        img = img_tag['src']

        # Get description
        des_tag = soup.select(".dish-desc")[0]
        #print(des_tag)
        description = des_tag.text.strip()
        if description == "":
            description = des_tag.findNext('div').text

        # Get price
        price = ""
        if len(soup.findAll('dd')) != 0:
            price = soup.findAll('dd')[0].text
        else:
            price_tag = soup.select(".detail-rate")[0]
            price = price_tag.text.strip()
            price = price.replace(' ','')
            price = price.replace('\n','')
        price = price.replace('$','')

        # Get calories
        calorie = ""
        nutritions = soup.select(".cal21.marbottom")
        if len(nutritions) == 1:
            calorie = nutritions[0].contents[3].text.strip()

        dish_record = ['"'+name+'"','"'+description+'"',"","",calorie,price,img,"0","2"]
        print(','.join(dish_record))
