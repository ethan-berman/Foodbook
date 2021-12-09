use bermane_db;

insert into ingredient(cost, name, unit) 
values (1.49, "Butter(unsalted)", "pound"),
    (0.39, "Wonder Bread", "slices"),
    (2.29, "American Cheese", "pound");

insert into user(username, email, password, restrictions)
values ("eberman", "bermane@whitman.edu", "lol", "DF");

insert into recipe(author, name, tools, preptime, description, category)
values (1, "Grilled Cheese", "Stove", 15, "The classic american grilled cheese", "american");
                                        
insert into quantity(ingredient, recipe, quantity, unit)
values (1, 1, 1, "tbsp"),
        (2, 1, 2, "slices"),
        (3, 1, 2, "slices");