#! python3.8
# WebExtraction.py - This program will collect recipes on a given page

import os, bs4, requests

# Initialization of Iterator elements, Web_recipe class object, and Recipe Storage Directory
elements = 0
#Web_recipe = Recipe('', '', '', '', '', '', '', '', '', '', '', '')

def obtain_website_to_scrape():
    website = input("Please paste website link to extract recipe (omit - https://www.): ")
    website = f"https://www.{website}"
    res = requests.get(website)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features="html.parser")
    return website

def CleanAndPresentVariables(ListOrString):
    return ListOrString
# All htmlParsing definitions are defined by the element and class name -> i.e. H1 for 'h1', C for class, etc...

def H1_C_ParseString(html_class):
    global elements, soup
    elementSearch = soup.find('h1', {'class': html_class})
    for i in elementSearch:
        a = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
    elements += 1
    a = CleanAndPresentVariables(a)
    return a
def div_C_ParseString(html_class):
    global elements, soup
    elementSearch = soup.find('div', {'class': html_class})
    for i in elementSearch:
        a = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
    elements += 1
    a = CleanAndPresentVariables(a)
    return a
def div_C_ParseList(html_class):
    global elements, soup
    a = []
    elementSearch = soup.find('div', {'class': html_class})
    for i in elementSearch:
        b = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
        a.append(b)
    elements += 1
    print(a)
    a = CleanAndPresentVariables(a)
    return a
def ul_C_ParseList(html_class):
    global elements, soup
    a = []
    elementSearch = soup.find("ul", {"class": html_class})
    for i in elementSearch:
        b = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
        a.append(b)
    elements += 1
    a = CleanAndPresentVariables(a)
    return a
def span_C_ParseString(html_class):
    global elements, soup
    elementSearch = soup.find('span', {'class': html_class})
    for i in elementSearch:
        a = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
    elements += 1
    return CleanAndPresentVariables(a)
def li_C_ParseList(html_class):
    global elements, soup
    a = []
    elementSearch = soup.find_all("li", {"class": html_class})
    for i in elementSearch:
        b = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
        a.append(b)
    elements += 1
    print(a)
    a = CleanAndPresentVariables(a)
    print(a)
    return a
def label_C_ParseList(html_class):
    global elements, soup
    a = []
    elementSearch = soup.find_all("label", {"class": html_class})
    for i in elementSearch:
        b = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
        a.append(b)
    elements += 1
    a = CleanAndPresentVariables(a)
    return a
def span_C_ParseList(html_class):
    global elements, soup
    a = []
    elementSearch = soup.find_all("span", {"class": html_class})
    for i in elementSearch:
        b = bs4.BeautifulSoup(str(i), features="html.parser").get_text()
        a.append(b)
    elements += 1
    a = CleanAndPresentVariables(a)
    return a

def taste_of_home(Web_recipe):
    global elements
    elements = 0
    html_class = ["recipe-title",
                  "recipe-time-yield__label-servings",
                  "recipe-nutrition-facts mobile-expand-section",
                  "recipe-ingredients__list recipe-ingredients__collection",
                  "recipe-directions__list"]
    try:
        Web_recipe.title = H1_C_ParseString(html_class[elements])
        Web_recipe.servings = div_C_ParseString(html_class[elements])
        Web_recipe.serving_size = div_C_ParseList(html_class[elements])
        Web_recipe.ingredients = ul_C_ParseList(html_class[elements])
        Web_recipe.directions = ul_C_ParseList(html_class[elements])
    except:
        pass
def serious_eats(Web_recipe):
    global elements
    elements = 0
    html_class = ["title recipe-title",
                  "info yield",
                  "ingredient",
                  "recipe-procedure-text"]
    try:
        Web_recipe.title = H1_C_ParseString(html_class[elements])
        Web_recipe.servings = span_C_ParseString(html_class[elements])
        try:
            Web_recipe.ingredients = ul_C_ParseList(html_class[elements])
        except:
            Web_recipe.ingredients = li_C_ParseList(html_class[elements])
        Web_recipe.directions = div_C_ParseList(html_class[elements])
    except:
        pass


def all_recipes(Web_recipe):
    global elements
    elements = 0
    html_class = ["recipe-summary__h1",
                  "servings-count",
                  "nutrition-summary-facts",
                  "checkList__line",
                  "recipe-directions__list--item"]
    try:
        Web_recipe.title = H1_C_ParseString(html_class[elements])
        Web_recipe.servings = span_C_ParseString(html_class[elements])
        Web_recipe.serving_size = div_C_ParseList(html_class[elements])
        Web_recipe.ingredients = li_C_ParseList(html_class[elements])
        Web_recipe.directions = span_C_ParseList(html_class[elements])
        print(Web_recipe.title)
    except:
        pass

def add_recipe_scraping(rec_id, website_name, title, cuisine, cook_time, servings, serving_size,
                        ingredients, directions, nutrition_info, notes, picture):
        username = get_current_username()
        # TODO: Check to make sure recipe title is unique
        with open(picture, 'rb') as temp:
            with open(f'{UserDatabaseFileDirectory}\\Pictures\\{title}.png', 'wb') as perm:
                perm.write(temp.read())
        food_photo = f'{UserDatabaseFileDirectory}\\Pictures\\{title}.png'
        connection = sqlite3.connect(f'{UserDatabaseFileDirectory}\\{username}.db')
        cur = connection.cursor()
        cur.execute(f'''INSERT INTO {username}_Recipes VALUES 
                    (:rec_id, :website_name, :title, :cuisine, :cook_time, :servings, :serving_size, 
                     :ingredients, :directions, :nutrition_info, :notes, :picture)''',
                    {'rec_id': rec_id, 'website_name': website_name, 'title': title, 'cuisine': cuisine,
                     'cook_time': cook_time,
                     'servings': servings, 'serving_size': serving_size, 'ingredients': ingredients,
                     'directions': directions,
                     'nutrition_info': nutrition_info, 'notes': notes, 'picture': food_photo})
        connection.commit()
        connection.close()
        print("Recipe Added!")


def MainExtraction():
    collection_of_websites = {'tasteofhome': taste_of_home(Web_recipe),
                              'seriouseats': serious_eats(Web_recipe),
                              'allrecipes': all_recipes(Web_recipe)}
    website = obtain_website_to_scrape()
    for keys, values in collection_of_websites.items():
        if keys in website:
            Web_recipe.Website_Name = keys
            collection_of_websites[keys]
    add_recipe_scraping(Recipe.rec_id, Recipe.website_name, Recipe.title, Recipe.cuisine, Recipe.cook_time, Recipe.servings,
                        Recipe.serving_size, Recipe.ingredients, Recipe.directions, Recipe.nutrition_info,
                        Recipe.notes, Recipe.picture)


