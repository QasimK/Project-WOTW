"""Convert the excel csv file to a json file (WOTW Particular)

commandline:
argument1 = input filename
argument2 = output filename (optional, default: output_json.json)

Format of csv: see Model
"""

import sys, csv
import types
import copy

def output_error(error_message):
    raw_input(error_message+"\nPress enter to continue...")

class type_list_single(object):
    """A single list object
    
    eg. ["Damage"]
    """
    pass

def get_defined_models():
    return [
        Model("game.itemproperty", {
            "name": (types.StringType, False), #False=Required
            "sname": (types.StringType, True)  #True = Optional
        }),
        Model("game.item", {
            "name": (types.StringType, False),
            "is_unlimited_stack": (types.BooleanType, False),
            "max_stack_size": (types.IntType, True)
        }),
        Model("game.itempropertyinfo", {
            "item": (type_list_single, False),
            "item_property": (type_list_single, False),
            "value": (types.StringType, False)
        }),
        Model("game.monster", {
            "name": (types.StringType, False),
            "hp": (types.IntType, False),
            "hp_dev": (types.IntType, False),
            "weapon": (type_list_single, False),
            "armour": (type_list_single, False),
            "gold": (types.IntType, True),
            "gold_dev": (types.IntType, True)
        }),
        Model("game.inventory", {
            "is_unlimited": (types.BooleanType, False),
            "size": (types.IntType, True)
        }),
        Model("game.inventoryiteminfo", {
            "inventory": (types.IntType, False),
            "item": (type_list_single, False),
            "stack_size": (types.IntType, False)
        }),
        Model("game.shop", {
            "name": (types.StringType, False),
            "inventory": (types.IntType, False)
        }),
        Model("game.gameview", {
            "name": (types.StringType, False),
        }),
        Model("game.character", {
            "user_account": (types.IntType, False),
            "inventory": (types.IntType, False)
        }),
        Model("auth.user", {
            "username": (types.StringType, False),
            "first_name": (types.StringType, True),
            "last_name": (types.StringType, True),
            "is_active": (types.BooleanType, False),
            "is_superuser": (types.BooleanType, False),
            "is_staff": (types.BooleanType, False),
            "last_login": (types.StringType, False),
            "groups": (type_list_single, False),
            "user_permissions": (type_list_single, False),
            "password": (types.StringType, False),
            "email": (types.StringType, True),
            "date_joined": (types.StringType, False)
        }),
    ]

def select_model(model_name, list_of_models):
    """Return the Model object or None for failure"""
    for model in list_of_models:
        if model.name == model_name:
            return model


class Model(object):
    """A model which has a name and certain fields
    and data corresponding to those fields
    
    eg. django output:
    {
        "pk": 1,
        "model": "game.itemproperty",
        "fields": {
            "field1": "string",
            "field2": 23
        }
    }
    
    1- pk is automatically done
    2- model is the django model name
    3- fields must be specified (they may be optional and of a particular type)
    
    The model must correspond to what is in the csv file
    The field names must correspond to what is in the csv file
    
    eg. csv file:
    model, game.itemproperty
    field1, field2
    string, 23
    morestuff,
    endmodel
    
    As you can see the field2 was set to be optional
    Also you must have the endmodel to indicate the end of the model
    """
    
    def __init__(self, name, fields={}):
        """Set the model name and optionally fields"""
        self.name = name
        self.fields = fields
        self.data = []
        #eg.
        #{"field1": "string", "field2": 23}
    
    def add_field(self, field_name, data_type, optional):
        """Add a possible field with its data_type and whether it is optional"""
        if field_name in self.fields:
            raise KeyError("Field name already in model")
        self.fields[field_name] = (data_type, optional)
    
    def set_fields(self, fields):
        """Set the fields dictionary (overrides existing fields)"""
        self.fields = fields
    
    def add_data(self, data_dict):
        """Add a complete model of this, eg.
        data_dict = {
            "field1": "string",
            "field2": 23
        }"""
        self.data.append(data_dict)
    
    def validate(self):
        """Validate that required data is in, Return true/false"""
        name_optional = []
        for field, etc in self.fields.iteritems():
            name_optional.append((field, etc[1]))
        
        for item in self.data:
            fields_has = []
            for field, value in item.iteritems():
                #Check it is a valid field
                if field not in self.fields.iterkeys():
                    return False, "Not a valid field: %s" % field
                fields_has.append(field)
                
                #Check that the data type is correct
                etc = self.fields[field]
                data_type = etc[0]
                if data_type == types.BooleanType:
                    if value.lower() != "true" and value.lower() != "false":
                        return False, "Type error: Boolean required\n"+\
                                "field: %s, value: %s"%(field, value)
                elif data_type == types.IntType:
                    try:
                        int(value)
                    except ValueError:
                        return False, "Type error: Int required\n"+\
                                "field: %s, value: %s"%(field, value)
                elif data_type == type_list_single:
                    if value != "[]":
                        new_value = value
                        if value[0:2] != '["':
                            new_value = '["' + new_value
                        if value[-2:] != '"]':
                            new_value = new_value + '"]'
                        item[field] = new_value
            
            #Check that all required fields are present
            for field_name, etc in self.fields.iteritems():
                data_type = etc[0]
                optional = etc[1]
                if not optional and field_name not in fields_has:
                    return False, "Missing field: %s" % field_name
        
        return True, ""
    
    
    def get_output_string(self):
        """Return the output string corresponding to this model"""
        pass


