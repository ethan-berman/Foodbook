from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify, Response)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import random
import queries
import bcrypt
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
    page_title = "Foodbook"
    return render_template('main.html', recipes=recipes, page_title=page_title)

@app.route('/join/', methods=["GET", "POST"])
def join():
    if request.method == "GET":
        page_title = "Foodbook | Sign up"
        return render_template("join.html",page_title=page_title)
    else:
        try:
            username = request.form['username']
            email = request.form['email']
            passwd1 = request.form['password1']
            passwd2 = request.form['password2']
            if passwd1 != passwd2:
                flash('passwords do not match')
                return redirect( url_for('index'))
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
            print(passwd1, hashed)
            conn = dbi.connect()
            curs = dbi.cursor(conn)
            try:
                curs.execute('''INSERT INTO user(uid,username,password,email)
                                VALUES(null,%s,%s,%s)''',
                            [username, hashed,email])
                conn.commit()
            except Exception as err:
                flash('That username is taken: {}'.format(repr(err)))
                return redirect(url_for('index'))
            curs.execute('select last_insert_id()')
            row = curs.fetchone()
            uid = row[0]
            flash('FYI, you were issued UID {}'.format(uid))
            session['username'] = username
            session['uid'] = uid
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('user', username=username) )
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )
        
@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        page_title = "Foodbook | Login"
        return render_template("login.html", page_title=page_title)
    else:
        try:
            username = request.form['username']
            passwd = request.form['password']
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''SELECT uid,password
                        FROM user
                        WHERE username = %s''',
                        [username])
            row = curs.fetchone()
            if row is None:
                # Same response as wrong password,
                # so no information about what went wrong
                flash('login incorrect. Try again or join')
                return redirect( url_for('index'))
            hashed = row['password']
            hashed2 = bcrypt.hashpw(passwd.encode('utf-8'), hashed.encode('utf-8'))
            print('rehash is: {} {}'.format(hashed2, type(hashed2)))
            if hashed2.decode('utf-8') == hashed:
                print('They match!')
                flash('successfully logged in as '+username)
                session['username'] = username
                session['uid'] = row['uid']
                session['logged_in'] = True
                session['visits'] = 1
                return redirect( url_for('user', username=username) )
            else:
                print('They don\'t match.')
                flash('login incorrect. Try again or join')
                return redirect( url_for('index'))
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )


@app.route('/user/<username>')
def user(username):
    conn = dbi.connect()
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            uid = session['uid']
            recipes = queries.getRecipesByUser(conn, uid)
            session['visits'] = 1+int(session['visits'])
            return render_template('user.html',
                                   page_title='Foodbook: Welcome {}'.format(username),
                                   name=username,
                                   uid=uid,
                                   visits=session['visits'],
                                   recipes=recipes)

        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('uid')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('index'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/recipe/<rid>')
def recipe_detail(rid):
    # Detail view for recipe, includes the OP and reviews and their authors
    conn = dbi.connect()
    recipe = queries.getRecipeById(conn, rid)
    author = queries.getAuthor(conn, rid)
    ingredients = queries.getRecipeIngredients(conn, rid)
    instructions = queries.getInstructionsByRecipe(conn, rid)
    reviews = queries.getReviewsByRecipe(conn, rid)
    page_title = "Foodbook | {}".format(recipe.get('name'))
    for item in reviews:
        poster = queries.getReviewAuthor(conn, item['revid'])
        item['author'] = poster
    for item in ingredients:
        ingredient_name = queries.getIngredientDetail(conn, item.get('ingredient'))
        item['ingredient_name'] = ingredient_name.get("name")
    return render_template("recipe_detail.html",page_title=page_title, recipe=recipe, ingredients=ingredients, instructions=instructions, author=author, reviews=reviews)

@app.route('/recipe/', methods=["GET", "POST"])
def recipe_create():
    conn = dbi.connect()
    try:
        if 'username' in session:
            if request.method == "GET":
                ingredients = queries.getAllIngredients(conn)
                page_title = "Foodbook | Create Recipe"
                return render_template("recipe_create.html", ingredients=ingredients,page_title=page_title)
            else:
                #Handle new ingredient insert
                data = request.json
                #get params
                title = data.get('title')
                description = data.get('description')
                ingredients = data.get('ingredients')
                instructions = data.get("instructions")
                uid = session['uid']
                # reduce to boolean
                isTitle = len(title) == 0
                isDescription = len(description) == 0
                isIngredients = len(ingredients) == 0
                isInstructions = len(instructions) == 0
                #validate inputs
                if (isTitle or isDescription or isIngredients or isInstructions):
                    flash("Missing data!")
                    # have to jsonify because this is jquery request, regular redirect wont work
                    return jsonify({"redirect":url_for("recipe_create")})
                    # return redirect(url_for("recipe_create"))
                #Input valid, insert new entry
                recipe_id = queries.insertRecipe(conn, uid, title, description)
                for item in ingredients:
                    print(item)
                    id = queries.insertQuantity(conn, recipe_id, item['iid'], item['quantity'], item['unit'])
                    print(id)
                for i in range(len(instructions)):
                    id = queries.insertInstruction(conn, recipe_id, i, instructions[i])
                    print(id)

                # have to jsonify because jquery request
                return jsonify({"redirect": url_for("recipe_detail", rid=recipe_id)})
        else:
            flash('you are not logged in. Please login or Sign up.')
            return redirect(url_for('index'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))


@app.route('/ingredient/')
def ingredient():
    # Get first x ingredients and list them
    conn = dbi.connect()
    ingredients = queries.getIngredients(conn, 10)
    page_title = "Foodbook | Ingredients"
    return render_template('ingredient_list.html', ingredients=ingredients,page_title=page_title)

@app.route('/ingredient_create/', methods=['POST'])
def ingredient_create():
    #Handles new ingredients
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
    # Basic information about an ingredient
    print(iid)
    conn = dbi.connect()
    ingredient = queries.getIngredientDetail(conn, iid)
    page_title = "Foodbook | {}".format(ingredient.get('name'))
    print(ingredient)
    return render_template('ingredient_detail.html', ingredient=ingredient, page_title=page_title)

@app.route('/lookup/')
def ingredient_search():
    #Does keyword search in response to jQuery request, returns JSON
    conn = dbi.connect()
    name = request.args.get('name')
    print(name)
    results = queries.searchIngredient(conn, name)
    print(results)
    return jsonify(results=results)

@app.route('/find_recipe/')
def recipe_search():
    conn = dbi.connect()
    name = request.args.get('name')
    recipes = queries.searchRecipe(conn, name)
    for recipe in recipes:
        recipe['author'] = queries.getAuthor(conn, recipe.get('rid'))
    return jsonify(results=recipes)
    
@app.route("/review/<rid>", methods=["POST"])
def review(rid):
    # Handles creating new review, takes a recipe that the review is about
    conn = dbi.connect()
    try:
        if 'username' in session:
            username = session['username']
            uid = session['uid']
            body = request.form['body']
            print(body)
            if body:
                insertId = queries.insertReview(conn, uid, rid, body)
                print(insertId)
            else:
                flash("You cannot post an empty review!")
            return redirect(url_for('recipe_detail', rid=rid))
        else:
            flash('You are not logged in.  Please login or Sign up')
            return redirect(url_for('recipe_detail', rid=rid))
    except Exception as err:
        flash('Some kind of error ' + str(err))
        return redirect(url_for('recipe_detail', rid=rid))


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

