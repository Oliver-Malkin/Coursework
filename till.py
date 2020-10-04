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
    

def draw_total():
    total_frame = tkinter.Frame(height = top_box_height-padding*4,
                                width = (window.winfo_screenwidth()-top_box_width)-padding*4)
    total_frame.place(x = top_box_width+padding*2,
                      y = padding*2)

    # Set up the labels for the total values
    ex_vat = tkinter.Label(total_frame, relief = "sunken", font = FONT, text = "Excluding VAT:\n£0.00")
    inc_vat = tkinter.Label(total_frame, relief = "sunken", font = FONT, text = ("Including VAT @ "+str(VAT*100)+"%:\n£0.00"))
    offers_applied = tkinter.Label(total_frame, relief = "sunken", font = FONT, text = "Offers and Discounts:\n£0.00")
    total_price = tkinter.Label(total_frame, relief = "sunken", font = FONT, text = "Total cost of order:\n£0.00")

    ex_vat.place(x = padding, y = padding*2,
                 width = (window.winfo_screenwidth()-top_box_width)-padding*6,
                 height = (top_box_height-padding*4)/5)
    
    inc_vat.place(x = padding, y = (top_box_height-padding*4)/5+padding*4,
                 width = (window.winfo_screenwidth()-top_box_width)-padding*6,
                 height = (top_box_height-padding*4)/5)

    offers_applied.place(x = padding, y = (2*(top_box_height-padding*4)/5)+padding*6,
                 width = (window.winfo_screenwidth()-top_box_width)-padding*6,
                 height = (top_box_height-padding*4)/5)

    total_price.place(x = padding, y = (3*(top_box_height-padding*4)/5)+padding*8,
                 width = (window.winfo_screenwidth()-top_box_width)-padding*6,
                 height = (top_box_height-padding*4)/5)

    return total_frame, ex_vat, inc_vat, offers_applied, total_price

# end draw_total


def command_buttons():

    frame_width = window.winfo_screenwidth()-bottom_box_width-padding*4
    frame_height = window.winfo_screenheight()-top_box_height-padding*4
    
    command_frame = tkinter.Frame(width = frame_width,
                                  height = frame_height)
    command_frame.place(x = bottom_box_width+padding*2,
                        y = top_box_height+padding*2)
    
    delete = tkinter.Button(command_frame,
                            text = "Delete Selected",
                            command = lambda button = "del":
                            commands(button),
                            justify = "center",
                            font = FONT,
                            wraplength=frame_width-padding*2,
                            bg = '#E8AD25').place(x = 0, y = 0,
                                                  width = (frame_width/2)-padding,
                                                  height = (frame_height/6)-padding)

    set_qty = tkinter.Button(command_frame,
                             text = 'Set Quantity', 
                             command = lambda button = "set_qty":
                             commands(button),
                             justify = "center",  
                             wraplength=frame_width-padding,
                             font = FONT,
                             bg = '#3771DD').place(x = (frame_width/2), y = 0,
                                                   width = (frame_width/2)-padding,
                                                   height = (frame_height/6)-padding)
    
    discounts_whole = tkinter.Button(command_frame,
                                     text = "Whole Discount",
                                     command = lambda button = "multi_dis":
                                     commands(button),
                                     justify = "center",
                                     font = FONT,
                                     wraplength=frame_width-padding*2,
                                     bg = '#45D388').place(x = 0, y = (frame_height/6),
                                                           width = (frame_width/2)-padding,
                                                           height = (frame_height/6)-padding)

    discounts_single = tkinter.Button(command_frame,
                                      text = "Single Discount",
                                      command = lambda button = "sngl_dis":
                                      commands(button),
                                      justify = "center",
                                      font = FONT,
                                      wraplength=frame_width-padding*2,
                                      bg = '#45D388').place(x = (frame_width/2),
                                                            y = (frame_height/6),
                                                            width = (frame_width/2)-padding,
                                                            height = (frame_height/6)-padding)

    void = tkinter.Button(command_frame,
                          text = "Void",
                          command = lambda button = "void":
                          commands(button),
                          justify = "center",
                          font = FONT,
                          wraplength=frame_width-padding*2,
                          bg = '#DD3737').place(x = 0, y = (frame_height/6)*2,
                                                width = frame_width/2-padding,
                                                height = (frame_height/6)-padding)

    complete_order = tkinter.Button(command_frame,
                                    text = "Complete Order",
                                    command = lambda button = "comp_order":
                                    commands(button),
                                    justify = "center",
                                    font = FONT,
                                    wraplength = frame_width-padding*2,
                                    bg = '#B652D3').place(x = frame_width/2,
                                                          y = (frame_height/6)*2,
                                                          width = frame_width/2-padding,
                                                          height = frame_height/6-padding)

    log_off = tkinter.Button(command_frame,
                             text = "Log Off",
                             command = lambda button = "log_off":
                             commands(button),
                             justify = "center",
                             font = FONT,
                             wraplength = frame_width-padding*2,
                             bg = "#EAD51B").place(x = 0, y = (frame_height/6)*3,
                                                  width = frame_width/2-padding,
                                                  height = frame_height/6-padding)

    reboot = tkinter.Button(command_frame,
                             text = "Restart and Update",
                             command = lambda button = "reboot":
                             commands(button),
                             justify = "center",
                             font = FONT,
                             wraplength = frame_width-padding*2,
                             bg = "#EAD51B").place(x = frame_width/2, y = (frame_height/6)*3,
                                                  width = frame_width/2-padding,
                                                  height = frame_height/6-padding)

    shutdown = tkinter.Button(command_frame,
                             text = "Shutdown",
                             command = lambda button = "shutdown":
                             commands(button),
                             justify = "center",
                             font = FONT,
                             wraplength = frame_width-padding*2,
                             bg = "#EAD51B").place(x = 0, y = (frame_height/6)*4,
                                                  width = frame_width/2-padding,
                                                  height = frame_height/6-padding)

    reprint = tkinter.Button(command_frame,
                             text = "Re-print Last\nReceipt",
                             command = lambda button = "reprint":
                             commands(button),
                             justify = "center",
                             font = FONT,
                             wraplength = frame_width-padding*2,
                             bg = "#EAD51B").place(x = frame_width/2, y = (frame_height/6)*4,
                                                  width = frame_width/2-padding,
                                                  height = frame_height/6-padding)

    sys_commands = tkinter.Button(command_frame,
                                  text = "System Commands",
                                  command = lambda button = "sys_commands":
                                  commands(button),
                                  justify = "center",
                                  font = FONT,
                                  wraplength = frame_width-padding*2,
                                  bg = "#EB5218").place(x = 0, y = (frame_height/6)*5,
                                                  width = frame_width/2-padding,
                                                  height = frame_height/6-padding)

    open_item_button = tkinter.Button(command_frame,
                               text = "Open Item",
                               command = lambda: open_item(),
                               justify = "center",
                               font = FONT,
                               wraplength = frame_width-padding*2,
                               bg = '#C57AFF').place(x = frame_width/2, y = (frame_height/6)*5,
                                                     width = frame_width/2-padding,
                                                     height = frame_height/6-padding)

