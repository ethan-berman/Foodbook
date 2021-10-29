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

def insertIngredient(conn, name, cost):
    curs = dbi.dict_cursor(conn)
    curs.execute("insert into ingredient(name,cost) values (%s, %s);", [name,cost])
    conn.commit()
    curs.execute("select last_insert_id() as id from ingredient")
    id = curs.fetchone()
    id = id['id']
    return id

def getRecipes(conn, limit):
    curs = dbi.dict_cursor(conn)
    curs.execute("select * from recipe limit %s", [limit])
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
    curs.execute("select * from quantity inner join recipe on quantity.recipe = recipe.rid")
    quantities = curs.fetchall()
    return quantities