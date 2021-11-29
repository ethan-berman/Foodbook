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
    return render_template('main.html', recipes=recipes)

@app.route('/join/', methods=["GET", "POST"])
def join():
    if request.method == "GET":
        return render_template("join.html")
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
        return render_template("login.html")
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
            print('database has hashed: {} {}'.format(hashed,type(hashed)))
            print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
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
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            uid = session['uid']
            session['visits'] = 1+int(session['visits'])
            return render_template('user.html',
                                   page_title='My App: Welcome {}'.format(username),
                                   name=username,
                                   uid=uid,
                                   visits=session['visits'])

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
    conn = dbi.connect()
    recipe = queries.getRecipeById(conn, rid)
    author = queries.getAuthor(conn, rid)
    ingredients = queries.getRecipeIngredients(conn, rid)
    instructions = queries.getInstructionsByRecipe(conn, rid)
    reviews = queries.getReviewsByRecipe(conn, rid)
    for item in reviews:
        poster = queries.getReviewAuthor(conn, item['revid'])
        item['author'] = poster
    for item in ingredients:
        # print(item)
        ingredient_name = queries.getIngredientDetail(conn, item.get('ingredient'))
        # print(ingredient_name)
        item['ingredient_name'] = ingredient_name.get("name")
    return render_template("recipe_detail.html",recipe=recipe, ingredients=ingredients, instructions=instructions, author=author, reviews=reviews)

@app.route('/recipe/', methods=["GET", "POST"])
def recipe_create():
    conn = dbi.connect()
    try:
        if 'username' in session:
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
                uid = session['uid']
                print(data)

                print(request.form)
                print(ingredients)
                

                recipe_id = queries.insertRecipe(conn, uid, title, description)
                for item in ingredients:
                    print(item)
                    id = queries.insertQuantity(conn, recipe_id, item['iid'], item['quantity'], item['unit'])
                    print(id)
                for i in range(len(instructions)):
                    id = queries.insertInstruction(conn, recipe_id, i, instructions[i])
                    print(id)

                return redirect(url_for("recipe_detail", rid=recipe_id))
        else:
            flash('you are not logged in. Please login or Sign up.')
            return redirect(url_for('index'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))


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

@app.route("/review/<rid>", methods=["POST"])
def review(rid):
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

