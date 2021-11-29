import cs304dbi as dbi

def getIngredientDetail(conn, iid):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from ingredient where iid=%s",[iid])
    ingredient = curs.fetchone()
    return ingredient

def getIngredients(conn, limit):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from ingredient limit %s", [limit])
    ingredients = curs.fetchall()
    return ingredients

def getAllIngredients(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute("select iid, name from ingredient")
    ingredients = curs.fetchall()
    return ingredients

def insertIngredient(conn, name, cost):
    curs = dbi.dict_cursor(conn)
    curs.execute("insert into ingredient(name,cost) values (%s, %s);", [name,cost])
    conn.commit()
    curs.execute("select last_insert_id() as id from ingredient")
    id = curs.fetchone()
    id = id['id']
    return id

def insertQuantity(conn, recipe, ingredient, quantity, unit):
    curs = dbi.dict_cursor(conn)
    curs.execute("insert into quantity(ingredient, recipe, quantity, unit) values (%s, %s, %s, %s);", [ingredient,recipe,quantity,unit])
    conn.commit()
    curs.execute("select last_insert_id() as id from quantity")
    id = curs.fetchone()
    id = id['id']
    return id
def searchIngredient(conn, name):
    curs = dbi.dict_cursor(conn)
    param = "%" + name + "%"
    curs.execute("select * from ingredient where name like %s ", [param])
    results = curs.fetchall()
    return results

def getRecipes(conn, limit):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from recipe limit %s", [limit])
    recipes = curs.fetchall()
    return recipes
def getAllRecipes(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from recipe")
    recipes = curs.fetchall()
    return recipes

def getRecipeById(conn, rid):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from recipe where rid=%s", [rid])
    recipe = curs.fetchone()
    return recipe

def getRecipeIngredients(conn, rid):
    curs = dbi.dict_cursor(conn)
    print(rid)
    curs.execute("select * from quantity where recipe = %s", [rid])
    quantities = curs.fetchall()
    return quantities

def insertRecipe(conn, author, name, description):
    curs = dbi.dict_cursor(conn)
    curs.execute("insert into `recipe`(author, name, description) values (%s, %s, %s)", [author, name, description])
    conn.commit()
    curs.execute("select last_insert_id() as id from ingredient")
    id = curs.fetchone()
    id = id['id']
    return id

def insertInstruction(conn, recipe, number, content):
    curs = dbi.dict_cursor(conn)
    curs.execute("insert into instruction(recipe, number, content) values (%s, %s, %s)", [recipe,number,content])
    conn.commit()
    curs.execute("select last_insert_id() as id from instruction")
    id = curs.fetchone()
    id = id['id']
    return id

def getInstructionsByRecipe(conn, recipe):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from instruction where recipe = %s", [recipe])
    instructions = curs.fetchall()
    return instructions

def getAuthor(conn, recipe):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from user, recipe where recipe.author = user.uid and recipe.rid = %s", [recipe])
    author = curs.fetchone()
    return author
def getReviewAuthor(conn, review):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from user, review where review.author = user.uid and review.revid = %s", [review])
    author = curs.fetchone()
    return author

def insertReview(conn, author, recipe, body):
    curs = dbi.dict_cursor(conn)
    curs.execute("insert into review (author, recipe, body) values (%s, %s, %s)", [author,recipe,body])
    conn.commit()
    curs.execute("select last_insert_id() as id from review")
    id = curs.fetchone()
    id = id['id']
    return id

def getReviewsByRecipe(conn, recipe):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from review where recipe = %s", [recipe])
    reviews = curs.fetchall()
    return reviews