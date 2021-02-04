# It is strongly suggested to us a separate file to define the io of your tile and process. 
# it will help you to have control over it's fonctionality using object oriented programming

# in python variable are not mutable object (their value cannot be changed in a function)
# Thus use a class to define your input and output in order to have mutable variables
class Process:
    def __init__(self):
        
        # set up your inputs
        self.year   = None
        self.asset  = None
        self.filter = None
        self.rfdi = None
        self.ls_mask = None
        self.dB = None
    
        # set up your outputs
        self.asset_id = None
        self.dataset  = None