print("What is your name?")
name = input();
print("Hello " + name + "! Do you have any allergies? ")
allergies = input();
if (allergies == "yes"):
    (allergies.lower().replace("y ","Y") == "yes")
    if(allergies.lower().replace("Yes ","") == "yes"):
        print("Please list your allergies!")
        allergy = input();

        print("\r\nName: "+name+"\r\n")
        print("Allergies: "+allergy+"\r\n")
else:
    print("You are safe to eat anything you want!")
