import numpy as np

class DataField(np.ndarray):


    def __new__(cls, input_array, name, unit, concatenation_type = 'normal'):
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.unit = unit
        if concatenation_type == 'normal' or concatenation_type == 'additive':
            obj.concatenation_type = concatenation_type
        else:
            raise ValueError("Invalid concatenation type! Valid values: normal, additive")
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.name = getattr(obj, 'name', None)
        self.unit = getattr(obj, 'unit', None)
        self.concatenation_type = getattr(obj, 'concatenation_type', None)

    # def __init__(self, values, name, unit, concatenation_type = 'normal'):
    #     self.values = values
    #     self.name = name
    #     self.unit = unit

    def __get__(self, instance, owner):
        print("AAA")


    @staticmethod
    def concatenate(field_1, field_2):
        if field_1.name  == field_2.name and field_1.unit  == field_2.unit and field_1.concatenation_type  == field_2.concatenation_type:
            if(field_1.concatenation_type == 'normal'):
                joined_array = np.concatenate([field_1, field_2])
                joined_field = DataField(joined_array, field_1.name, field_1.unit, concatenation_type = field_1.concatenation_type)
                return joined_field

            elif (field_1.concatenation_type == 'additive'):
                field_1_not_empty = not field_1.is_empty()
                prev_value = field_1[-1] if field_1_not_empty else 0
                joined_array = np.concatenate([field_1,  prev_value + field_2])
                joined_field = DataField(joined_array, field_1.name, field_1.unit, concatenation_type = field_1.concatenation_type)

                return joined_field
            else:
                raise ValueError("Invalid concatenation type! Valid values: normal, additive")
        else:
            raise ValueError("Fields are of different types!")
