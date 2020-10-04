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

def draw_boxes():
    
    # The first two arguments set the start point x1, y1 in pixles of the
    # rectangle. The next two arguments set the end point x2, y2 of the rectangle
    order_total_box = canvas.create_rectangle(padding, padding,
                                        top_box_width-padding,
                                        top_box_height-padding,
                                        width=box_width)

    # This creates the order total box
    price_total_box = canvas.create_rectangle(top_box_width+padding,
                                        padding,
                                        window.winfo_screenwidth()-padding,
                                        top_box_height-padding,
                                        width=box_width)

    # This creates the tab box, using the same methods as above
    tab_box = canvas.create_rectangle(padding,
                                        top_box_height+padding,
                                        bottom_box_width-padding,
                                        window.winfo_screenheight()-padding,
                                        width=box_width)

    # This creates the command buttons box
    command_box = canvas.create_rectangle(bottom_box_width+padding,
                                          top_box_height+padding,
                                          window.winfo_screenwidth()-padding,
                                          window.winfo_screenheight()-padding,
                                          width=box_width)

# end draw_boxes

    
def draw_buttons(to_draw, pos): # to_draw is the array of buttons to be drawn
    global tabs_frame

    width_bound = ((0, bottom_box_width-padding*4))
    height_bound = ((0, (window.winfo_screenheight()-top_box_height)-padding*4))

    try:
        tabs_frame.destroy() # Trys to destroy the frame
    except: # Excepts any exeception
        pass

    # Draws the frame for the tabs, using the bounds set above
    tabs_frame = tkinter.Frame(height = height_bound[1],
                           width = width_bound[1])
    tabs_frame.place(y = top_box_height+padding*2, x = padding*2)
    
    # Paramiters for the buttons height/width
    button_height = 80        
    button_width = 120

    # Starting positions for the button to be placed within the frame
    current_width = width_bound[0]
    current_height = height_bound[0]

    # Goes through each item in the array passed to the procedure
    for i in range(len(to_draw)):
        if pos == -1: # Tab button
            b = tkinter.Button(tabs_frame,
                           text = to_draw[i][0], # The text on the button is first part of the array
                           command = lambda button_name = to_draw[i][0], x = i:
                           button_pressed(button_name, x, -1), # When the button is pressed it calles a precedure
                                                # button_pressed, and passes the name of the button
                           justify = "center",  # centers the button's text
                           wraplength=button_width-padding, # Makes the text wrap around the button
                                                # the amount it starts to wrap is in pixles hence
                                                # using the button_width
                           bg = tabs[i][1],  # Sets the background color of the button
                           font = FONT) # Sets the font of the button
            
        else: # Item button
            if to_draw[i][1] == 0: # If outage is 0 (false)
                outage = 'normal'
            else: # Else outage will be 1 (true)
                outage = 'disabled'
                
            b = tkinter.Button(tabs_frame,
                           text = to_draw[i][0], # The text on the button is first part of the array
                           command = lambda button_name = to_draw[i][0], x = i:
                           button_pressed(button_name, -1, x), # When the button is pressed it calls a precedure
                                                # button_pressed, and passes the name of the button
                                                # the -1 shows it is an item and the number x is the position
                                                # of the button in the passed tabs array
                               
                           justify = "center",  # centers the button's text
                           wraplength=button_width-padding, # Makes the text wrap around the button
                                                # the amount it starts to wrap is in pixles hence
                                                # using the button_width
                           bg = tabs[pos][1],  # Sets the background color of the button
                           state = outage, # Sets the state of the button
                           font = FONT) # Sets the font of the button

        # Draw the button on the screen
        b.place(x=current_width, y=current_height, width=button_width,
                height=button_height)

        # Calculates the new x and y positions for the button
        current_height += button_height+padding # adds the button heigh to the current y pos

        # If the next position is out of the bounds of the box, move to next column
        if current_height+button_height > height_bound[1]:
            current_height = height_bound[0]
            current_width += button_width+padding

    if pos != -1: # not a tabs being drawn
        b = tkinter.Button(tabs_frame,
                           text = 'Back to tabs\n↵', # The text on the button is first part of the array
                           command = lambda button_name = 'back':
                           button_pressed(button_name, -1, 'tab'), # When the button is pressed it calles a precedure
                                                # button_pressed, and passes the name of the button
                           justify = "center",  # centers the button's text
                           wraplength=button_width-padding, # Makes the text wrap around the button
                                                # the amount it starts to wrap is in pixles hence
                                                # using the button_width
                           font = FONT) # Sets the font of the button
        
        while current_width+button_width*2 < width_bound[1]:
            current_width += button_width+padding
            
        while current_height+button_height*2 < height_bound[1]:
            current_height += button_height+padding
            
        b.place(x=current_width, y=current_height, width=button_width,
                height=button_height)

# end draw_buttons
        

def button_pressed(inp, pos, item_pos):
    global current_tab
    if inp == "back": # back button
        draw_buttons(tabs, -1) # Draw tabs
        
    elif pos > -1 and item_pos == -1: # tabs
        draw_buttons(menu[inp], pos) # Draw relating items
        current_tab = tabs[pos][0]        
    else: # item
        # Add item, price to array
        # current_order.append((inp, menu[current_tab][item_pos][2]))
        # Now changed to call procedure add_to_order
        add_to_order(inp, menu[current_tab][item_pos][2], current_tab)

# end button_pressed
