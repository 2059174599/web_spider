from pykafka import KafkaClient
import logging, json
from eversec.settings import DATABASE

logger = logging.getLogger('eversec.toKafka')

class KafkaTest(object):
    """
    kafka消息队列
    document：https://github.com/Parsely/pykafka
    """
    def __init__(self):
        self.producerHostList = DATABASE['kafka']['product'] if DATABASE['kafka'] else []
        self.zookeeperHostList = DATABASE['kafka']['consumer'] if DATABASE['kafka'] else []
        self.client = KafkaClient(hosts=','.join(self.producerHostList))

    def getProduct(self):
        return KafkaClient(hosts=','.join(self.producerHostList)).topics

    def getConsumer(self):
        return KafkaClient(hosts=','.join(self.zookeeperHostList)).topics

    def checkTopic(self, index=0):
        """
        检查数据源topic是否满足要求
        """
        topics = self.getProduct()
        return SOURCE_TOPICS[index] in topics

    def simple_consumer(self, topic, offset=0):
        """
        消费者指定消费
        :param offset:
        :return:
        """

        topic = self.client.topics[topic.encode()]
        partitions = topic.partitions
        last_offset = topic.latest_available_offsets()
        print("最近可用offset {}".format(last_offset))  # 查看所有分区
        consumer = topic.get_simple_consumer(b"simple_consumer_group", partitions=[partitions[0]])  # 选择一个分区进行消费
        offset_list = consumer.held_offsets
        print("当前消费者分区offset情况{}".format(offset_list))  # 消费者拥有的分区offset的情况
        consumer.reset_offsets([(partitions[0], offset)])  # 设置offset
        msg = consumer.consume()
        print("消费 :{}".format(msg.value.decode()))
        msg = consumer.consume()
        print("消费 :{}".format(msg.value.decode()))
        msg = consumer.consume()
        print("消费 :{}".format(msg.value.decode()))
        offset = consumer.held_offsets
        print("当前消费者分区offset情况{}".format(offset))  # 3

    def balance_consumer(self, topic):
        """
        使用balance consumer去消费kafka
        :return:
        """
        client = KafkaClient(hosts=','.join(self.producerHostList))
        logger.info('topics: {}'.format(client.topics))
        print('topics: {}'.format(client.topics))
        topic = client.topics[topic]
        # managed=True 设置后，使用新式reblance分区方法，不需要使用zk，而False是通过zk来实现reblance的需要使用zk
        consumer = topic.get_balanced_consumer(consumer_group=b'test_group_2',  # LC().kafka.consumer['consumer_group'],
                                               # managed=True,
                                               # 设置为False的时候不需要添加consumer_group，直接连接topic即可取到消息
                                               auto_commit_enable=True,
                                               auto_commit_interval_ms=1,
                                               # 这里就是连接多个zk
                                               zookeeper_connect=','.join(self.zookeeperHostList)
                                               )
        # consumer = topic.get_simple_consumer()
        for message in consumer:
            if message is not None:
                 logger.info('message.value {}'.format(message.value))
                 yield message.value


    def async_produce_message(self, message,topic):
        """
        异步生产
        """
        topics = self.client.topics[topic]
        with topics.get_producer(sync=False, delivery_reports=True) as producer:
            res = json.dumps(message, ensure_ascii=False).encode()
            # res = message.encode()
            producer.produce(res)
            logger.info('finish topic:{}, message:{}'.format(topic, message))
            #msg, exc = producer.get_delivery_report(block=False)
            #if exc is not None:
            #    logger.error('Failed to deliver msg {}: {}'.format(msg.partition_key, repr(exc)))
            #else:
            #    logger.info('Successfully delivered msg {}'.format(msg.partition_key))



if __name__ == '__main__':
    kafka_ins = KafkaTest()
    # for i in kafka_ins.balance_consumer(topic):
    #     print(i.decode())
    msg = {'name': '金属狂潮', 'apksize': '96.13M', 'downloadUrl': 'https://game.gionee.com/Front/Index/tj/?type=1&_url=https%3A%2F%2Fgamedl.gionee.com%2FAttachments%2Fdev%2Fapks%2F2022%2F01%2F17%2F1642388626251.apk%3Fcku%3D2515193743_null%26action%3Ddlpc%26object%3Dcom.jskc.jinli%26intersrc%3Dgamedetail_gid19670', 'version': '5.0', 'introduce': '游戏以末日废土为背景，拥有丰富的四个不同阵营且特点鲜明的角色，回合制玩法加自动点击，让战斗更有趣味。多线性的收集养成，自由多样的阵容搭配，满足你的收集和养成欲望。', 'developer': '上海技乐网络科技有限公司', 'category': '游戏', 'updatetime': '2022-01-21', 'icon_url': 'https://s-dev.gionee.com/Attachments/dev/icons/2021/12/09/61b1a1c3aa3c1.png.144.png', 'sceenshot_url': "['https://s-dev.gionee.com/Attachments/dev/screens/2021/12/09/61b1a1a6b85ec_480x800.jpg', 'https://s-dev.gionee.com/Attachments/dev/screens/2021/12/09/61b1a1aab3e34_480x800.jpg', 'https://s-dev.gionee.com/Attachments/dev/screens/2021/12/09/61b1a1ae8b47c_480x800.jpg', 'https://s-dev.gionee.com/Attachments/dev/screens/2021/12/09/61b1a1b2b61d9_480x800.jpg', 'https://s-dev.gionee.com/Attachments/dev/screens/2021/12/09/61b1a1bd156d1_480x800.jpg']", 'shop': '金立游戏商城', 'url': 'https://game.gionee.com/Front/Game/detail/?id=19670&cku=2515193743_null&action=visit&object=gamedetail19670&intersrc=category100_new_gid19670', 'jsonObject': {'time': '2022-01-25 20:34:19'}, 'province': '上海市', 'city': '上 海市', 'dlamount': '', 'source': 'pc'}
    print(msg)
    # print(json.dumps(msg, ensure_ascii=False))
    # kafka_ins.async_produce_message(msg, topic)
    # from kafka import KafkaConsumer
    #
    # consumer = KafkaConsumer(topic,bootstrap_servers='192.168.205.232:29094')
    # print(consumer.metrics())
    # for msg in consumer:
    #     print(msg)
