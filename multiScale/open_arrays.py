from concurrency_tools import SharedNDArray

list_iter =[]
for iter in range(0,100):
    data_buf =  SharedNDArray(shape=(400, 1000, 1000), dtype='uint16')
    data_buf[::10, ::10, ::10] = 7
    list_iter.append(data_buf)
    print(iter)

print(list_iter[3].mean())
input()