# end command_buttons


def open_item():
    popup = tkinter.Toplevel()
    popup.attributes("-topmost", True)
    popup.maxsize(300, 200)
    popup.minsize(300, 200)
    popup.grab_set()
    popup.title("Open Item")

    label = tkinter.Label(popup, text = "Enter name of product", font = FONT)
    label.place(x = padding, y = padding, height = 20, width = 300-padding*2)

    entry = tkinter.Text(popup, font = FONT)
    entry.place(x = padding, y = 20+padding, height = 120-padding, width = 300-padding*2)

    choice = tkinter.IntVar()

    enter = tkinter.Button(popup,
                          text = "Enter",
                          font = FONT,
                          justify = "center",
                          command = lambda: choice.set(1))
    enter.place(x = padding, y = 140+padding, height = 50-padding, width = 300/2-padding)

    cancel = tkinter.Button(popup,
                            text = "Cancel",
                            font = FONT,
                            justify = "center",
                            command = lambda: choice.set(2))
    cancel.place(x = 300/2+padding, y = 140+padding, height = 50-padding, width = 300/2-padding*2)

    enter.wait_variable(choice) # Waits for the user to press a button

    if choice.get() == 1: # Enter pressed
        item = entry.get("1.0", "end")
        label.config(text = "Enter price of product")
        entry.delete("1.0", "end")
        enter.wait_variable(choice)
        
        temp = []
        a = ""
        for i in range(len(item)):
            if item[i] != "\n": # split up the item and remove the '\n'
                temp.append(item[i])
        item = a.join(temp) # Re-join the item
            
        if choice.get() == 1: # Enter pressed again
            price = entry.get("1.0", "end")
            price = add_zero(float(price))
            add_to_order(item, str(price), "Customer Specific Item")
            popup.destroy()

        else:
            popup.destroy()
    else:
        popup.destroy()

