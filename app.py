from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify, Response)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import random
import queries

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
@app.route('/')
def index():
    conn = dbi.connect()
    recipes = queries.getAllRecipes(conn)
    return render_template('main.html', recipes=recipes)

@app.route('/recipe/<rid>')
def recipe_detail(rid):
    conn = dbi.connect()
    recipe = queries.getRecipeById(conn, rid)
    ingredients = queries.getRecipeIngredients(conn, rid)
    instructions = queries.getInstructionsByRecipe(conn, rid)
    for item in ingredients:
        # print(item)
        ingredient_name = queries.getIngredientDetail(conn, item.get('ingredient'))
        # print(ingredient_name)
        item['ingredient_name'] = ingredient_name.get("name")
    return render_template("recipe_detail.html",recipe=recipe, ingredients=ingredients, instructions=instructions)

@app.route('/recipe/', methods=["GET", "POST"])
def recipe_create():
    conn = dbi.connect()
    if request.method == "GET":
        ingredients = queries.getAllIngredients(conn)
        return render_template("recipe_create.html", ingredients=ingredients)
    else:
        print(request.json)
        data = request.json
        title = data.get('title')
        description = data.get('description')
        ingredients = data.get('ingredients')
        instructions = data.get("instructions")
        print(data)

        print(request.form)
        print(ingredients)
        

        recipe_id = queries.insertRecipe(conn, "1", title, description)
        for item in ingredients:
            print(item)
            id = queries.insertQuantity(conn, recipe_id, item['iid'], item['quantity'], item['unit'])
            print(id)
        for i in range(len(instructions)):
            id = queries.insertInstruction(conn, recipe_id, i, instructions[i])
            print(id)

        return redirect(url_for("recipe_detail", rid=recipe_id))


@app.route('/ingredient/')
def ingredient():
    conn = dbi.connect()
    ingredients = queries.getIngredients(conn, 10)
    return render_template('ingredient_list.html', ingredients=ingredients)

@app.route('/ingredient_create/', methods=['POST'])
def ingredient_create():
    if ('name' in request.form and 'cost' in request.form):
        print(request.form)
        name = request.form['name']
        cost = float(request.form['cost'])
        conn = dbi.connect()
        id = queries.insertIngredient(conn,name=name,cost=cost)
        # id = queries.insertIngredient
        return redirect(url_for('ingredient_detail',iid=id))

@app.route('/ingredient/<iid>')
def ingredient_detail(iid):
    print(iid)
    conn = dbi.connect()
    ingredient = queries.getIngredientDetail(conn, iid)
    print(ingredient)
    return render_template('ingredient_detail.html', ingredient=ingredient)

@app.route('/lookup/')
def ingredient_search():
    conn = dbi.connect()
    name = request.args.get('name')
    print(name)
    results = queries.searchIngredient(conn, name)
    print(results)
    return jsonify(results=results)


@app.before_first_request
def init_db():
    dbi.cache_cnf()

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)

