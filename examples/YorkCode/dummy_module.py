            #####################################################
            #  This code is imported by the example code above. #
            #       Copypaste it into 'dummy_module.py'         #
            #####################################################
class Camera:
    def record(self, out):
        out.fill(1)

class Preprocessor:
    def process(self, x, out):
        x.max(axis=0, out=out)

class Display:
    def show(self, image):
        pass