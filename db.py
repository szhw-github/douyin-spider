
from pymongo import MongoClient,ASCENDING
from settings import DATABASE,CLIENT,COLLECTION


def login_mongodb():
    """
    连接mognodb
    :return: 数据库的集合
    """
    client=MongoClient(CLIENT)
    db=client[DATABASE]
    collection=db[COLLECTION]
    collection.create_index([('id', ASCENDING)], unique=True)
    return collection

