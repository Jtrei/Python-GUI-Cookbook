import os, bs4, requests

website_title_html_info = {"tasteofhome": ['h1', 'recipe-title']}
website_ingredient_html_info = {"tasteofhome": ['ul', 'recipe-ingredients__list recipe-ingredients__collection splitColumns', 'li'],}

website_name = {'tasteofhome': 0}

class Scraper:
    def __init__(self, url):
        self.title = ''
        self.ingredients = []

        self.url = url
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response.raise_for_status()
        except ConnectionError:
            print("Error")

        self.soup = bs4.BeautifulSoup(response.text, features="html.parser")
        
    def scrape_recipe(self):
        for k, v in website_name.items():
            if k in self.url:
                # Title
                parent_heading, class_name = website_title_html_info[k][0], website_title_html_info[k][1]
                for element in self.soup.find_all(parent_heading, class_=class_name):
                    self.title
                # Ingredients
                parent_heading, class_name, child_heading = website_ingredient_html_info[k][0], website_ingredient_html_info[k][1],website_ingredient_html_info[k][2]
                for element in self.soup.find_all(parent_heading, class_=class_name):
                    for child_heading in element:
                        self.ingredients.append(child_heading.get_text())

#crape = Scraper('https://www.tasteofhome.com/recipes/best-ever-potato-soup/')
#crape.scrape_recipe()


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


