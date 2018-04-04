import ssl
import urllib.request
from bs4 import BeautifulSoup


class Dish:
    def __init__(self):
        self.DIN = default
        self.name = default
        self.description = default
        self.ingredient = default
        self.category = default
        self.calorie = default
        self.img = default
        self.price = default
        self.score = 0
        self.RIN = default
        self.restaurant = "Red Lobster"

    def print_dish(self):
        print('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' %
              (self.DIN, self.name, self.description, self.ingredient, self.category, self.calorie, self.price, self.img, self.score, self.RIN, self.restaurant))


def make_soup(url):
    f = urllib.request.urlopen(url)
    content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    return soup


def select_one(obj, tag):
    ret = obj.select(tag)
    if len(ret) == 1:
        return ret[0]
    else:
        return default


def update_dish(ds):
    name = "\"" + select_one(ds, "h2").text.strip() + "\""  # must exist
    if name in dish_list:
        dish_list[name].img = domain + select_one(ds, "img").get('src')
    else:
        d = Dish()
        d.name = name
        description = select_one(ds, "p").text.split("\n")
        d.description = "\"" + description[0] + "\""
        if len(description) > 1:
            d.calorie = description[1][:-4]
        d.img = domain + select_one(ds, "img").get('src')
        d.category = "Specials"
        dish_list[name] = d

ssl._create_default_https_context = ssl._create_unverified_context

domain = "https://www.redlobster.com"

default = ""
default_img = "https://static.olocdn.net/menu/redlobster/73593a27983ec402d3c3f7babb796f68.jpg"

dish_list = {}

################################
# Order Page: Create dish list #
################################

soup = BeautifulSoup(open("redlobster_order.html"), "html.parser")

# category
cat_src = soup.select("h3")[:-1]  # remove gift card
cat_list = [s.text for s in cat_src]

# dish
dish_all_src = soup.select("#ProductList > .Products")[:-1]  # remove gift card
for i, das in enumerate(dish_all_src):
    dish_src = das.select("li")
    for ds in dish_src:
        d = Dish()
        img = select_one(ds, ".product__image").get('src')
        if img is None or img == default_img:  # default image
            continue
        d.name = "\"" + select_one(ds, ".product__name").text + "\""  # must exist
        description = select_one(ds, ".product__description") \
            .get_text(separator="||").split('||')  # must exist
        if description[0].strip()[-4:] == " Cal":  # no description
            d.calorie = description[0].strip()[:-4]
        else:
            d.description = "\"" + description[0].strip() + "\""
            if len(description) > 1:
                d.calorie = description[1].strip()[:-4]
        d.category = cat_list[i]
        d.price = select_one(ds, ".product__attribute--price")
        if d.price != default:
            d.price = d.price.text[1:]  # remove $
        d.img = img
        dish_list[d.name] = d

######################
# Menu Page: Special #
######################

soup = make_soup("https://www.redlobster.com/menu/specials")

dish_src = soup.select(".medium-4")
for ds in dish_src:
    update_dish(ds)

#####################
# Menu Page: Others #
#####################

# tab_list = ["/dinner", "/lunch", "/kids"]
#
# for tab in tab_list:
#     soup1 = make_soup(domain + "/menu" + tab)
#     # print(soup1)
#     dish_src = soup1.select(".menu-item-detail")
#     for ds in dish_src:
#         if ds.get('href') is not None:
#             soup2 = make_soup(ds.get('href'))
#     print(len(dish_src))
#     break
#
# dish_src = soup.select(".medium-4")
# for ds in dish_src:
#     update_img(select_one(ds, "h2").text, domain + select_one(ds, "img").get('src'))  # all false ...

###################
# Manually Update #
###################

# update_img("Lobster Lover&rsquo;s Dream®", domain +
        #    "/images/default-source/images/events/2018/event-6-lobsterfest/favorites-chef-pairing/lobsterlovers")

##############
# Print Dish #
##############

# header. debug purpose
print("DIN,name,description,ingredient,category,calorie,price,img,score,RIN,restaurant")

for name in dish_list:
    dish_list[name].print_dish()
