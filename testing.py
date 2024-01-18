class car:
    myvar = 0
    def __init__(self) -> None:
        self.color = 'red'
        self.engine = '2jz'
        self.type = 'suv'
    @staticmethod
    def print_all(self):

        print(f'color is {self.color}\nengine is {self.engine}\ntype is {self.type}')

    def changemyvar(self,value):

        self.myvar = value

def print_global_variable():
    print(global_variable)
    print('pepsi')
# Global variable defined after the function
global_variable = "I am a global variable"

# Call the function
print_global_variable()
