


class write_Params:
    def __init__(self, view):
        self.view = view


    def write_to_textfile(self, filePath):
        with open(filePath, 'w') as f:
            f.write('Experiment parameters of ' + filePath + "\n")
            f.write('---------------------------------------------\n')
            f.write('Plane spacing lowres: ' + str(self.view.runtab.stack_aq_plane_spacing_lowres.get()) + "\n")
            f.write('Plane spacing highres: ' + str(self.view.runtab.stack_aq_plane_spacing_highres.get()) + "\n")
            f.write('Nb of planes lowres: ' + str(self.view.runtab.stack_aq_numberOfPlanes_lowres.get()) + "\n")
            f.write('Nb of planes highres: ' + str(self.view.runtab.stack_aq_numberOfPlanes_highres.get()) + "\n")

            f.write('---------------------------------------------\n')
            f.write('low resolution stack positions\n')

            for iter_lowrespos in self.view.stagessettingstab.stage_savedPos_tree.get_children():
                #get current position from list
                xpos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][1]))
                ypos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][2]))
                zpos = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][3]))
                angle = int(float(self.view.stagessettingstab.stage_savedPos_tree.item(iter_lowrespos)['values'][4]))
                current_startposition = [zpos, xpos, ypos, angle]
                f.write(str(current_startposition) + "\n")

            f.write('\n---------------------------------------------\n')
            f.write('high resolution stack positions\n')

            for iter_highrespos in self.view.stagessettingstab.stage_highres_savedPos_tree.get_children():
                #get current position from list
                xpos = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(iter_highrespos)['values'][1]))
                ypos = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(iter_highrespos)['values'][2]))
                zpos = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(iter_highrespos)['values'][3]))
                angle = int(float(self.view.stagessettingstab.stage_highres_savedPos_tree.item(iter_highrespos)['values'][4]))
                current_startposition = [zpos, xpos, ypos, angle]
                f.write(str(current_startposition) + "\n")