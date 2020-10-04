###########################################################
# Author:   Oliver Malkin (c)                             #
# Purpose:  Till GUI for Electronic Pager Ordering System #
# Date:     November 2018                                 #
###########################################################

import tkinter
from tkinter import messagebox
from mysql.connector import MySQLConnection as sql
import math
import datetime
import os

# initialization and variables

window = tkinter.Tk()
window.attributes("-fullscreen", True)

# Setting up connection to databse
database = sql(host='192.168.1.64',
                database = 'menu',
                user = 'readonly',
                password = 'Read Only')

curs = database.cursor()

# The menu

menu = {
    }

tabs = []

curs.execute('SELECT name, colour FROM menu.tabs;')
tabs = curs.fetchall() # Executes the command above, fetches data, stores in tabs

for x in range(len(tabs)):
    # Selects name, outage, price from item table with relating tab_id to tab[x][0]
    curs.execute("""SELECT name, outage, price FROM menu.items 
WHERE tab_id = (SELECT tab_id FROM menu.tabs WHERE name = '%s');"""
                 %(tabs[x][0]))
    menu[tabs[x][0]] = curs.fetchall() # Creates an array with the fetched data


database.close() # Close the connection to the database

# Set the tuples in the menu to arrays
for tab in range(len(menu)): # Goes through each element in the dictionary
    for item in range(len(menu[tabs[tab][0]])): # Goes through each of the item in the element
        # Convert the tuple to an array
        menu[tabs[tab][0]][item] = [menu[tabs[tab][0]][item][0],
                                    menu[tabs[tab][0]][item][1],
                                    menu[tabs[tab][0]][item][2]]

# Draw the canvas

# This statement sets the canvas to be the same width and hight of the window
# The part 'window.winfo_screenwidth()/height() retrieves screen's width/height in pixles
canvas = tkinter.Canvas(window,
                        width=window.winfo_screenwidth(),
                        height=window.winfo_screenheight(),
                        bg = '#DFDFDF')

# Draws the canvas on the main window 'window'
canvas.pack()

# These control the apperence of the boxes dab
top_box_width = window.winfo_screenwidth()*4/5 # Stores the width of the top partition
top_box_height = window.winfo_screenheight()*3/8 # Stores the height of the top box
bottom_box_width = window.winfo_screenwidth()*4/6 # Stores the width of bottom partition
padding = 5 # Padding
box_width = 2 # width of box lines

global tabs_frame
global current_tab

current_order = []
current_tab = ''

FONT = (('Courier New', 13, 'bold')) # This is the font that will be used throughout the program

VAT = 0.2 # VAT @ 20%
running_total = 0
discounts = 0 # used to hold the offers/discounts
discount_pos = [] # Stores the positions of the dicounts in the listobx
whole_discount = () # Stores the whole discount

last_order = []

#########################
# End of initialization #
#########################
