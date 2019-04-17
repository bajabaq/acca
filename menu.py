#!/usr/bin/python
# Version 1
import sys



print "Get project name"
print "Get project location - city, state"

print "Get the door types"
print "Get the window types"

print "Get number of above-ground stories"
print "Get exposure of ground floor - lat, lng for each corner"

print "If num above-ground stories == 1; then skip"
print "else if num above-ground stories > 1; then say"
print "  are remaining floors oriented the same as the ground floor?"
print "  if yes then break; else loop over each remaining floor getting the exposures"

print "foreach exposure "
print "    get the wall composition (if num exposure > 1, use as default)"
print "    get the door type and size"

print "    get the window type and size"


vals = (1,2,3,4,5)
print 'Pick the value and press [ENTER]:'
i=0
for val in vals:    
    print "\t" + str(i)+") " + str(val)
    i=i+1
#endfor
choice = raw_input()

sys.exit()



## Show menu ##
def menu():
        strs = ('Enter 1 for addition\n'
                'Enter 2 for subtaction\n'
                'Enter 3 for multiplication\n'
                'Enter 4 for division\n'
                'Enter 5 to exit : ')
        choice = raw_input(strs)
        return int(choice) 

while True:          #use while True
    choice = menu()
    if choice == 1:
        add(input("Add this: "),input("to this: "))
    elif choice == 2:
        sub(input("Subtract this: "),input("from this: "))
    elif choice == 3:
        mul(input("Multiply this: "),input("by this: "))
    elif choice == 4:
        div(input("Divide this: "),input("by this: "))
    elif choice == 5:
        break


print (30 * '-')
print ("   M A I N - M E N U")
print (30 * '-')
print ("1. Backup")
print ("2. User management")
print ("3. Reboot the server")
print (30 * '-')
 
## Get input ###
choice = ''
low = 1
high = 3
while (len(choice) < 1):
    choice = int(raw_input('Enter your choice [1-3] : '))
    
#endwhile
    

 
### Take action as per selected menu-option ###
if choice == 1:
        print ("Starting backup...")
elif choice == 2:
        print ("Starting user management...")
elif choice == 3:
        print ("Rebooting the server...")
else:    ## default ##
        print ("Invalid number. Try again...")
#endif        
