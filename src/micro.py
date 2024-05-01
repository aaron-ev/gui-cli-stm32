
class Micro():
    supportedGpios  = ['gpioa', 
                       'gpiob',
                       'gpioc',
                       'gpiod',
                       'gpioe',
                       'gpioh'
                       ]
    supportedPins = (0, 15)
    def __init__(self):
        pass
    
    def getSupportedPins(self):
        return self.supportedPins

    def getSupportedGpios(self):
            return self.supportedGpios
