# Foodbook
Project for Web-Apps and Databases (CS-301) at Whitman College

## Overview
When you are a busy student, sometimes it's hard to figure out what to make for dinner on top of class and homework.  That is why we created Foodbook, a Web App designed for college students to share recipes with other students.  Foodbook allows users to post their recipes, browse other user submitted recipes, and review recipes they tried.

Foodbook was built using the Flask python framework.  Foodbook is a CRUD Api and uses JQuery on templates to provide interactivity.  It also uses MySql on the backend, using the python package PyMySql to connect the Flask server and the database.

I have also started working on a modern front-end to work with the Foodbook Api using React.  This project can be found in this [repository](https://github.com/ethan-berman/foodbook-frontend).  Due to the technical overhead of using JQuery as opposed to a more modern framework, the front end of this version does not support all operations we had intended.

## Features:
 - Create a recipe using a dynamic form built in JQuery
 - See what recipes other people have posted
 - Find other recipes written by the same person
 - Leave a review on a recipe
 - Session based authentication

## Work in Progress:
 - Edit an existing recipe
 - Fork a recipe with reference back to the original
 - Delete a recipe
 - Delete a review
 - Pull data for food prices to calculate meal prices based on location
 - Populate the database more
