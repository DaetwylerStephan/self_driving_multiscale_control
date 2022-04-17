
class functiontest():
    def __init__(self):
        # init it
        self.current_positionfilepath = 'D:/acquisitions/testimage.txt'

if __name__ == '__main__':

    c = functiontest()
    print(c.current_positionfilepath)
    c.current_positionfilepath ="test"
    print(c.current_positionfilepath)
    testit = c.current_positionfilepath
    print(testit)
    c.current_positionfilepath = "test2"
    print(c.current_positionfilepath)
    print(testit)
