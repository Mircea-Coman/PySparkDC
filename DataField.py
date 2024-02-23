import numpy as np

class DataField:


    def __init__(self, values, name, unit, concatenation_type = 'normal'):
        self.values = values
        self.name = name
        self.unit = unit
        if concatenation_type == 'normal' or concatenation_type == 'additive':
            self.concatenation_type = concatenation_type
        else:
            raise ValueError("Invalid concatenation type! Valid values: normal, additive")

    def __get__(self, instance, owner):
        print("AAA")


    @staticmethod
    def concatenate(field_1, field_2):
        if field_1.name  == field_2.name and field_1.unit  == field_2.unit and field_1.concatenation_type  == field_2.concatenation_type:
            new_field = DataField(np.array([]), field_1.name, field_1.unit, concatenation_type = field_1.concatenation_type)
            if(field_1.concatenation_type == 'normal'):
                new_field.values = np.concatenate([field_1.values, field_2.values])
                return new_field

            elif (field_1.concatenation_type == 'additive'):
                field_1_not_empty = not field_1.value.is_empty()
                prev_value = self.value[-1] if field_1_not_empty else 0
                new_field.values = np.concatenate([field_1.values,  prev_value + field_2.values])
                return new_field
            else:
                raise ValueError("Invalid concatenation type! Valid values: normal, additive")
        else:
            raise ValueError("Fields are of different types!")
