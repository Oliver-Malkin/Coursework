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

def draw_order_box():
    # Draw order textbox and frame
    order_box_frame = tkinter.Frame(height = top_box_height-padding*4,
                                    width = top_box_width-padding*4, bg='#dfdfdf')
    order_box_frame.place(x = padding*2, y = padding*2)
    
    order_box = tkinter.Listbox(order_box_frame, font= (FONT[0],FONT[1]), bg='#dfdfdf', borderwidth = 0)
    # place Listbox in top left quadrant
    order_box.place(x = 0, y = 0,
                    width = top_box_width-padding*4,
                    height = top_box_height-padding*4)

    # set up scrollbar
    scrollbar = tkinter.Scrollbar(order_box, orient="vertical", command=order_box.yview) # Effect only the vertical scroll
    scrollbar.pack(side="right", fill="y") # Put the scrollbar on the right of the listbox, fill along right
    order_box.config(yscrollcommand=scrollbar.set) # Tell the orderbox that the scrollbar changed the y view
    

    # Print the title accross the Listbox
    WIDTH = math.floor((top_box_width-padding*4)/10) # Width of text box in characters
    order_box.insert(tkinter.END, "┌"+"─"*math.floor(WIDTH*2/3-1)+"┬"+"─"*math.floor(WIDTH/9-1)+"┬"+
                    "─"*math.floor(WIDTH/9-1)+"┬"+"─"*math.floor(WIDTH/9-1)+"┐")
    
    order_box.insert(tkinter.END, "│Name"+" "*math.floor(WIDTH*2/3-5) +
                                  "│Price"+" "*math.floor(WIDTH*1/9-6) +
                                  "│Qty"+" "*math.floor(WIDTH*1/9-4) +
                                  "│Total"+" "*math.floor(WIDTH*1/9-6) + "│")
    
    order_box.insert(tkinter.END, "├"+"─"*math.floor(WIDTH*2/3-1)+"┼"+"─"*math.floor(WIDTH/9-1)+"┼"+
                    "─"*math.floor(WIDTH/9-1)+"┼"+"─"*math.floor(WIDTH/9-1)+"┤")
    
    order_box.insert(tkinter.END, "└"+"─"*math.floor(WIDTH*2/3-1)+"┴"+"─"*math.floor(WIDTH/9-1)+"┴"+
                    "─"*math.floor(WIDTH/9-1)+"┴"+"─"*math.floor(WIDTH/9-1)+"┘")
    return order_box

# end draw_order_box


def add_to_order(name, price, tab):
    global discounts
    global running_total
    WIDTH = math.floor((top_box_width-padding*4)/10) # Width of text box in characters
    found = False # Used to determin if the item is already in the list
    x = 0 # Index value for loop
    
    if len(current_order) != 0:
        while x < len(current_order) and found == False:
            if name in current_order[x] and tab in current_order[x]: # Same item found
                current_order[x][3] += 1 # Increase qty val by 1
                new_total = int(current_order[x][3])*float(price) # price * qty
                new_total = round(new_total,2)

                new_total = add_zero(new_total)

                current_order[x][4] = new_total # Replace the old total with the new value
                order_box.delete(x+3) # Remove the line on the Listbox

                # Update the deleted line
                order_box.insert(x+3, "│"+tab+": "+name+" "*math.floor(WIDTH*2/3-len(tab)-len(name)-3) +
                                      "│£"+price+" "*math.floor(WIDTH*1/9-len(price)-2) +
                                      "│"+str(current_order[x][3])+" "*math.floor(WIDTH*1/9-len(str(current_order[x][3]))-1) +
                                      "│£"+str(new_total)+" "*math.floor(WIDTH*1/9-len(str(new_total))-2) + "│")

                # update discount value if needed
                if x+1 in discount_pos:
                    update_discount(x)

                                               
                found = True # Exit the loop
            x += 1 # Increment the index
    if len(whole_discount) > 0:
        a = 1
    else:
        a = 0
    if found == False: # If the above loop did not find the item or empty array
        current_order.append([tab, name, price, 1, price]) # Add item to the current order array
        order_box.insert(order_box.size()-1-a, "│"+tab+": "+name+" "*math.floor(WIDTH*2/3-len(tab)-len(name)-3) +
                                      "│£"+price+" "*math.floor(WIDTH*1/9-len(price)-2) +
                                      "│1"+" "*math.floor(WIDTH*1/9-2) +
                                      "│£"+price+" "*math.floor(WIDTH*1/9-len(price)-2) + "│")
    running_total = float(running_total)
    running_total += float(price)
    
    if len(whole_discount) > 0: # If there is something in the whole_discount variable
        update_discount_whole()
        
    update_labels()

# end add_to_order

        
# Update the labels
def update_labels():
    global discounts
    global running_total

    running_total = round(float(running_total), 2)

    ex_vat_val = running_total*(1-VAT)
    ex_vat_val = round(ex_vat_val, 2)

    discounts = float(discounts)
    discounts = round(discounts, 2)

    running_total = add_zero(running_total)

    ex_vat_val = add_zero(ex_vat_val)

    discounts = add_zero(discounts)

    total = round(float(running_total)-float(discounts),2)

    total = add_zero(total)

    ex_vat_label.config(text="Excluding VAT:\n£"+str(ex_vat_val))
    inc_vat_label.config(text="Including VAT @ "+str(VAT*100)+"%:\n£"+str(running_total))
    offers_label.config(text="Offers and Discounts:\n£"+str(discounts))
    total_price_label.config(text="Total cost of order:\n£"+str(total))

# end update_labels
