               ####################################################
                #  EXAMPLE CODE (copypaste into 'test.py' and run) #
                ####################################################
from proxy_objects import ProxyManager, launch_custody_thread
from dummy_module import Camera, Preprocessor, Display

def main():
    pm = ProxyManager(shared_memory_sizes=(10*2000*2000*2, # Two data buffers
                                           10*2000*2000*2,
                                            1*2000*2000*1, # Two display buffers
                                            1*2000*2000*1))
    data_buffers = [pm.shared_numpy_array(0, (10, 2000, 2000), 'uint16'),
                    pm.shared_numpy_array(1, (10, 2000, 2000), 'uint16')]
    display_buffers = [pm.shared_numpy_array(2, (2000, 2000), 'uint8'),
                       pm.shared_numpy_array(3, (2000, 2000), 'uint8')]

    camera = pm.proxy_object(Camera)
    preprocessor = pm.proxy_object(Preprocessor)
    display = pm.proxy_object(Display)

    def snap(data_buffer, display_buffer, custody):
        custody.switch_from(None, to=camera)
        camera.record(out=data_buffer)

        custody.switch_from(camera, to=preprocessor)
        preprocessor.process(data_buffer, out=display_buffer)

        custody.switch_from(preprocessor, to=display)
        display.show(display_buffer)

        custody.switch_from(display, to=None)

    for i in range(15):
        th0 = launch_custody_thread(target=snap, first_resource=camera,
                            args=(data_buffers[0], display_buffers[0]))
        if i > 0:
            th1.join()
        th1 = launch_custody_thread(target=snap, first_resource=camera,
                            args=(data_buffers[1], display_buffers[1]))
        th0.join()
    th1.join()

if __name__ == '__main__':
    main()
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