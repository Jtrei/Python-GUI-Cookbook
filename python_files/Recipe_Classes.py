class Recipe:
    def __init__(self):
        pass

    def input(self, website_name, title, cuisine, cook_time, servings, serving_size, ingredients, directions,
                 nutrition_info, notes, picture):
        self.rec_id: int = 0
        self.website_name: str = website_name
        self.title: str = title
        self.cuisine: str = cuisine
        self.cook_time: int = cook_time
        self.servings: int = servings
        self.serving_size: int = serving_size
        self.ingredients: str = ingredients
        self.directions: str = directions
        self.nutrition_info: str = nutrition_info
        self.notes: str = notes
        self.picture: str = picture

    def __repr__(self):
        recipe_string = f'''
        'rec_ID':{self.rec_id}, 
        'website':{self.website_name}, 
        'title':{self.title}, 
        'cuisine':{self.cuisine}, 
        'cook_time':{self.cook_time}, 
        'servings':{self.servings}, 
        'serving_size':{self.serving_size}, 
        'ingredients':{self.ingredients}, 
        'directions':{self.directions},
        'nutrition_info':{self.nutrition_info}, 
        'Notes':{self.notes},
        'Picture':{self.picture}'''
        return  recipe_string   

    def add(self, rec_id, website_name, title, cuisine, cook_time, servings, serving_size, ingredients, directions,
             nutrition_info, notes, picture):
        pass

    def file_writer(self, file_name, *arg, **kwarg):
        with open(file_name, 'w') as RecipeWriter:
            RecipeWriter.write(f''' Recipe Identifier: {kwarg}
                                    Website title: {self.website_name}
                                    Recipe title: {self.title}

                                    Cuisine type: {self.cuisine}

                                    Servings: {self.servings}
                                    Serving Size: {self.serving_size}
                                    Cook time: {self.serving_size} minutes
                                    Nutrition info: 
                                    {self.nutrition_info}

                                    Ingredients: 
                                    {self.ingredients}

                                    Directions: 
                                    {self.directions}
                                    
                                    Notes: 
                                    {self.Notes}
                                                ''')
    