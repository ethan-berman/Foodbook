use bermane_db;

drop table if exists quantity;
drop table if exists ingredient;
drop table if exists review;
drop table if exists instruction;
drop table if exists recipe;
drop table if exists user;

create table user (
    uid int auto_increment,
    username varchar(40) not null,
    email varchar(40) not null,
    password char(60) not null,
    restrictions set('vegan', 'vegetarian', 'pescetarian', 'peanut allergy', 'GF', 'DF'),
    unique(username),
    primary key (uid)
)
ENGINE = InnoDB;

create table recipe (
    rid int auto_increment,
    author int not null,
    name varchar(50) not null,
    preptime int,
    tools set("oven", "stove", "knife", "microwave"),
    description text not null,
    category set("mexican", "french", "greek", "chinese", "american", "pasta"),
    primary key(rid),
    index(rid),
    foreign key (author) references user(uid)
        on delete cascade
        on update cascade
    
)
ENGINE = InnoDB;

create table instruction (
    instid int auto_increment,
    recipe int not null,
    number tinyint not null,
    content text not null,
    primary key(instid),
    foreign key (recipe) references recipe(rid)
        on delete cascade
        on update cascade
)
ENGINE = InnoDB;

create table review (
    revid int auto_increment,
    author int not null,
    recipe int not null,
    body text not null,
    primary key(revid),
    index(revid),
    foreign key(author) references user(uid)
        on delete restrict,
    foreign key(recipe) references recipe(rid)
        on delete restrict
        on update cascade
)
ENGINE = InnoDB;

create table ingredient (
    iid int auto_increment,
    name varchar(50) not null,
    cost float,
    unit enum("cup", "pound", "count", "tbsp", "tsp", "kilogram", "gram", "slices"),
    primary key(iid)
)
ENGINE = InnoDB;

create table quantity (
    qid int auto_increment not null,
    ingredient int not null,
    recipe int not null,
    quantity float not null,
    unit enum("cup", "pound", "count", "tbsp", "tsp", "kilogram", "gram", "slices"),
    primary key(qid),
    index (qid),
    foreign key (ingredient) references ingredient(iid)
        on delete restrict
        on update cascade,
    foreign key (recipe) references recipe(rid)
        on delete restrict
        on update cascade
)
ENGINE = InnoDB;