def remove_empty_end(row):
    """Remove empty commas from the end of the row
    
    eg. test, test,,test,,,
    will become test, test,,test
    """
    row_copy = copy.copy(row)
    while len(row_copy) > 0:
        item = row_copy.pop()
        if item != "":
            row_copy.append(item)
            return row_copy

def write_indents(file, indent_level):
    file.write(" "*4*indent_level)


if __name__ == "__main__":
    #Input and output filenames
    csvfile_name = sys.argv[1]
    output_name = sys.argv[2]
    
    #Defined models
    models = get_defined_models()
    
    #Parse CSV
    current_model = None
    set_order = False #The field order used to correspond to model fields
    row_order = []
    with open(csvfile_name, 'rb') as csvfile:
        reader = csv.reader(csvfile, 'excel')
        for row in reader:
            #Pick what model to use
            if current_model == None:
                if row[0] == "model":
                    model_name = row[1]
                    current_model = select_model(model_name, models)
                    
                    if current_model == None:
                        error_msg = "Corresponding model to: %s not found"\
                                    % model_name
                        raise KeyError(error_msg)
                    
            else: #We are already in a model
                #End of model
                if row[0] == "endmodel":
                    current_model = None
                    set_order = False
                    row_order = []
                else:
                    if not set_order:
                        #Set the row_order the fields appear in
                        row_order = remove_empty_end(row)
                        set_order = True
                    else:
                        #Now just parse the data
                        data = {}
                        
                        required_section = row[:len(row_order)]
                        for i, value in enumerate(required_section):
                            if value != "":
                                data[row_order[i]] = value
                        current_model.add_data(data)
                        vsuccess, msg = current_model.validate()
                        if not vsuccess:
                            raise ValueError("Model does not validate\n"+
                                         str(row)+"\n"+
                                         msg)
    
    if current_model != None:
        raise Exception("Model did not end: %s" % current_model.name)
    
    #Remove any models not in use
    used_models = []
    for model in models:
        if len(model.data):
            used_models.append(model)
    
    models = used_models
    
    #Output JSON
    indent_level = 0
    with open(output_name, 'w') as output:
        def write_pre():
            write_indents(output, indent_level)
        
        output.write("[\n")
        indent_level += 1
        for i, model in enumerate(models):
            indent_level = 1
            pk = 0
            for ii, modelitem in enumerate(model.data):
                pk += 1
                
                indent_level = 1
                write_pre()
                output.write("{\n")
                
                indent_level = 2
                write_pre()
                output.write('"pk": ' + str(pk) + ',\n')
                write_pre()
                output.write('"model": "%s",\n' % model.name)
                write_pre()
                output.write('"fields": {\n')
                
                #Write fields
                indent_level = 3
                WRITE_STR = ""
                for field, etc in model.fields.iteritems():
                    if field in modelitem:
                        data_type = etc[0]
                        if data_type == types.StringType:
                            ws = '"%s": "%s"'%(field, modelitem[field])
                        elif data_type == types.BooleanType:
                            ws = '"%s": %s'%(field, modelitem[field].lower())
                        else:
                            ws = '"%s": %s'%(field, modelitem[field])
                        WRITE_STR += " "*4*indent_level
                        WRITE_STR += ws + ",\n"
                if len(WRITE_STR) > 1:
                    WRITE_STR = WRITE_STR[:-2] + "\n"
                output.write(WRITE_STR)
                
                
                indent_level = 2                
                write_pre()
                output.write('}\n')
                
                indent_level = 1
                write_pre()
                if i == len(models)-1 and ii == len(model.data)-1:
                    output.write("}\n")
                else:
                    output.write("},\n")
            output.write("\n"*10)
        
        output.write("]")
    