# end open_item

    
def commands(command, args = None):
    global running_total # Make the running_total global for this procedure
    global discounts
    global discount_pos
    global whole_discount
    global current_order
    global last_order
    
    try:
        # If the button requires a line being selected
        line_not_required = ["comp_order", "void", "log_off", "reboot", "shutdown", "reprint", "sys_commands"]
        if command not in line_not_required:
            line = order_box.curselection()
            line = line[0] # Takes the number rather than the tuple
            line -= 3 # Take 3 from the line number
    
            if line < 0 or line == order_box.size()-4: # If negative or == bottom line - 4
                messagebox.showerror("System", "Invalid selection made\nPlease re-select item")
                raise KeyboardInterrupt # Exit the commands procedure
            
        if command == "del":
            if line in discount_pos: # If the item is discount data
                discounts = float(discounts) # Converts discounts to float
                discounts -= float(current_order[line][1]) # Subtrace the discount from the discounts variable
                discounts = add_zero(round(discounts)) # Convert to string an add required zero
                discount_pos.remove(line)
                del current_order[line]
                order_box.delete(line+3)
                
                if len(whole_discount) > 0: # If there is something in the whole_discount variable
                        update_discount_whole()
                update_labels()
                
            elif len(whole_discount) > 0 and line+4 == order_box.size()-1: # Whole order line selected
                total = float(whole_discount[1]) # total holds the value of the discount price
                discounts = float(discounts)-total # Removes the discount from the discounts variable
                discounts = add_zero(discounts)
                whole_discount = () # Remove the whole order discount
                order_box.delete(order_box.size()-2) # Remove the discount from the order_box
                update_labels()
                
                
            else: # Not a discount item
                running_total = float(running_total) # Turn into float
                running_total -= float(current_order[line][4]) # Subtract total price from the selected item
                order_box.delete(line+3) # Delete the line on the order_box
                del current_order[line] # Delete it from the current_order array
                
                if line+1 in discount_pos: # if there was a discount assosiated with that item
                    discounts = float(discounts) # Converts discounts to float
                    discounts -= float(current_order[line][1]) # Subtract the discount from the discounts variable
                    discounts = add_zero(round(discounts)) # Convert to string an add required zero
                    discount_pos.remove(line+1) # Remove the discount pos
                    del current_order[line] # remove the discount from teh order
                    order_box.delete(line+3) # update GUI order_box
                    
                if len(whole_discount) > 0: # If there is something in the whole_discount variable
                        update_discount_whole()
                update_labels() # Update the labels to read correct price


            discount_pos = []
            for x in range(len(current_order)): # Update the discount_pos array
                if "discount" in current_order[x]:
                    discount_pos.append(x)

        elif command == "set_qty":
            popup = tkinter.Toplevel() # Creates popup window
            popup.minsize(250, 100) # Makes the window 250 by 100 pxels
            popup.title("System") 
            
            popup.grab_set() # disables main window
            popup.attributes("-topmost", True) # Keeps popup on top

            label = tkinter.Label(popup, text = "Enter New Quantity:", font = FONT).pack()
            
            new_qty = tkinter.Entry(popup, width = 28)
            new_qty.pack()
            
            var = tkinter.IntVar()
            
            button = tkinter.Button(popup, text = "Enter", font = (FONT[0],FONT[1]),
                                  command = lambda: var.set(1))
            button.pack() # Displays button on screen
            
            button.wait_variable(var) # Waits for the variable var to change
            new_qty = new_qty.get() # Gets the value entered into the text box

            if int(new_qty) not in range(1, 51): # is the number entered not between 1 and 50
                messagebox.showerror("System", "Invalid entry!")
                popup.destroy()
            else:
                old_qty = int(current_order[line][3]) # Store the old qty val
                current_order[line][3] = int(new_qty) # Sets the new quantity
                current_order[line][4] = int(new_qty)*float(current_order[line][2]) # Update the total

                current_order[line][4] = add_zero(round(current_order[line][4], 2)) # Add the zero to the string is needed
                
                difference = current_order[line][3]-old_qty # Calculates the difference between the new and the old qty              
                difference = float(current_order[line][2]) * difference # Price difference qty * difference
                
                running_total = float(running_total) # Make sure running total is a float
                running_total += float(difference) # Add difference to old total

                order_box.delete(line+3) # Remove the line on the Listbox

                WIDTH = math.floor((top_box_width-padding*4)/10)
                # Update the deleted line
                order_box.insert(line+3, "│"+current_order[line][0]+": "+current_order[line][1]+
                                    " "*math.floor(WIDTH*2/3-len(current_order[line][0])-len(current_order[line][1])-3) +
                                    "│£"+current_order[line][2]+" "*math.floor(WIDTH*1/9-len(current_order[line][2])-2) +
                                    "│"+str(current_order[line][3])+" "*math.floor(WIDTH*1/9-len(str(current_order[line][3]))-1) +
                                    "│£"+str(current_order[line][4])+" "*math.floor(WIDTH*1/9-len(str(current_order[line][4]))-2) + "│")

                if line+1 in discount_pos: # If the item has a discount applied
                    update_discount(line) # Update the discount

                if len(whole_discount) > 0: # If there is something in the whole_discount variable
                        update_discount_whole()
                
                popup.destroy() # Destroys the popup
                update_labels()

        elif command == "sngl_dis":
            if line+1 in discount_pos:
                messagebox.showerror("System", "Discount Already Applied!")
            else:
                popup = tkinter.Toplevel() # Creates popup window
                popup.minsize(250, 100) # Makes the window 250 by 100 pxels
                popup.title("System") 
                
                popup.grab_set() # disables main window
                popup.attributes("-topmost", True) # Keeps popup on top

                label = tkinter.Label(popup, text = "Enter Percentage Discount:", font = FONT).pack()
                
                discount = tkinter.Entry(popup, width = 28)
                discount.pack()
                
                var = tkinter.IntVar()
                
                button = tkinter.Button(popup, text = "Enter", font = (FONT[0],FONT[1]),
                                      command = lambda: var.set(1))
                button.pack() # Displays button on screen

                button.wait_variable(var) # Waits for the variable var to change
                discount = discount.get() # Gets the value entered into the text box

                if 0 >= float(discount) or float(discount) > 100 or line in discount_pos: # if discount not between 1 and 100
                    messagebox.showerror("System", "Invalid entry!") # Show error message
                    popup.destroy() # Destroy the popup
                    
                else:
                    discount_total = float(current_order[line][4])*float(discount)/100 # calculates discount amount
                    discounts = float(discounts) # converts discount to float
                    discounts += float(discount_total) # Adds the discount to the discount total
                    
                    discounts = round(discounts, 2) # Rounds the discounts value to 2dp
                    discount_total = round(discount_total, 2) # Rounds the discount total to 2dp
                    
                    discount_total = add_zero(discount_total) # Adds the zero if needed
                    
                    current_order.insert(line+1, ["discount", discount_total, float(discount)/100]) # Insert into the current_order array
                    discount_pos.append(line+1) # Adds position of discount to the array
                    
                    WIDTH = math.floor((top_box_width-padding*4)/10)
                    order_box.insert(line+4, "│    -Discount @ "+str(discount)+"%"+" "
                                     *math.floor(WIDTH*2/3-18-len(str(discount)))+
                                     "│ ──"+" "*math.floor(WIDTH*1/9-4)+
                                     "│ ──"+" "*math.floor(WIDTH*1/9-4)+
                                     "│ -£"+str(discount_total)+" "*math.floor(WIDTH*1/9-4-len(str(discount_total)))+"│") # Add discount to GUI

                    if len(whole_discount) > 0: # If there is something in the whole_discount variable
                        update_discount_whole()

                    discount_pos = []
                    for x in range(len(current_order)): # Update the discount_pos array
                        if "discount" in current_order[x]:
                            discount_pos.append(x)

                    
                    update_labels() # Update the labels on the GUI
                    popup.destroy() # Destroy the popup

        elif command == "multi_dis": # Whole discount button pressed
            if len(whole_discount) == 0: # Something not in the discount
                popup = tkinter.Toplevel() # Creates popup window
                popup.minsize(250, 100) # Makes the window 250 by 100 pxels
                popup.title("System") # Sets the tile of the popup to system
                
                popup.grab_set() # disables main window
                popup.attributes("-topmost", True) # Keeps popup on top

                label = tkinter.Label(popup, text = "Enter Percentage Discount:", font = FONT).pack()
                
                discount = tkinter.Entry(popup, width = 28)
                discount.pack()
                
                var = tkinter.IntVar()
                
                button = tkinter.Button(popup, text = "Enter", font = (FONT[0],FONT[1]),
                                      command = lambda: var.set(1))
                button.pack() # Displays button on screen

                button.wait_variable(var) # Waits for the variable var to change
                discount = discount.get() # Gets the value entered into the text box
                discount = float(discount) # Converts to float

                if 0 >= float(discount) or float(discount) > 100: # Between excluding 0, including 100
                    messagebox.showerror("System", "Invalid entry!") # Show error message
                    popup.destroy()

                else:
                    total = float(running_total)-float(discounts) # Calculate the total with discounts already applied

                    discount_total = float(round(total*discount/100, 2)) # Calculates x% to take off and rounds to 2dp
                    whole_discount = (discount, discount_total) # Stores the whole discount as a decimal and the amount taken off

                    discounts = float(discounts)
                    discounts += float(discount_total)
                    discount_total = add_zero(discount_total) # Add a zero if needed

                    # Insert the discount into the orderbox
                    WIDTH = math.floor((top_box_width-padding*4)/10)
                    order_box.insert(order_box.size()-1, "│    -Whole Discount @ "+str(discount)+"%"+" "
                                             *math.floor(WIDTH*2/3-24-len(str(discount)))+
                                             "│ ──"+" "*math.floor(WIDTH*1/9-4)+
                                             "│ ──"+" "*math.floor(WIDTH*1/9-4)+
                                             "│ -£"+str(discount_total)+" "*math.floor(WIDTH*1/9-4-len(str(discount_total)))+"│")
                    update_labels()
                    popup.destroy()
            else:
                messagebox.showerror("System", "Discount Already Applied")


        elif command == "void":
            if len(current_order) != 0: # Is the order not empty?
                if args == None:
                    confirm = messagebox.askokcancel("System", "Confirm Void")
                else:
                    confirm = True # Dont ask for confirmation
                    
                if confirm == True:
                    # Reset the order variables
                    discount_pos = []
                    whole_discount = ()
                    running_total = 0
                    discounts = 0
                    current_order = []

                    # Update the GUI
                    order_box.delete(3, order_box.size()-2)
                    update_labels()

                    draw_buttons(tabs, -1)
                else:
                    pass
            else:
                messagebox.showerror("System", "Order Empty")

        elif command == "comp_order":
            if len(current_order) != 0: # Is the order not empty?
                popup = tkinter.Toplevel() # Show the popup
                popup.minsize(300, 150) # Set the size
                popup.title("System") # Sets the tile of the popup to system

                popup.grab_set() # disables main window
                popup.attributes("-topmost", True) # Keeps popup on top

                choice = tkinter.IntVar()
                
                card = tkinter.Button(popup, text="Card", font = FONT,
                                      command = lambda: choice.set(1))
                card.place(x = padding, y = 20, height = 125, width = math.floor(300/3-padding*2))
                
                cash = tkinter.Button(popup, text="Cash", font = FONT,
                                      command = lambda: choice.set(2))
                cash.place(x = math.floor(300/3+padding), y = 20,
                           height = 125, width = math.floor(300/3-padding*2))
                
                cancel = tkinter.Button(popup, text="Cancel", font = FONT,
                                        command = lambda: choice.set(3))
                cancel.place(x = math.floor(300*2/3+padding), y = 20,
                             height = 125, width = math.floor(300/3-padding*2))
                
                card.wait_variable(choice) # Wait for the choice variable to change
                popup.destroy() # Destroys the popup

                running_total = add_zero(round(float(running_total), 2))
                discounts = add_zero(round(float(discounts), 2))
                total = add_zero(round((float(running_total)-float(discounts)), 2))

                if choice.get() == 1: # Card payment
                    file = open("takings/takings-for-"+
                        str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "a") # Open the file as appendable

                    file.write("Time of Transaction: "+datetime.datetime.now().strftime("%H:%M-%S")+"\n")
                    file.write("Type of Transaction: Card Payment\n")
                    file.write("Total for Order: £"+str(running_total)+"\n")
                    file.write("Discounts: £"+str(discounts)+"\n")
                    file.write("Total Charged: £"+str(total)+"\n\n")
                    
                    file.close()
                    messagebox.showinfo("Payment", "Transaction Complete\n£"+str(total)) # Successful Transaction
                    print_recipt("Card", None)
                    last_order = current_order
                    last_order.append(["Card", running_total, discounts, whole_discount])

                    # Read the total file
                    file = open("takings/total-for-"+
                        str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")
                    content = file.read()
                    content = float(content) # convert from string to floating point
                    content += float(total) # Add the total just charged
                    content = str(content) # Convirt total to string
                    file.close() # Close the file

                    # Opent he file as writable
                    file = open("takings/total-for-"+
                        str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "w")
                    file.write(str(content)) # Write the new total
                    file.close() # Close the file

                    tabs_frame.destroy()
                    messagebox.showinfo("Order Complete", "Now make drinks")
                    
                    commands("void", True) # Clear the till
                    
                elif choice.get() == 2: # Cash payment
                    file = open("takings/takings-for-"+
                        str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "a")

                    file.write("Time of Transaction: "+datetime.datetime.now().strftime("%H:%M-%S")+"\n")
                    file.write("Type of Transaction: Cash Payment\n")
                    file.write("Total for Order: £"+str(running_total)+"\n")
                    file.write("Discounts: £"+str(discounts)+"\n")
                    file.write("Total Charged: £"+str(total)+"\n\n")
                    
                    file.close()
                    print_recipt("Cash", None)
                    last_order = current_order
                    last_order.append(["Cash", running_total, discounts, whole_discount])
                    
                    file = open("takings/total-for-"+
                        str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")
                    content = file.read()
                    content = float(content)
                    content += float(total)
                    content = str(content)
                    file.close()
                    
                    file = open("takings/total-for-"+
                        str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "w")
                    file.write(content)
                    file.close()

                    tabs_frame.destroy()
                    messagebox.showinfo("Order Complete", "Now make drinks")
                    
                    commands("void", True)
                    
                else:
                    messagebox.showinfo("System", "Transaction Cancled")
            else:
                messagebox.showerror("System", "Order Empty")

        elif command == "log_off":
            confirm = messagebox.askokcancel("System", "Comfirm log off")
            if confirm == True:
                login()
                draw_buttons(tabs, -1)
            else:
                messagebox.showinfo("System", "Log off cancled")

        elif command == "reboot":
            if args == True: # Reboot without warning
                print("Sys rebooting")
                #os.system("shutdown -r now")
            else:
                confirm = messagebox.askokcancel("System", "Confirm Reboot")
                if confirm == True:
                    messagebox.showinfo("System", "Press okay to reboot system")
                    #os.system("shutdown -r now")
                else:
                    messagebox.showinfo("System", "Reboot Cancled")

        elif command == "shutdown":
            if args == True: # Shutdown without warning
                print("Sys shutdown")
                #os.system("shutdown -h now")
            else:
                confirm = messagebox.askokcancel("System", "Confirm Shutdown")
                if confirm == True:
                    messagebox.showinfo("System", "Press okay to shutdown system")
                    #os.system("shutdown -h now")
                else:
                    messagebox.showinfo("System", "Shutdown Cancled")

        elif command == "reprint":
            if len(last_order) == 0:
                messagebox.showinfo("System", "No orders made yet")
            else:
                print_recipt(None, last_order)
                
        elif command == "sys_commands":
            #################
            # Scan RFID tag #
            #################
            auth = messagebox.askokcancel("System", "Scan Managers Fob")
            if auth == True:
                popup = tkinter.Toplevel()
                popup.maxsize(350, 200+padding)
                popup.minsize(350, 200+padding)

                popup.grab_set()
                popup.attributes("-topmost", True)
                popup.title("System Commands")

                choice = tkinter.IntVar()
                choice.set(0)
                
                x_read = tkinter.Button(popup,
                                        text = "x-read",
                                        command = lambda: choice.set(1),
                                        font = FONT,
                                        justify = "center",
                                        wraplength = 350/2-padding)

                z_read = tkinter.Button(popup,
                                        text = "z-read",
                                        command = lambda: choice.set(2),
                                        font = FONT,
                                        justify = "center",
                                        wraplength = 350/2-padding)

                petty_cash = tkinter.Button(popup,
                                            text = "Petty Cash",
                                            command = lambda: choice.set(3),
                                            font = FONT,
                                            justify = "center",
                                            wraplength = 350/2-padding)

                refunds = tkinter.Button(popup,
                                         text = "Refunds and Exchanges",
                                         command = lambda: choice.set(4),
                                         font = FONT,
                                         justify = "center",
                                         wraplength = 350/2-padding)

                toggle_outage = tkinter.Button(popup,
                                               text = "Toggle outage of products",
                                               command = lambda: choice.set(5),
                                               font = FONT,
                                               justify = "center",
                                               wraplength = 350-padding)
                
                x_read.place(x = padding,
                             y = padding,
                             height = 200/3-padding,
                             width = 350/2-padding)
                
                z_read.place(x = 350/2+padding,
                             y = padding,
                             height = 200/3-padding,
                             width = 350/2-padding*2)

                petty_cash.place(x = padding,
                                 y = 200/3+padding,
                                 height = 200/3-padding,
                                 width = 350/2-padding)

                refunds.place(x = 350/2+padding,
                              y = 200/3+padding,
                              height = 200/3-padding,
                              width = 350/2-padding*2)

                toggle_outage.place(x = padding,
                              y = (200/3)*2+padding,
                              height = 200/3-padding,
                              width = 350-padding*2)

                x_read.wait_variable(choice)

                choice = choice.get()
                popup.destroy() # Destory the popup after command executed
                
                if choice == 1: # x read
                    try:
                        # Trys to read the file for the days takings
                        file = open("takings/takings-for-"+
                            str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")

                        content = file.readlines()

                        popup = tkinter.Toplevel()
                        popup.grab_set() # disables main window
                        popup.attributes("-fullscreen", True)

                        textbox = tkinter.Listbox(popup,
                                                  font = FONT)
                        
                        textbox.place(x = padding, y = padding,
                                      height = window.winfo_screenheight()-padding*2-50,
                                      width = window.winfo_screenwidth()-padding*2)

                        # Effect only the vertical scroll
                        scrollbar = tkinter.Scrollbar(textbox, orient="vertical", command=textbox.yview)
                        # Put the scrollbar on the right of the listbox, fill along right
                        scrollbar.pack(side="right", fill="y")
                        # Set the scrollbar
                        textbox.config(yscrollcommand=scrollbar.set)
                        

                        textbox.insert(tkinter.END, "Transactions for today:")
                        textbox.insert(tkinter.END, "")

                        for x in range(len(content)):
                            textbox.insert(tkinter.END, content[x])

                        file = open("takings/total-for-"+
                            str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")

                        content = file.read()
                        content = add_zero(round(float(content), 2))
                        textbox.insert(tkinter.END, "Total taken today: £"+str(content))
                        
                        done = tkinter.IntVar()   
                        back = tkinter.Button(popup,
                                              text = "Back ↵",
                                              command = lambda: done.set(1),
                                              font = FONT,
                                              justify = "center")

                        back.place(x = padding, y = window.winfo_screenheight()-padding-50,
                                   height = 50-padding*2, width = window.winfo_screenwidth()-padding*2)

                        back.wait_variable(done) # Wait here for user to press back button

                        popup.destroy() # Destroy the window
                        
                    except FileNotFoundError:
                        mesagebox.showinfo("System", "No orders made today")
                    except ValueError:
                        popup.destroy()
                        messagebox.showinfo("System", "No orders made today")

                elif choice == 2: # z read
                    confirm = messagebox.askokcancel("Z-Read", "Z-Read pressed\nConfirm action") # Give user chance to cancel
                    if confirm == True: # Cash up till, make innoperative until tomorrow
                        
                        file = open("takings/total-for-"+
                                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")
                        total_taken = file.read()
                        total_taken = add_zero(str(total_taken))
                        file.close()

                        os.system("rm takings/total-for-"+ # Remove the total file
                                 str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt")

                        os.system("mv takings/takings-for-"+
                                  str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt takings/total-for-"+
                                  str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt") # Change file to total

                        # Add the total taken for the day
                        file = open("takings/total-for-"+
                                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "a")
                        file.write("Total taken today: £"+str(total_taken))
                        file.close()

                        file = open("system/z-read.dat", "w") # Wrtie todays date after z-read cash up
                        file.write(str(datetime.datetime.now().strftime("%d-%m-%y")))
                        file.close()

                        ####################
                        # Print total file #
                        ####################

                        messagebox.showinfo("System", "Register open")

                        messagebox.showinfo("System", "Z-Read done")
                        choice = messagebox.askyesno("System", "Shutdown system?")

                        if choice == True:
                            commands("shutdown", True) # Shutdown sys without warning
                            login() # Just incase the shoutdown was un-sucessful the till is still logged out
                        else:
                            login()
                    else:
                        messagebox.showinfo("System", "Z-Read Cancled")
                        

                elif choice == 3: # petty cash
                    file = open("takings/petty-cash-"+
                                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "a")
                    
                    popup = tkinter.Toplevel()
                    popup.grab_set()
                    popup.attributes("-topmost", True)
                    popup.minsize(300, 200)
                    popup.maxsize(300, 200)
                    popup.title("Petty-cash")

                    label = tkinter.Label(popup, text = "Enter amount (in Pounds)", font = FONT)
                    label.place(x = padding, y = padding, height = 30, width = 300-padding*2)

                    entry = tkinter.Text(popup)
                    entry.place(x = padding, y = 30+padding, height = 115, width = 300-padding*2)

                    # Effect only the vertical scroll
                    scrollbar = tkinter.Scrollbar(entry, orient="vertical", command=entry.yview)
                    # Put the scrollbar on the right of the listbox, fill along right
                    scrollbar.pack(side="right", fill="y")
                    # Set the scrollbar
                    entry.config(yscrollcommand=scrollbar.set)

                    choice = tkinter.IntVar()
                    choice.set(-1)
                    enter = tkinter.Button(popup, text = "Enter",
                                           command = lambda: choice.set(1),
                                           font = FONT,
                                           justify = "center")

                    back = tkinter.Button(popup, text = "Cancel",
                                          command = lambda: choice.set(0),
                                          font = FONT,
                                          justify = "center")

                    enter.place(x = padding, y = 145+padding*2, height = 200-(145+padding*3), width = 300/2-padding)
                    back.place(x = 300/2+padding, y = 145+padding*2, height = 200-(145+padding*3), width = 300/2-padding*2)

                    enter.wait_variable(choice)
                    if choice.get() == 0:
                        popup.destroy()
                        
                    elif choice.get() == 1:
                        amount = entry.get("1.0", "end")
                        amount = float(amount)

                    entry.delete("1.0", "end")
                    label.config(text = "Reason for withdrawal:")
                    choice.set(-1)

                    enter.wait_variable(choice)
                    if choice.get() == 0:
                        popup.destroy()
                        
                    elif choice.get() == 1:
                        reason = entry.get("1.0", "end")
                        file.write("Petty cash: "+str(reason))
                        file.write("Amount: £"+str(add_zero(amount)))
                        file.close()
                        popup.destroy()
                                        

                elif choice == 4: # Refunds
                    popup = tkinter.Toplevel()
                    popup.grab_set()
                    popup.attributes("-topmost", True)
                    popup.minsize(300, 200)
                    popup.maxsize(300, 200)
                    popup.title("Refunds")

                    label = tkinter.Label(popup, text = "Amount to refund", font = FONT)
                    label.place(x = padding, y = padding, height = 30, width = 300-padding*2)

                    entry = tkinter.Text(popup)
                    entry.place(x = padding, y = 30+padding, height = 115, width = 300-padding*2)

                    # Effect only the vertical scroll
                    scrollbar = tkinter.Scrollbar(entry, orient="vertical", command=entry.yview)
                    # Put the scrollbar on the right of the listbox, fill along right
                    scrollbar.pack(side="right", fill="y")
                    # Set the scrollbar
                    entry.config(yscrollcommand=scrollbar.set)

                    choice = tkinter.IntVar()
                    choice.set(-1)
                    enter = tkinter.Button(popup, text = "Enter",
                                           command = lambda: choice.set(1),
                                           font = FONT,
                                           justify = "center")

                    back = tkinter.Button(popup, text = "Cancel",
                                          command = lambda: choice.set(0),
                                          font = FONT,
                                          justify = "center")

                    enter.place(x = padding, y = 145+padding*2, height = 200-(145+padding*3), width = 300/2-padding)
                    back.place(x = 300/2+padding, y = 145+padding*2, height = 200-(145+padding*3), width = 300/2-padding*2)

                    enter.wait_variable(choice)
                    if choice.get() == 0:
                        popup.destroy()
                    elif choice.get() == 1:
                        amount = entry.get("1.0", "end")
                        amount = float(amount)

                    choice.set(-1)

                    entry.delete("1.0", "end")
                    label.config(text = "Reason for refund:")

                    enter.wait_variable(choice)
                    if choice.get() == 0:
                        popup.destroy()
                    elif choice.get() == 1:
                        reason = entry.get("1.0", "end")
                        file = open("takings/takings-for-"+
                            str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "a")

                        file.write("Refund\n")
                        file.write("Reason for refund: "+str(reason))
                        file.write("Amount refunded: £"+str(add_zero(amount)))

                        file.close()

                        file = open("takings/total-for-"+
                            str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")
                        content = file.read()
                        content = float(content)
                        content -= float(amount)
                        content = str(content)
                        file.close()
                        
                        file = open("takings/total-for-"+
                            str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "w")
                        file.write(content)
                        
                        file.close()
                        popup.destroy()
                    

                elif choice == 5: # Toggle outage vals
                    popup = tkinter.Toplevel()
                    popup.title("Toggle Outage")
                    popup.minsize(700,400)
                    popup.maxsize(700,400)
                    popup.attributes("-topmost", True)
                    popup.grab_set()

                    label = tkinter.Label(popup, font = FONT)
                    label.place(x = padding, y = padding, width = 700-padding*2, height = 20)
                    
                    left_box = tkinter.Listbox(popup, font = FONT)
                    left_box.place(x= padding, y = 20 + padding, width = 700/2-padding*2-30, height = 380-padding*3)

                    # Set up scroll bar for left box
                    scrollbar_left = tkinter.Scrollbar(left_box, orient="vertical", command=left_box.yview)
                    scrollbar_left.pack(side="right", fill="y")
                    left_box.config(yscrollcommand=scrollbar_left.set)
                    
                    right_box = tkinter.Listbox(popup, font = FONT)
                    right_box.place(x = 700/2+30+padding, y = 20 + padding, width = 700/2-padding*2-30, height = 380-padding*3)

                    # Set up scroll bar for right box
                    scrollbar_right = tkinter.Scrollbar(right_box, orient="vertical", command=right_box.yview)
                    scrollbar_right.pack(side="right", fill="y")
                    right_box.config(yscrollcommand=scrollbar_right.set)

                    choice = tkinter.IntVar()
                    choice.set(-1)

                    enter = tkinter.Button(popup, font = FONT, text = "Enter", justify = "center",
                                              command = lambda: choice.set(1))
                    enter.place(x = 700/2-padding-30, y = 150, width = 65, height = 30)
                    
                    back = tkinter.Button(popup, font = FONT, text = "Back", justify = "center",
                                              command = lambda: choice.set(2))
                    back.place(x = 700/2-padding-30, y = 180+padding, width = 65, height = 30)

                    to_left = tkinter.Button(popup, font = FONT, text = "<<<", justify = "center",
                                              command = lambda: choice.set(3))
                    to_left.place(x = 700/2-padding-30, y = 210+padding*2, width = 65, height = 30)

                    to_right = tkinter.Button(popup, font = FONT, text = ">>>", justify = "center",
                                              command = lambda: choice.set(4))
                    to_right.place(x = 700/2-padding-30, y = 240+padding*3, width = 65, height = 30)

                    while choice.get() != 2: # Back button pressed
                        
                        # Display the tabs in the first box (left)
                        for x in range(len(tabs)):
                            left_box.insert(tkinter.END, tabs[x][0])

                        back.config(text = "Back", state  = "normal")
                        label.config(text = "Select tab, then press enter")
                        enter.config(text = "Enter")
                        
                        enter.wait_variable(choice) # Wait for enter button to be pressed
                        
                        if choice.get() == 2: # Back button pressed, exit window
                            popup.destroy()
                        else:
                            tab = left_box.curselection() # Position of the tab in the tabs array
                            items = menu[tabs[tab[0]][0]] # Gets the element with the related tab selected
                            left_box.delete(0, tkinter.END) # Remove the contents of the left list box

                            for x in range(len(items)):
                                if items[x][1] == 0: # In stock
                                    left_box.insert(tkinter.END, items[x][0])
                                else: # Outage
                                    right_box.insert(tkinter.END, items[x][0])

                            label.config(text = " IN STOCK"+" "*36+"OUT OF STOCK") # Change text on label
                            enter.config(text = "Done")
                            choice.set(0)

                            while choice.get() != 1: # Done button not pressed

                                back.config(text = "", state = "disabled")

                                enter.wait_variable(choice)

                                if choice.get() == 3: # Out to in
                                    if right_box.curselection() == ():
                                        messagebox.showerror("Toggle Outage", "No item selected")
                                    else:
                                        # Get the selected line
                                        selection = right_box.get(right_box.curselection())
                                        # Move from the right box to left
                                        right_box.delete(right_box.curselection())
                                        left_box.insert(tkinter.END, selection)
                                        for x in range(len(items)):
                                            if items[x][0] == selection: # Selected item
                                                items[x][1] = 0 # Set as in stock

                                elif choice.get() == 4: # In to out
                                    if left_box.curselection() == ():
                                        messagebox.showerror("Toggle Outage", "No item selected")
                                    else:
                                        selection = left_box.get(left_box.curselection())
                                        left_box.delete(left_box.curselection())
                                        right_box.insert(tkinter.END, selection)
                                        for x in range(len(items)):
                                            if items[x][0] == selection: # Selected item
                                                items[x][1] = 1 # Set as out of stock

                                elif choice.get() == 1: # Enter button/back
                                    confirm = messagebox.askokcancel("Confirm save", "Save changes?")
                                    if confirm == True:
                                        menu[tabs[tab[0]][0]] == items # Sets new vals
                                        right_box.delete(0, tkinter.END)
                                        left_box.delete(0, tkinter.END)
                        
            else:
                messagebox.showerror("System", "Authorization error!\nCard scanned is not managers card")

        else:
            pass
        
    except IndexError:
        messagebox.showerror("System", "No selection made")
    except KeyboardInterrupt:
        pass
    
# end commands

def add_zero(val):
    val = float(val)
    if len(str(round(val-math.floor(val),2))) == 3:
        val = str(val)
        val = val+"0"
    else:
        pass
    return val

# end add_zero

def update_discount(x): # Where x is the position of the item in the current_order
    global discounts
    global discount_pos
    discount = (float(current_order[x+1][2])) # Discount as decimal that was entered
    discounts = float(discounts) # Convert discounts to float
    discounts -= float(current_order[x+1][1]) # Subtract the old discount

    current_order[x+1][1] = round(float(current_order[x][4])*discount, 2) # Update the discount price
    current_order[x+1][1] = add_zero(current_order[x+1][1]) # Add the zero, if required

    discounts += float(current_order[x+1][1]) # Add new discount price
    discounts = round(discounts, 2)

    order_box.delete(x+4) # Removes the discount line on the order_box
    WIDTH = math.floor((top_box_width-padding*4)/10)
    order_box.insert(x+4, "│    -Discount @ "+str(round(discount*100, 2))+"%"+" "
         *math.floor(WIDTH*2/3-18-len(str(round(discount*100, 2))))+
         "│ ──"+" "*math.floor(WIDTH*1/9-4)+
         "│ ──"+" "*math.floor(WIDTH*1/9-4)+
         "│ -£"+str(current_order[x+1][1])+" "*math.floor(WIDTH*1/9-4-len(str(current_order[x+1][1])))+"│")

    discount_pos = []
    for x in range(len(current_order)):
        if "discount" in current_order[x]:
            discount_pos.append(x)


def update_discount_whole():
    global discounts
    global whole_discount
    discounts = float(discounts)
    discounts -= float(whole_discount[1]) # Take away the old total discount

    discount = float(whole_discount[0]) # Sets discount to be the whole discount value entered

    total = float(running_total)-float(discounts) # recalculate the new one

    discount_total = float(round(total*discount/100, 2)) # Calculates x% to take off and rounds to 2dp
    whole_discount = (discount, discount_total) # Stores the whole discount as a decimal and the amount taken off

    discounts = float(discounts)
    discounts += float(discount_total)
    discount_total = add_zero(discount_total) # Add a zero if needed

    # Insert the discount into the orderbox
    WIDTH = math.floor((top_box_width-padding*4)/10)
    order_box.delete(order_box.size()-2) # Delete old line
    # Insert new one
    order_box.insert(order_box.size()-1, "│    -Whole Discount @ "+str(discount)+"%"+" "
                 *math.floor(WIDTH*2/3-24-len(str(discount)))+
                 "│ ──"+" "*math.floor(WIDTH*1/9-4)+
                 "│ ──"+" "*math.floor(WIDTH*1/9-4)+
                 "│ -£"+str(discount_total)+" "*math.floor(WIDTH*1/9-4-len(str(discount_total)))+"│")

def login():
    try:
        global tabs_frame
        tabs_frame.destroy()
    except:
        pass # The frame does not exist    

    LOGIN = tkinter.IntVar()
    LOGIN.set(0)

    popup = tkinter.Toplevel()
    popup.grab_set() # disables main window
    popup.attributes("-topmost", True) # Keeps popup on top
    popup.minsize(175, 125)
    popup.maxsize(175, 125)
    popup.title("System") # Sets the tile of the popup to system

    label = tkinter.Label(popup,
                          text = "Till logged out.\nPress button to log in",
                          justify = "center")
    button = tkinter.Button(popup, text = "Log In",
                            justify = "center",
                            command = lambda: LOGIN.set(1),
                            font = FONT)
    
    label.place(x = 0, y = 10, width = 175, height = 30)
    button.place(x = 0, y = 50, width = 175, height = 75)

    button.wait_variable(LOGIN)

    #################
    # Scan RFID tag #
    #################

    z_read = open("system/z-read.dat","r")
    z_date = z_read.read()
    z_read.close()

    # Date not passed last z-read
    if str(z_date) == str(datetime.datetime.now().strftime("%d-%m-%y")):
        popup.destroy()
        messagebox.showerror("System", "Unable to log in\nReason: Z-Read not expired")
        login()
    else:

        popup.destroy()
        
        messagebox.showinfo("System", "Till logged in") # Let uesr know the till is logged in


def print_recipt(payment_type = None, order = None):
    # Open the recipt file as writable
    
    if order == None: # Use current data
        order = current_order
        total = add_zero(round(float(running_total), 2))
        discount = add_zero(round(float(discounts), 2))
        charged = add_zero(round(float(running_total)-float(discounts), 2))

        if len(whole_discount) != 0:
            whole = add_zero(round(float(whole_discount[1]), 2))
            percentage = round(whole_discount[0])
        else:
            whole = 0
    else:
        order = last_order


    if payment_type == None: # Using the last order data        
        payment_type = order[len(order)-1][0] # Set payment type
        total = add_zero(round(float(order[len(order)-1][1]), 2)) # Total cost
        discount = add_zero(round(float(order[len(order)-1][2]), 2)) # Discount
        # Total charged
        charged = add_zero(round(float(order[len(order)-1][1])- float(order[len(order)-1][2]), 2))


        if len(order[len(order)-1][3]) == 0: # Nothing in the whole_discount tuple
             whole = 0
        else:
            whole = add_zero(order[len(order)-1][3][1])
            percentage = round(order[len(order)-1][3][0])

        del order[len(order)-1] # Remove the last entry

    file = open("receipts/"+str(datetime.datetime.now().strftime("%d-%m-%y@%H:%M-%S.txt")), "w")
    file.write("Order:\n")

    for x in range(len(order)):
        if order[x][0] == "discount":
            # Write to file "  -Dicount @ xx%    -£x.xx"
            file.write("  -Discount @ "+str(order[x][2]*100)+"%   -£"+str(order[x][1])+"\n")
        else:
            # Write to file "<qty> <tab>: <name of item> £<price indevidual> £<price total> \n"
            file.write(str(order[x][3])+" "+order[x][0]+": "+order[x][1]+" £"+
                       str(add_zero(order[x][2]))+" £"+str(add_zero(order[x][4]))+"\n")


    if whole != 0: # If there is a whole discount
        file.write("\n  -Dicount @ "+str(percentage)+"% -£"+str(whole))

    # Print totals and discounts
    file.write("\n\nPayment: "+str(payment_type)+"\n")
    file.write("Total: £"+str(total)+"\n")
    file.write("Discounts: -£"+str(discount)+"\n")
    file.write("Total charged: £"+str(charged)+"\n")
    file.close()
    
    messagebox.showinfo("System", "Receipt printed") # Popup letting the user the recipt has been printed

    
# Create the takings file for the day
try:
    file = open("takings/takings-for-"+
                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r") # Trys to read the file for the days takings
    file.close()
except FileNotFoundError:
    file = open("takings/takings-for-"+
                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "w") # creates a takings file
    file.close()

# Create a total file
try:
    file = open("takings/total-for-"+
                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")
    file.close()
except FileNotFoundError:
    file = open("takings/total-for-"+
                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "w")
    file.write("0.0")
    file.close()

# Create a petty-cash file
try:
    file = open("takings/petty-cash-"+
                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "r")
    file.close()
except FileNotFoundError:
    file = open("takings/petty-cash-"+
                str(datetime.datetime.now().strftime("%d-%m-%y"))+".txt", "w")
    file.close()

draw_boxes() # Draws the black border lines between each part on screen
command_buttons() # Draw the command buttons
order_box = draw_order_box() # Draw the order box and store in order_box
# Set up the total labels
total_frame, ex_vat_label, inc_vat_label, offers_label, total_price_label = draw_total()
login() # Log in required when first boot
draw_buttons(tabs, -1) # tabs is the array being passed, -1 tells the procedure its tabs to be drawn
















