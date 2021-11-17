import auxiliary_code.concurrency_tools as ct
import src.slit.slit_cmd as SlitControl

class slitmodel:
    def __init__(
        self
        ):

        slit_init = ct.ResultThread(target=self._init_slit).start()  #
        slit_init.get_result()


    def _init_slit(self):
        """
        Initialize motorized slit
        """
        self.adjustableslit = SlitControl.slit_ximc_control()
        #self.adjustableslit.slit_info()
        # self.adjustableslit.slit_status()
        # self.adjustableslit.slit_set_microstep_mode_256()
        # self.adjustableslit.home_stage()
        # print("slit homed")
        # self.adjustableslit.slit_set_speed(1000)

if __name__ == '__main__':
    # first code to run in the multiscope

    # Create scope object:
    model = slitmodel()
    input()