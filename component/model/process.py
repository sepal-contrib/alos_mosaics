# It is strongly suggested to us a separate file to define the io of your tile and process. 
# it will help you to have control over it's fonctionality using object oriented programming

# in python variable are not mutable object (their value cannot be changed in a function)
# Thus use a class to define your input and output in order to have mutable variables

from sepal_ui import model
from traitlets import Any

class Process (model.Model):
        
        # set up your inputs
        year = Any(None).tag(sync=True)
        filter = Any(None).tag(sync=True)
        scale = Any(30).tag(sync=True)
        dB = Any(True).tag(sync=True)
        ls_mask = Any(True).tag(sync=True)
        backscatter = Any(True).tag(sync=True)
        rfdi = Any(True).tag(sync=True)
        fnf = Any(False).tag(sync=True)
        texture = Any(False).tag(sync=True)
        aux = Any(False).tag(sync=True)
        viz = Any('RGB').tag(sync=True)
        scale = Any(25).tag(sync=True)
    
        # set up your outputs
        asset_id = Any(None).tag(sync=True)
        dataset  = Any(None).tag(sync=True)