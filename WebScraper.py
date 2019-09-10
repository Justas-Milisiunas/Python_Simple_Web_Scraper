import requests
import threading
import time
import json
import uuid
import urllib
import os.path
from bs4 import BeautifulSoup
from Recipe import Recipe
from Product import Product
from Step import Step
from Photo import Photo
from Tag import Tag
import re

new_recipes = []
recipes_with_watermarks = 0


def save_to_file(recipes):
    f = open("json_jump.json", "a")
    dump = json.dumps(recipes)
    f.write(dump)
    f.close()


def scrape_page(page_link):
    page_reponse = requests.get(page_link)
    page_soup = BeautifulSoup(page_reponse.text, "html.parser")

    try:
        image_url = page_soup.select_one(".recipeGallerySegment .bigImg img")['src']

        if "without-watermark" not in image_url:
            global recipes_with_watermarks
            recipes_with_watermarks += 1
            return

        recipe_title = page_soup.select_one(".recipeTitleSegment h1").text.strip()
        before_split = page_soup.select_one(".method .info .info").text.strip()

        recipe_preparation_time = int(re.findall("\d+", before_split)[0])
        if "min" in before_split:
            recipe_preparation_time = int(60 * recipe_preparation_time)
        elif "val" in before_split:
            recipe_preparation_time = int(60 * 60 * recipe_preparation_time)
        recipe_portion_amount = page_soup.select_one(".info").text.strip()
        if len(recipe_portion_amount) is 0:
            recipe_portion_amount = int(4)
        else:
            recipe_portion_amount = int(re.findall("\d+", recipe_portion_amount)[0])

        recipe_description = ''
        try:
           recipe_description = page_soup.select_one(".authorsDescription").text.strip()
        except AttributeError:
            recipe_description = ''
            print('No description')

        amounts = page_soup.select(".ingredients .infoA table tr")
        recipe_products = []
        for amount in amounts:
            cells = amount.select("td")
            if len(cells) is 1:
                continue
            quantity = cells[0].text.strip()
            product_name = cells[1].text.strip()[0:30].strip()
            new_product = Product(product_name, quantity)
            recipe_products.append(new_product.__dict__)

        steps = page_soup.select(".infoA .description")
        recipe_steps = []
        for step in steps:
            step_text = step.select_one(".text")
            # print(step_text.text)
            new_step = Step(step_text.text)
            recipe_steps.append(new_step.__dict__)

        recipe_view_count = int(0)
        recipe_rating = int(0)
        recipe_votes_count = int(0)

        image_extension = image_url.split('.')[-1]
        image_fileName = ''
        image_name = ''
        while True:
            image_name = uuid.uuid4().hex
            image_fileName = image_name + "." + image_extension
            if not os.path.isfile("Photos/" + image_fileName):
                break;


        opener = urllib.request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405')
        opener.retrieve(image_url, "Photos/" + image_fileName)
        # urllib.request.urlretrieve(image_url, "Photos/" + image_fileName)

        recipe_image = Photo(image_fileName)
        recipe_images = []
        recipe_images.append(recipe_image.__dict__)

        # Tags
        recipe_tags = []
        temp = Tag("grilio patiekalai")
        recipe_tags.append(temp.__dict__)

        tags = page_soup.select(".guidelinesSegment a")
        for tag in tags:
            if not "lamaistas" in tag.text:
                new_tag = Tag(tag.text)
                recipe_tags.append(new_tag.__dict__)

        new_recipe = Recipe(recipe_title, recipe_products, recipe_steps,
                            recipe_portion_amount, recipe_preparation_time,
                            recipe_description, recipe_view_count, recipe_rating,
                            recipe_votes_count, recipe_images, recipe_tags)
        new_recipes.append(new_recipe.__dict__)
        print("Saved " + page_link + " " + str(len(new_recipes)))
    except Exception as e:
        print("Error " + str(e) + " || " + page_link)


url = "https://www.lamaistas.lt/receptai/grilio-patiekalai/200"
response = requests.get(url)

print(response)

soup = BeautifulSoup(response.text, "html.parser")
current_time = uuid.uuid4().hex


page_links = soup.select(".frame a")
threads = []
for link in page_links:
    # time.sleep(0.25)
    if "https://www.lamaistas.lt/receptas" in link["href"]:
        thread = threading.Thread(target=scrape_page, args=(link["href"],))
        threads.append(thread)
        thread.start()
        # thread.join()
        # new_recipe = scrape_page(link["href"])

for thread in threads:
    thread.join()

# recipe = scrape_page('https://www.lamaistas.lt/receptas/braskinis-zele-pyragas-57475')

# print(new_recipes.__dict__)
print("Saved recipes: " + str(len(new_recipes)) + " With watermarks: " + str(recipes_with_watermarks))
save_to_file(new_recipes)
print("Issaugota")
