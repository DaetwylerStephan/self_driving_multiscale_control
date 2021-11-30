from tifffile import imread, imwrite
import napari


if __name__ == '__main__': #needed for threading of napari in subprocess

    filename= "D://multiScope_Data/20211119_Daetwyler_Xenograft/Experiment0002/t00000/low_stack000/1_CH488_000000.tif"

    imstack1 = imread(filename)
    print(imstack1.shape)
    print(imstack1.dtype)

    # print("The mean of the TIFF stack (whole stack!) is:")
    # print(imstack1.mean())
    #
    with napari.gui_qt():
        # create the viewer with an image
        viewer = napari.view_image(imstack1)

