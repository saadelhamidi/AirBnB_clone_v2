#!/usr/bin/python3
""" Console Module """
import cmd
import shlex
import sys
import ast
from models.base_model import BaseModel
from models.__init__ import storage
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """ Contains the functionality for the HBNB console """

    prompt = '(hbnb) ' if sys.__stdin__.isatty() else ''

    classes = {
        'BaseModel': BaseModel, 'User': User, 'Place': Place,
        'State': State, 'City': City, 'Amenity': Amenity, 'Review': Review
    }

    dot_cmds = ['all', 'count', 'show', 'destroy', 'update']

    types = {
        'number_rooms': int, 'number_bathrooms': int,
        'max_guest': int, 'price_by_night': int,
        'latitude': float, 'longitude': float
    }

    def preloop(self):
        """ Prints if isatty is false """
        if not sys.__stdin__.isatty():
            print('(hbnb)')

    def precmd(self, line):
        """ Reformat command line for advanced command syntax """
        if '.' in line and '(' in line and ')' in line:
            try:
                cls, cmd = line.split('.', 1)
                cmd, args = cmd.split('(', 1)
                args = args.strip(')')
                args_list = shlex.split(args)

                if cmd in self.dot_cmds:
                    line = ' '.join([cmd, cls] + args_list)

            except Exception:
                pass
        return line

    def postcmd(self, stop, line):
        """ Prints if isatty is false """
        if not sys.__stdin__.isatty():
            print('(hbnb) ', end='')
        return stop

    def do_quit(self, command):
        """ Method to exit the HBNB console """
        exit()

    def help_quit(self):
        """ Prints the help documentation for quit """
        print("Exits the program with formatting\n")

    def do_EOF(self, arg):
        """ Handles EOF to exit program """
        print()
        exit()

    def help_EOF(self):
        """ Prints the help documentation for EOF """
        print("Exits the program without formatting\n")

    def emptyline(self):
        """ Overrides the emptyline method of CMD """
        pass

    def do_create(self, args):
        """ Create an object of any class """
        if not args:
            print("** class name missing **")
            return

        class_name, *params = shlex.split(args)
        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        new_instance = self.classes[class_name]()

        for param in params:
            try:
                key, value = param.split('=')
                value = self.parse_value(value)
                setattr(new_instance, key, value)
            except ValueError:
                continue

        storage.save()
        print(new_instance.id)

    def parse_value(self, value):
        """ Helper function to parse values into their appropriate types """
        if '.' in value:
            return float(value)
        elif value.isdigit() or (value[0] == '-' and value[1:].isdigit()):
            return int(value)
        return value.replace('"', '').replace('_', ' ')

    def help_create(self):
        """ Help information for the create method """
        print("Creates a class of any type")
        print("[Usage]: create <className> <param1=value1> <param2=value2> ...\n")

    def do_show(self, args):
        """ Method to show an individual object """
        class_name, obj_id = self.parse_args(args)

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if not obj_id:
            print("** instance id missing **")
            return

        key = f"{class_name}.{obj_id}"
        obj = storage.all().get(key)
        if obj:
            print(obj)
        else:
            print("** no instance found **")

    def help_show(self):
        """ Help information for the show command """
        print("Shows an individual instance of a class")
        print("[Usage]: show <className> <objectId>\n")

    def do_destroy(self, args):
        """ Destroys a specified object """
        class_name, obj_id = self.parse_args(args)

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if not obj_id:
            print("** instance id missing **")
            return

        key = f"{class_name}.{obj_id}"
        if key in storage.all():
            del storage.all()[key]
            storage.save()
        else:
            print("** no instance found **")

    def help_destroy(self):
        """ Help information for the destroy command """
        print("Destroys an individual instance of a class")
        print("[Usage]: destroy <className> <objectId>\n")

    def do_all(self, args):
        """ Shows all objects, or all objects of a class """
        class_name = args.strip()
        obj_list = []

        if class_name and class_name not in self.classes:
            print("** class doesn't exist **")
            return

        for key, obj in storage.all().items():
            if not class_name or key.startswith(class_name):
                obj_list.append(str(obj))

        print(obj_list)

    def help_all(self):
        """ Help information for the all command """
        print("Shows all objects, or all of a class")
        print("[Usage]: all <className>\n")

    def do_count(self, args):
        """ Count current number of class instances """
        class_name = args.strip()
        if class_name in self.classes:
            count = sum(1 for key in storage.all() if key.startswith(class_name))
            print(count)
        else:
            print("** class doesn't exist **")

    def help_count(self):
        """ Help information for the count command """
        print("Usage: count <class_name>")

    def do_update(self, args):
        """ Updates a certain object with new info """
        class_name, obj_id, attr_name, attr_val = self.parse_update_args(args)

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if not obj_id:
            print("** instance id missing **")
            return

        key = f"{class_name}.{obj_id}"
        obj = storage.all().get(key)
        if not obj:
            print("** no instance found **")
            return

        if not attr_name:
            print("** attribute name missing **")
            return

        if not attr_val:
            print("** value missing **")
            return

        if attr_name in self.types:
            attr_val = self.types[attr_name](attr_val)

        setattr(obj, attr_name, attr_val)
        obj.save()

    def parse_update_args(self, args):
        """ Helper function to parse update arguments """
        args = shlex.split(args)
        if len(args) < 2:
            return args + [None] * (4 - len(args))
        elif len(args) < 4:
            return args + [None]
        return args

    def help_update(self):
        """ Help information for the update class """
        print("Updates an object with new information")
        print("Usage: update <className> <id> <attrName> <attrVal>\n")

    def parse_args(self, args):
        """ Helper function to parse class and id arguments """
        return args.split()

if __name__ == "__main__":
    HBNBCommand().cmdloop()
