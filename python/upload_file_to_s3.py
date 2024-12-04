# -*-coding:utf-8-*-
import time

from minio import Minio
import os

basePath="C:/Users/LiuYang/Downloads/"
def work():
    folder_list = os.listdir(basePath)
    for tmpFolder in folder_list:
        print("&" * 60)
        print (tmpFolder)
        if os.path.isdir(basePath+tmpFolder):
            for tmpFile in os.listdir(basePath+tmpFolder):
                print ("="*60)
                print (basePath+tmpFolder+"/"+tmpFile)
                destFilePath = "[%s]%s" % (tmpFolder, tmpFile)
                print (destFilePath)
                upload_file(basePath+tmpFolder+"/"+tmpFile, destFilePath)
                # time.sleep(0.1)
def upload_file(sourcepath, targetpath):
    # minio_client = Minio(
    #     '192.168.1.113:9000',
    #     access_key='aiVQtdmzTrg8ijR9iBvC',
    #     secret_key='lVWr51xizRNGqssQnKamKXIZxsVI3hdXHtPyNZzQ',
    #     secure=False
    # )

    minio_client = Minio(
        '192.168.1.107:9000',
        access_key='qBPz2OTL3ExDazb2L2uV',
        secret_key='qz4RoRiEfVFyBdya72OdzrRNUsuTdw9Vc8Vsg5Tw',
        secure=False
    )
    bucket_name = "bilibili"
    print ("source file path {}".format(sourcepath))
    print ("target file path {}".format(targetpath))
    minio_client.fput_object(bucket_name=bucket_name, object_name="{}".format(targetpath),file_path=sourcepath)


if __name__=='__main__':
    work()