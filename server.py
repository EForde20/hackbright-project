""" Flask site for project app."""

from flask import Flask, render_template, request, session
from flask_debugtoolbar import DebugToolbarExtension
from model import search_recipes, recipe_info_by_id, determine_base_unit
from model import User
from model import Recipe
from model import ShoppingList
from model import ListIngredient
from model import Ingredient
from model import connect_to_db, db
from jinja2 import StrictUndefined
from sqlalchemy.sql import func

import os

app = Flask(__name__)

app.secret_key = os.environ["secretkey"]

# Raises an error if an undefined variable is used in Jinja2
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def homepage():
    """Display homepage."""

    return render_template("homepage.html")


@app.route("/inventory", methods=["GET", "POST"])
def show_inventory():
    """ Display user's current ingredients."""

    # if user is searching again for recipes, session is still active
    if session['user_id']:
        current_ingredients = []
        return render_template("inventory.html", current_ingredients=current_ingredients)

    username = request.form.get("username")
    password = request.form.get("password")

    check_user = User.query.filter(User.username == username, User.password == password).first()

    if check_user:
        # user begins with no inventory
        session['user_id'] = check_user.user_id
        current_ingredients = []
        return render_template("inventory.html", current_ingredients=current_ingredients)
    else:
        return render_template("/homepage.html")


@app.route("/recipes")
def show_matching_recipes():
    """ Display recipes using the ingredient selected."""

    diet = request.args.get("diet")
    intolerances = request.args.getlist("intolerances")
    numresults = request.args.get("numresults")
    query = request.args.get("query")

    intolerances = "%2C+".join(intolerances)

    recipe_info = search_recipes(diet, intolerances, numresults, query)

    return render_template("recipes.html", recipe_info=recipe_info)


@app.route("/shopping_list", methods=["POST"])
def show_shopping_list():
    """Display shopping list of missing ingredients."""

    recipe_ids = request.form.getlist("recipeid")

    # dictionary for multiple recipes selected
    # key: ingredient name
    # value: {quantity: __, base unit: __}
    # aggregated_ingredients = {}

    for recipe_id in recipe_ids:
        all_rec = db.session.query(Recipe.recipe_id).all()
        recipe = recipe_info_by_id(recipe_id)
        if (int(recipe['id']),) not in all_rec:  
            selected_recipe = Recipe(recipe_id=int(recipe['id']),
                                     user_id=int(session['user_id']),
                                     )
            db.session.add(selected_recipe)
        
        # for ingredient in recipe['extendedIngredients']:

    #         all_ing = db.session.query(Ingredient.ingredient_id).all()
    #         if (int(ingredient['id']),) not in all_ing:

    #             base_unit = determine_base_unit(str(ingredient['unit'])
    #             recipe_ingredient = Ingredient(ingredient_id=int(ingredient['id']),
    #                                            ingredient_name=str(ingredient['name']),
    #                                            ingredient_unit=base_unit),
    #                                            )
    #             db.session.add(recipe_ingredient)

    #         recipe_quantity = RecipeIngredient(recipe_id=int(recipe['id']),
    #                                            ingredient_id=int(ingredient['id']),
    #                                            quantity=float(ingredient['amount']),
    #                                            )
    #         db.session.add(recipe_quantity)

    # db.session.commit()

    # ingredients = (db.session.query(func.sum(RecipeIngredient.quantity),
    #                                 Ingredient.ingredient_unit,
    #                                 Ingredient.ingredient_name)
    #                          .join(Ingredient)
    #                          .join(Recipe)
    #                          .join(User)
    #                          .filter(User.user_id == session['user_id'])
    #                          .group_by(Ingredient.ingredient_unit, Ingredient.ingredient_name)
    #                          .order_by(Ingredient.ingredient_name)).all()

    # dummy ingredients for testing
    ingredients = [(2, 'ounces', 'onions'), (1, 'pound', 'chicken')]

    return render_template("shopping.html", ingredients=ingredients)



if __name__ == "__main__":
    # the toolbar is only enabled in debug mode:
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")