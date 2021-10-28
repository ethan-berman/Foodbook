use bermane_db;

insert into ingredient(name, cost) 
values (1.49, "Butter(unsalted)"),
    (3.49, "Wonder Bread"),
    (2.29, "American Cheese");
insert into quantity(ingredient, recipe, quantity, unit)
values (0, 0, 1, "tbsp"),
        (1, 0, 2, "slices"),
        (2, 0, 2, "slices");
insert into user(username, email, password, restrictions)
values ("eberman", "bermane@whitman.edu", "lol", "DF");
insert into recipe(author, name, tools, preptime, description, category)
values (0, "Grilled Cheese", "Stove", 15, "The classic american grilled cheese", "american");
                                        