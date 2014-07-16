import sys

class messageIO():
    '''MessageIO an object used to hide the IO logic from scripts''' 
    def __init__(self, request_code=None, device=None, string=None):
        #Set the objects variable(s)
        self.devices = []
                
        #Run the main function if request_code is provided
        if request_code:
            self.messageIO(request_code, device, string)
    
    def checkDevice(self, device, string):
        #If the device already exists return True
        for dvc in self.devices:
            device_same = dvc.get_type() == device
            param_same = dvc.get_param() == string
            if device_same and param_same:
                return True
        return False
    
    def messageIO(self, request_code=None, device=None, string=None):
        #Verify the request_code
        if request_code == 'REQopen':
            #check for matching sets
            is_list =  (isinstance(device,list) or isinstance(device,tuple)) and (isinstance(string,list) or isinstance(string,tuple))
            is_string = isinstance(device,str) and isinstance(string,str)
            
            #If the device is a list loop through the values
            if is_list:
                if not len(string) == len(device):
                    raise Exception('string list size mismatch')
            #format strings as tuples
            elif is_string:
                device = (device,)
                string = (string,)
            else:
                raise Exception('Invalid device/string types')
            
            for device_itr, string_itr in zip(device, string):
                #Device opening 
                if not self.checkDevice( device_itr, string_itr ):
                    if device_itr == 'file':
                        #Create a file type object
                        self.devices.append( File(string_itr) )
                    elif device_itr == 'console':
                        #Open console writing
                        self.devices.append( Console(string_itr) )
                    else:
                        #Device code does not exist
                        raise Exception('Device type {0} does not exist'.format(device_itr))
                else:
                    raise Exception('Device already exists')

        elif request_code == 'REQput':
            # Writes strings to files
            for dvc in self.devices:
                dvc.put(string)
                
        elif request_code == 'REQclose':
            # Close all devices
            for dvc in self.devices:
                dvc.close()
            
            # Clear list of devices
            self.devices = []
        elif request_code == 'REQget':
            #TODO: implement at a later time
            pass

        
#Device classes
class Device():
    #Parent Device Class
    def __init__(self, param = None):
        self.param = param
        self.type = 'device'
    
    def get_param(self):
        return self.param
    
    def get_type(self):
        return self.type

    def put(self, string):
        pass
    
    def close(self):
        pass
    
class File(Device):  
    #File Device   
    def __init__(self, param = None):
        self.param = param   
        self.type = 'file'
        self.fileh = None
        self.open_file(self.param)
        
    def open_file(self, path):
        self.fileh = open(path,'a+')
    
    def put(self, string):
        self.fileh.write(string)
        
    def close(self):
        self.fileh.close()
        
class Console(Device):   
    #Console Device  
    def __init__(self, param = None):
        self.param = param   
        self.type = 'console'
    
    def put(self, string):
        sys.stdout.write(string)
        
