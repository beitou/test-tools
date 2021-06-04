import os
import time
from collections import defaultdict

import pandas as pd
import numpy as np
import xlrd
from jira import JIRA
import datetime
from dateutil.parser import parse
from xlutils.copy import copy

# 连接创建jira对象
QA = [
    "刘丽雨", "陈晨", "陈帅（技术）", "耿金龙", "侯丽娟", "李丽莉", "刘苹苹", "田孝庆",
    "宿宇", "耿金龙", "万莞羚", "刘苹苹", "闫茜", "卫鑫",
    "张力达",
]


#  获取当前工作目录
# cur_path = '../'
# work_path = os.path.join(cur_path, 'iterative_quality_data/')


class JiraOperation:

    def __init__(self, board_id=None, project=None, type=None, sprint=None, create_time=None, end_time=None,
                 col_name=None):
        self.jira = JIRA(auth=("chenshuai2", "Chenshua1&"), options={'server': 'http://jira.xiaobangtouzi.com'})
        self.board_id = board_id
        self.project = project
        self.type = type
        self.sprint = sprint
        self.create_time = create_time
        self.end_time = end_time
        self.col_name = col_name

    def write_value(self, row_name, value):
        """
        向某个单元格写入数据
        :param row_name:
        :param value:
        :return:
        """
        # excel路径
        file_path = '../iterative_quality_data/' + self.project + '.xlsx'
        data = xlrd.open_workbook(file_path)
        sheet = data.sheet_by_name('Sheet1')
        col = sheet.row_values(0).index(self.col_name)  # 定位列
        row = sheet.col_values(1).index(row_name)  # 定位行
        data_copy = copy(data)  # 复制原文件
        sheet_copy = data_copy.get_sheet(0)  # 取得复制文件的sheet对象
        sheet_copy.col(0).width = 256 * 15  # 设置列宽
        sheet_copy.col(1).width = 256 * 20
        sheet_copy.col(2).width = 256 * 40
        sheet_copy.write(row, col, value)  # 在某个单元格中写入value
        data_copy.save(file_path)

    def Time(self, data):
        """
        转化时间
        :param data:
        :return:
        """
        # 创建时间：2021-04-26T15:49:57.000+0800,1
        try:
            date = data.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
            return date
            # 创建时间2021-04-28 11:24:29
        except Exception as e:
            return 0

    def star_time_h(self, data):
        """
        按上班结束时间计算小时
        :param data:
        :return:
        """
        day_work_time = parse("20:0:0")
        stardata_day = str(data).split(' ')[0]
        stardata_time = parse(str(data).split(' ')[1])
        # 大于工作日结束时间记为0
        if stardata_time > day_work_time:
            stardata_h_int = 0
            return stardata_day, stardata_h_int
        else:
            stardata = str(day_work_time - stardata_time)
            stardata_h = int(stardata.split(":")[0])
            # 区分休息时间
            stardata_h_int = 6 if (6 < stardata_h <= 8) else (stardata_h if (stardata_h <= 6) else (stardata_h - 2))
            stardata_m = int(stardata.split(":")[1])
            # 大于30分钟进位1小时（会有误差）
            if stardata_m >= 30:
                stardata_h_int += 1
            return stardata_day, stardata_h_int

    def end_time_h(self, data):
        """
        按上班开始时间计算小时
        :param data:
        :return:
        """
        day_work_time = parse("10:0:0")
        enddata_day = str(data).split(' ')[0]
        enddata_time = parse(str(data).split(' ')[1])
        # 大于工作日结束时间记为0
        if enddata_time < day_work_time:
            enddata_h_int = 0
            return enddata_day, enddata_h_int
        else:
            enddata = str(enddata_time - day_work_time)
            enddata_h = int(enddata.split(":")[0])
            # 区分休息时间
            enddata_h_int = 2 if (2 < enddata_h <= 4) else (enddata_h if (enddata_h <= 2) else (enddata_h - 2))
            enddata_m = int(enddata.split(":")[1])
            # 大于30分钟进位1小时（会有误差）
            if enddata_m >= 30:
                enddata_h_int += 1
            return enddata_day, enddata_h_int

    def working_day_calculation(self, stardata, enddata):
        """
        根据传入时间计算工作小时数，如果结束时间为0，以当前时间创建结束时间
        :param stardata:
        :param enddata:
        :return:
        """
        subtask_time_all = 0
        t1, stardata_h = self.star_time_h(stardata)
        # 如果结束时间为0，以当前时间创建结束时间
        if enddata == 0:
            enddata = str(datetime.datetime.now())
            enddata = enddata.split(".")[0]
            t2, enddata_h = self.end_time_h(enddata)
        else:
            t2, enddata_h = self.end_time_h(enddata)
        # 计算除第一天和最后一天以外的总天数
        days = np.busday_count(t1, t2)
        # 时间差为0，以当天实际开始结束计算
        if days == 0:
            t1 = datetime.datetime.strptime(str(stardata), "%Y-%m-%d %H:%M:%S")
            t2 = datetime.datetime.strptime(str(enddata), "%Y-%m-%d %H:%M:%S")
            total_interval_time = (t2 - t1).total_seconds() / 3600
            subtask_time_all = int(total_interval_time)
        elif days != 0:
            subtask_time_all = ((days - 1) * 8)
            work_time_h = int(stardata_h) + int(enddata_h)
            subtask_time_all += work_time_h
        return subtask_time_all

    # 根据board_id获取全部全部sprint原始信息
    def sprint_data(self):
        sprint_data = []
        data = self.jira.sprints(self.board_id)
        for i in data:
            sprint_data.append(i.name + "---id=" + str(i.id))
        # br = self.JIRA.sprint
        return sprint_data

    def story(self):
        """
        本迭代总故事数
        :return:
        """
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND status in ("In Progress", "TO DO", "In Test", Developable, Deployed, Suspended, Refused, Deployable, "In Review", '
            '"In Design")AND Sprint={}  ORDER BY created DESC'.format(self.project, self.type, self.sprint),
            maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        self.write_value('本迭代总用户故事数/point点', str(len(jira_data)) + '/' + str(num))
        return {"story": len(jira_data), "point": num}
        # print(BPD_story)
        # print("商业化产品19-30迭代总故事数:",len(BPD_story))

    def plan_story_num(self):
        """
        sprint计划中故事数
        :return:
        """
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {} AND created <= {}  ORDER BY created DESC'.format(
                self.project, self.type, self.sprint, self.create_time), maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        self.write_value('计划需求故事数/point点', str(len(jira_data)) + '/' + str(num))
        return {"计划中故事数:{},point数{}".format(len(jira_data), num)}

    def temporary_story_num(self):
        """
        临时需求故事数
        :return:
        """
        num = 0
        # print(self.create_time,self.end_time)  #end_time
        sprint_start = self.create_time
        PD_story_plan = self.jira.search_issues(
            'project = {} AND  issuetype = {} AND Sprint = {} AND created > {}  ORDER BY created DESC'.format(
                self.project, self.type, self.sprint, sprint_start), maxResults=-1)
        for i in PD_story_plan:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        self.write_value('临时需求故事数/point点', str(len(PD_story_plan)) + '/' + str(num))
        return {"临时需求故事数:{},point数{}".format(len(PD_story_plan), num)}

    def deployednum(self):
        """
        上线完成故事数
        :return:
        """
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND status = Deployed AND Sprint = {} ORDER BY created DESC'.format(
                self.project, self.type, self.sprint), maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        self.write_value('上线完成故事数/point点', str(len(jira_data)) + '/' + str(num))
        return {"deployednum": len(jira_data), "point": num}

    def story_deliver_proportion(self):
        """
        故事交付率
        :return:
        """
        story_num = self.story()
        deployed_num = self.deployednum()
        story_deliver_proportion_num = round(deployed_num["deployednum"] / story_num["story"] * 100, 1)
        story_deliver_proportion_point = round(deployed_num["point"] / story_num["point"] * 100, 1)
        self.write_value('故事交付率/point点交付率',
                         str(story_deliver_proportion_num) + '%/' + str(story_deliver_proportion_point) + '%')
        return story_deliver_proportion_num, story_deliver_proportion_point

    def delay_release(self):
        """
        延期发布故事总数
        :return:
        """
        delay_release_num = 0
        point_num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {}  ORDER BY created DESC'.format(self.project, self.type,
                                                                                            self.sprint),
            expand='changelog', maxResults=-1)
        for i in jira_data:
            if i.fields.duedate != None:
                end_ymd = self.Time(i.fields.duedate)
                # end_story_time = i.fields.duedate
                for b in i.changelog.histories:
                    if b.items[0].toString == 'Deployed':
                        release_time_str = self.Time(b.created)
                        # y_m_d = on_test_tim.split(' ')[0]
                        release_time = ctime = time.strptime(release_time_str, "%Y-%m-%d %H:%M:%S")
                        end_time_str = str(end_ymd) + " 23:59:50"
                        end_time = ctime = time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                        release_time_num = time.mktime(release_time)
                        end_time_num = time.mktime(end_time)
                        if int(release_time_num) > int(end_time_num):
                            delay_release_num += 1
                            point_num += int(i.fields.customfield_10106)
                            # print(on_time,ac_time)
                            # if on_test_tim >
        self.write_value('延期发布故事总数/point点', str(delay_release_num) + '/' + str(point_num))
        return delay_release_num, point_num

    def delay_proportion(self):
        """
        延期故事率
        :return:
        """
        delay_release_num, point_num = self.delay_release()
        story_num = self.story()
        # print(delay_release_num,story_num)
        delay_pro = round(float(delay_release_num) / float((story_num["story"])) * 100, 1)
        point_pro = round(float(point_num) / float(story_num["point"]) * 100, 1)
        self.write_value('延期故事率/point点占比', str(delay_pro) + '%/' + str(point_pro) + '%')
        return delay_pro, point_pro

    def on_test_proportion(self):
        """
        准时提测故事占比 story
        :return:
        """
        on_test_num, point_num = self.accurate_test()
        story_num = self.story()
        story_point = story_num["point"]
        accurate_test_pro = round(float(on_test_num) / float((story_num["story"])) * 100, 1)
        point_pro = round(float(point_num) / float(story_point) * 100, 1)
        self.write_value('准时提测故事占比/point点占比', str(accurate_test_pro) + '%/' + str(point_pro) + '%')
        return accurate_test_pro, point_pro

    def accurate_test(self):
        """
        准时提测故事数 story
        :return:
        """
        on_test_num = 0
        point_num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {}  ORDER BY created DESC'.format(self.project, self.type,
                                                                                            self.sprint),
            expand='changelog', maxResults=-1)
        for i in jira_data:
            actual_test_time = self.Time(i.fields.customfield_10400)
            # end_story_time = i.fields.duedate
            for b in i.changelog.histories:
                if b.items[0].toString == 'In Test':
                    on_test_tim = self.Time(b.created)
                    # y_m_d = on_test_tim.split(' ')[0]
                    ymd_on_test = ctime = time.strptime(on_test_tim, "%Y-%m-%d %H:%M:%S")
                    if actual_test_time != 0:
                        actualtime = str(actual_test_time) + " 23:59:50"
                        ymd_actualtime = ctime = time.strptime(actualtime, "%Y-%m-%d %H:%M:%S")
                        on_time = time.mktime(ymd_on_test)
                        ac_time = time.mktime(ymd_actualtime)
                        if int(on_time) <= int(ac_time):
                            on_test_num += 1
                            point_num += int(i.fields.customfield_10106)
                            # print(on_time,ac_time)
                            # if on_test_tim >
                    else:
                        print(i.key + "没有预期提测时间")
        self.write_value('准时提测故事数 /point点', str(on_test_num) + '/' + str(point_num))
        return on_test_num, point_num

    def sprint_point(self):
        """
        迭代point数
        :return:
        """
        _subtask_time_all = 0
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {}  ORDER BY created DESC'.format(self.project, self.type,
                                                                                            self.sprint),
            expand='changelog', maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return num

    def test_subtask(self):
        """
        测试总工时 子任务
        :return:
        """
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype in (subTaskIssueTypes(), Sub-Task) AND Sprint = {} AND '
            'assignee in (membersOf(研发部_供应链研发), membersOf(研发部_产品研发)) ORDER BY created ASC'
                .format(self.project, self.sprint), expand='changelog', maxResults=-1)
        subtask_time_all = 0
        test_task_list = [i for i in jira_data if str(i.fields.assignee) in QA]
        for project in test_task_list:
            for log in project.changelog.histories:
                for log_info in log.items:
                    if "In Progress" in str(log_info.toString):
                        stardata = self.Time(log.created)
                        enddata = self.Time(project.fields.resolutiondate)
                        subtask_time_all += self.working_day_calculation(stardata, enddata)
                    else:
                        pass
        self.write_value('测试总工时 子任务', str(subtask_time_all))
        return subtask_time_all  # subtask_time_h  # {"已完成子任务数：%s,子任务总时长%s"%(_finish_num,subtask_time_h)}

    def sub_task(self):
        """
        研发总工时 子任务
        :return:
        """
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype in (subTaskIssueTypes(), Sub-Task) AND Sprint = {} AND '
            'assignee in (membersOf(研发部_供应链研发), membersOf(研发部_产品研发)) ORDER BY created ASC'
                .format(self.project, self.sprint), expand='changelog', maxResults=-1)
        # print("用户产品19-30迭代研发子任务:",len(UPD_dev_subTaskIssue))   #'直播间回放页测试评审'
        subtask_time_all = 0
        test_task_list = [i for i in jira_data if str(i.fields.assignee) not in QA]
        for project in test_task_list:
            for log in project.changelog.histories:
                for log_info in log.items:
                    if "In Progress" in str(log_info.toString):
                        stardata = self.Time(log.created)
                        enddata = self.Time(project.fields.resolutiondate)
                        subtask_time_all += self.working_day_calculation(stardata, enddata)
                    else:
                        pass
        # subtask_time_h1 = round(_subtask_time_all / 3600, 2)
        self.write_value('开发总工时 子任务', str(subtask_time_all))
        return subtask_time_all  # subtask_time_h  # {"已完成子任务数：%s,子任务总时长%s"%(_finish_num,subtask_time_h)}

    def dev_test_proportion(self):
        """
        测试开发工时比例/缺陷密度
        :return:
        """
        dev = self.sub_task()
        test = self.test_subtask()
        if (dev or test) == 0:
            self.write_value('测试开发工时占比 子任务', '0%')
        else:
            proportiontime = round((dev / test) * 100, 2)
            self.write_value('测试开发工时占比 子任务', str(proportiontime) + '%')

        # 缺陷密度(缺陷数量/开发总工时)
        bugdensity = 0
        bugdensity1 = len(self.story_bug())
        if bugdensity1 or dev != 0:
            bugdensity = round(dev / bugdensity1, 2)
        self.write_value('缺陷密度', bugdensity)
        # print('8.缺陷密度为：' + str(bugdensity))

    def ongoing_story(self):
        """
        story进行中
        :return:
        """
        num = 0
        # print(self.create_time,self.end_time)  #end_time
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {} AND status in ("In Progress", "In Test", Developable, Deployable, "In Review", "In Design")'.format(
                self.project, self.type, self.sprint), expand='changelog', maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        self.write_value('进行中的故事数/point点', str(len(jira_data)) + '/' + str(num))
        return {"进行中的故事数:{},point数{}".format(len(jira_data), num)}

    def intest_num(self):
        """
        已提侧故事数
        :return:
        """
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {} AND status in ("In Test", Deployed, Deployable)'.format(
                self.project, self.type, self.sprint), expand='changelog', maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        self.write_value('已提测的故事数/point点', str(len(jira_data)) + '/' + str(num))
        return {"已提侧故事数:{},point数{}".format(len(jira_data), num)}

    def story_bug(self):
        """
        故事关联bug
        :return:
        """
        buglist = []
        story = self.jira.search_issues(
            'project = {} AND issuetype = Story AND Sprint = {}'.format(self.project, self.sprint),
            maxResults=-1, expand='changelog')
        for s in story:
            links = s.fields.issuelinks
            for i in links:
                if hasattr(i, 'inwardIssue'):
                    if i.inwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.inwardIssue.key)
                elif hasattr(i, 'outwardIssue'):
                    if i.outwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.outwardIssue.key)
                else:
                    print('不是缺陷类型')
        print(buglist)
        return buglist

    def bug_category(self):
        """
        bug相关数据统计
        :return:
        """
        #
        # 通过bug关联的story统计bug类型
        counts = {}
        bugtypelist1 = []
        bug_list = self.story_bug()
        for bug_id in bug_list:
            bug = self.jira.search_issues(
                'project = {} AND issuetype = bug AND id = "{}" '.format(self.project, bug_id),
                maxResults=-1, expand='changelog')
            for issue in bug:
                bugtypelist1.append(issue.fields.customfield_10401.value)
                bugtypelist1.append(issue.fields.priority.name)
                bugtypelist1.append(issue.fields.status.name)
                counts = defaultdict(int)
                for kw in bugtypelist1:
                    counts[kw] += 1
        averagetime = 0
        average1 = len(bug_list)
        average2 = self.totaltime()
        if average1 or average2 != 0:
            averagetime = round(average2 / average1, 2)

        print('1.缺陷总数量：' + str(len(bug_list)))
        print('3.缺陷分类与数量：')
        print('前端：' + str(counts['前端']))
        print('服务端：' + str(counts['服务端']))
        print('Android端：' + str(counts['android端']))
        print('iOS端：' + str(counts['iOS端']))
        print('设计：' + str(counts['设计']))
        print('业务：' + str(counts['业务']))
        print('产品：' + str(counts['产品']))
        print('2.缺陷级别与数量：')
        print('Highest：' + str(counts['Highest']))
        print('High：' + str(counts['High']))
        print('Medium：' + str(counts['Medium']))
        print('Low：' + str(counts['Low']))
        print('Lowest：' + str(counts['Lowest']))
        print('未关闭bug数量：' + str(len(bug_list) - counts['已关闭']))
        print('7.缺陷平均解决时长为：' + str(averagetime))

        self.write_value('前端', counts['前端'])
        self.write_value('服务端', counts['服务端'])
        self.write_value('android端', counts['android端'])
        self.write_value('iOS端', counts['iOS端'])
        self.write_value('设计', counts['设计'])
        self.write_value('业务', counts['业务'])
        self.write_value('产品', counts['产品'])
        self.write_value('Highest(P0)', counts['Highest'])
        self.write_value('High(P1)', counts['High'])
        self.write_value('Medium(P2)', counts['Medium'])
        self.write_value('Low(P3)', counts['Low'])
        self.write_value('Lowest(P4)', counts['Lowest'])
        self.write_value('未关闭bug数量', len(bug_list) - counts['已关闭'])
        self.write_value('缺陷平均解决时长', averagetime)
        self.write_value('缺陷总数量', len(bug_list))

    def bug_defect(self):
        """
        线上bug数，由于线上故障不一定有story，但是一定有sprint，所以按照sprint统计
        :return:
        """
        UPD_Defect = self.jira.search_issues(
            'project = ' + str(self.project) + ' AND issuetype = Defect AND Sprint = ' + str(self.sprint),
            maxResults=100000)
        self.write_value('线上故障数', len(UPD_Defect))
        print('5.线上故障数：' + str(len(UPD_Defect)))

    def totaltime(self):
        """
        缺陷总解决时长
        :return:
        """
        sub_time_all = 0
        bug_id = ','.join(self.story_bug())
        # 按list获取bug相信信息
        bug = self.jira.search_issues(
            'project = {} AND issuetype = Bug AND id IN ({})'.format(self.project, bug_id),
            maxResults=-1, expand='changelog')
        for issue in bug:
            # 创建日期-转成日期格式
            createtime = issue.fields.created
            # 替换成日期格式
            finalcreatetime = createtime.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
            createtimeArray = datetime.datetime.strptime(finalcreatetime, "%Y-%m-%d %H:%M:%S")
            print('创建时间：' + str(createtimeArray))
            historieslistlen = len(issue.changelog.histories)
            resolvedtimeArray = 0
            for j in range(historieslistlen):
                historieslist = issue.changelog.histories[j]
                if historieslist.items[0].toString == 'Resolved':
                    Resolvedtime = historieslist.created
                    finalresolvedtime = \
                        Resolvedtime.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
                    resolvedtimeArray = datetime.datetime.strptime(finalresolvedtime, "%Y-%m-%d %H:%M:%S")
                    print(sub_time_all)
            sub_time_all += self.working_day_calculation(createtimeArray, resolvedtimeArray)
        self.write_value('缺陷总解决时长', int(sub_time_all))
        print('6.缺陷总解决时长-------' + str(sub_time_all) + '小时')
        return sub_time_all


if __name__ == '__main__':
    # Linedic = {'UPD': 219, 'BPD': 220, 'INSC': 221}
    Linedic = {'UPD': 219, 'BPD': 220, 'INSC': 221}
    for p in Linedic.keys():
        s = Linedic.get(p)
        jira_operation = JiraOperation(board_id=None, project=p, type="Story", sprint=s, create_time="2021-05-06",
                                       end_time="2021-05-22", col_name='5.06-5.21')
        # 缺陷分类与数量
        jira_operation.bug_category()
        # 线上bug数
        jira_operation.bug_defect()
        # # # sprint计划中故事数
        jira_operation.plan_story_num()
        # # #临时需求故事数
        jira_operation.temporary_story_num()
        # # # 故事交付率
        jira_operation.story_deliver_proportion()
        # # # 延期故事率
        jira_operation.delay_proportion()
        # # # 准时提测故事占比 story
        jira_operation.on_test_proportion()
        # # # 迭代point数
        jira_operation.sprint_point()
        # 测试开发工时比例/缺陷密度
        jira_operation.dev_test_proportion()
        # story进行中
        jira_operation.ongoing_story()
        # 已提侧故事数
        jira_operation.intest_num()
