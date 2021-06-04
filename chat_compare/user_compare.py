#!/user/bin/python
# -*- coding: UTF-8 -*-
import json
from multiprocessing.pool import ThreadPool

import web
import time

web.config.debug = False

tdb = web.database(dbn='mysql', host='172.16.0.115', port=3306, db='administration', user='app', pw='Yc)E7aqYU6)AjW')
sdb = web.database(dbn='mysql', host='172.16.0.115', port=3306, db='crm', user='app', pw='Yc)E7aqYU6)AjW')


def administration_external_user(chat_id):
    where = "chat_id = '%s'" % chat_id
    external_user_list = list(
        tdb.select('work_wechat_group_member_info', what='external_user_id', where=where))
    administration_list = [x.external_user_id for x in external_user_list]
    return administration_list


def crm_external_user(chat_id):
    crm_list = []
    where = "channel_chat_id = '%s'" % chat_id
    # 去一下work_group的总数
    group_sn_list = list(
        sdb.select('work_group', what='group_sn', where=where))
    if len(group_sn_list) > 0:
        channel_user_list = list(
            sdb.select('work_group_member', what='member_channel_user_id', where='group_sn in $group_ids',
                       vars={'group_ids': [i.group_sn for i in group_sn_list]}))
        crm_list = [x.member_channel_user_id for x in channel_user_list]
    return crm_list


def run_test(chat_ids):
    for k in chat_ids:
        # mock
        # k = 'wrwlQrCAAA9tGMsCjiPJt8b36CZaLKow'
        print('>>>>>>>>开始对比chat_id:[%s]<<<<<<<<<<' % k)
        # 用户list
        administration_list = administration_external_user(k)
        crm_list = crm_external_user(k)
        if len(administration_list) != 0 and len(crm_list) != 0:
            # 交集
            ret_list1 = list(
                (set(administration_list).union(set(crm_list))) ^ (set(administration_list) ^ set(crm_list)))
            # 两个list对比
            administration_list_only = list(set(administration_list) ^ set(ret_list1))
            crm_list_only = list(set(crm_list) ^ set(ret_list1))
            if len(administration_list_only) > 0:
                temp = ''
                for i in administration_list_only:
                    temp = temp + i + ','
                print('FAIL: administration多绑定用户chat_id是[%s];微信名是:[%s]' % (k, administration_list_only))
            if len(crm_list_only) > 0:
                temp = ''
                for i in crm_list_only:
                    temp = temp + i + ' , '
                print('FAIL: crm多绑定用户chat_id是[%s];微信名是:[%s]' % (k, crm_list_only))

        else:
            print('FAIL: 内容为空 [%s] [administration_list]:%s  [crm_list]:%s' % (k, administration_list, crm_list))


def run_many_thread_chat(start, end, limit=200):
    """
    多线程
    :param start:
    :param end:
    :param limit:
    :return:
    """
    start = time.strptime(start, "%Y-%m-%d %H:%M:%S")
    end = time.strptime(end, "%Y-%m-%d %H:%M:%S")
    # 转为时间戳
    start = str(int(time.mktime(start)) * 1000)
    end = str(int(time.mktime(end)) * 1000)
    where = "select count(*) as cnt from work_wechat_group_info where created_at >= %s and created_at <= %s and dismiss_at = 0" % (start, end)
    where_work_group = "select count(*) as group_cnt from work_group where created_at >= %s and created_at <= %s " % (start, end)
    work_group_total = list(sdb.query(where_work_group))[0]['group_cnt']
    #item_total = list(tdb.query(where))[0]['cnt']
    item_total = tdb.query(where)[0]['cnt']
    page_total = int(item_total / limit if item_total % limit == 0 else item_total / limit + 1)
    print('work_wechat_group_info的总数是:%s' % item_total)
    print('work_group的总数是:%s' % work_group_total)
    #print("总数:{};总页数:{}".format(item_total, page_total))
    pool = ThreadPool(10)
    for i in range(0, page_total):
        pool.apply_async(func=run_many_thread_chat_run, args=(start, end, limit, page_total, i))
    pool.close()  # 关闭线程池 不再提交任务
    pool.join()
    print("总数:{};总页数:{}".format(item_total, page_total))
    print('compare end')


def run_many_thread_chat_run(start, end, limit=200, page_total=0, page=0):
    """
    多线程执行
    :param start:
    :param end:
    :param limit:
    :param page_total:
    :param page:
    :return:
    """
    offset = page * limit
    #print('开始执行{}/{},页大小:{}页偏移量:{}'.format(page + 1, page_total, limit, offset))
    where = "created_at >= %s and created_at <= %s and dismiss_at = 0" % (start, end)
    chat_list = list(
        tdb.select('work_wechat_group_info', what='chat_id', where=where, limit=limit, offset=offset))
    chat_ids = [x.chat_id for x in chat_list]
    if len(chat_ids) == 0:
        print('执行完毕 {}/{},页大小:{}页偏移量:{}'.format(page + 1, page_total, limit, offset))
        return None
    # 开始执行对比
    run_test(chat_ids)
    print('执行完毕 {}/{},页大小:{}页偏移量:{}'.format(page + 1, page_total, limit, offset))
    return


if __name__ == '__main__':
    run_many_thread_chat("2020-06-03 10:30:40", "2021-06-03 11:31:41")
