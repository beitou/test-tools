# coding=utf-8
import datetime
from collections import defaultdict

import xlrd

from xlutils.copy import copy
import xlsxwriter
from jira import JIRA
import time
from datetime import datetime
import os

#  获取当前工作目录
cur_path = '/Users/vina0830/Documents/appium-test/jira'
# excel路径
file_path = os.path.join(cur_path, 'testFile', 'bugdata.xlsx')
QA = [
    "刘丽雨", "陈晨","陈帅（技术）","耿金龙","候丽娟","李丽莉","刘苹苹", "田孝庆",
    "宿宇", "耿金龙", "万莞羚", "刘苹苹", "闫茜","卫鑫",
    "张力达",
]

class JiraOperation:
    def __init__(self):
        try:
            self.jira = JIRA('http://jira.xiaobangtouzi.com', basic_auth=('yanqian', 'Vina0830'))
        except Exception as e:
            print('获取JIRA数据异常', e)

    def Time(self, data):
        # 创建时间：2021-04-26T15:49:57.000+0800,
        try:
            date = data.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
            return date
            # 创建时间2021-04-28 11:24:29
        except Exception as e:

            return 0

    # 向某个单元格写入数据
    def write_value(self, row, col, value):
        data = xlrd.open_workbook(file_path)
        data_copy = copy(data)  # 复制原文件
        sheet = data_copy.get_sheet(0)  # 取得复制文件的sheet对象
        sheet.col(0).width = 256 * 15 #设置列宽
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 40
        sheet.write(row, col, value)  # 在某个单元格中写入value
        data_copy.save(file_path)  # 保存文件



    def story_bug(self, project, sprint):
        buglist = []
        story = self.jira.search_issues('project = {} AND issuetype = Story AND Sprint = {}'.format(project, sprint),
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

    def bug_Total(self, project, sprint):
        # 缺陷总数量
        # 通过bug关联的story统计bug数量
        buglist = []
        story = self.jira.search_issues('project = {} AND issuetype = Story AND Sprint = {}'.format(project, sprint),
                                        maxResults=-1, expand='changelog')
        for s in story:
            links = s.fields.issuelinks
            for i in links:
                if hasattr(i,'inwardIssue'):
                    if i.inwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.id)
                elif hasattr(i,'outwardIssue'):
                    if i.outwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.id)
                else:
                    print('不是缺陷类型')

        if project == 'UPD':
            self.write_value(13, 3, len(buglist))
        elif project == 'BPD':
            self.write_value(13, 4, len(buglist))
        else:
            self.write_value(13, 5, len(buglist))
        print(str(project) + '-----------------------------')
        print(buglist)
        print('1.缺陷总数量：' + str(len(buglist)))
        return (len(buglist))

    def bug_level(self, project, sprint):
        # 缺陷级别与数量
        # 通过bug关联的story统计bug等级
        buglist = []
        story = self.jira.search_issues('project = {} AND issuetype = Story AND Sprint = {}'.format(project, sprint),
                                        maxResults=-1, expand='changelog')
        for s in story:
            links = s.fields.issuelinks
            for i in links:
                if hasattr(i, 'inwardIssue'):
                    if i.inwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.inwardIssue.fields.priority.name)
                        counts = defaultdict(int)
                        for kw in buglist:
                            counts[kw] += 1
                elif hasattr(i,'outwardIssue'):
                    if i.outwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.outwardIssue.fields.priority.name)
                        counts = defaultdict(int)
                        for kw in buglist:
                            counts[kw] += 1
                else:
                    print('不是缺陷类型')
        if project == 'UPD':
            self.write_value(14, 3, counts['Highest'])
            self.write_value(15, 3, counts['High'])
            self.write_value(16, 3, counts['Medium'])
            self.write_value(17, 3, counts['Low'])
            self.write_value(18, 3, counts['Lowest'])
        elif project == 'BPD':
            self.write_value(14, 4, counts['Highest'])
            self.write_value(15, 4, counts['High'])
            self.write_value(16, 4, counts['Medium'])
            self.write_value(17, 4, counts['Low'])
            self.write_value(18, 4, counts['Lowest'])
        else:
            self.write_value(14, 5, counts['Highest'])
            self.write_value(15, 5, counts['High'])
            self.write_value(16, 5, counts['Medium'])
            self.write_value(17, 5, counts['Low'])
            self.write_value(18, 5, counts['Lowest'])
        print(str(project) + '-----------------------------')
        print('2.缺陷级别与数量：')
        print('Highest：' + str(counts['Highest']))
        print('High：' + str(counts['High']))
        print('Medium：' + str(counts['Medium']))
        print('Low：' + str(counts['Low']))
        print('Lowest：' + str(counts['Lowest']))

    def bug_category(self, project, sprint):
        # 缺陷分类与数量
        # 通过bug关联的story统计bug类型
        bugtypelist1 = []
        for bug_id in self.story_bug(project, sprint):
            bug = self.jira.search_issues('project = {} AND issuetype = bug AND id = "{}" '.format(project, bug_id),
                                          maxResults=-1, expand='changelog')
            for issue in bug:
                bugtypelist1.append(issue.fields.customfield_10401.value)
                counts = defaultdict(int)
                for kw in bugtypelist1:
                    counts[kw] += 1
        print('3.缺陷分类与数量：')
        print('前端：' + str(counts['前端']))
        print('服务端：' + str(counts['服务端']))
        print('Android端：' + str(counts['android端']))
        print('iOS端：' + str(counts['iOS端']))
        print('设计：' + str(counts['设计']))
        print('业务：' + str(counts['业务']))
        print('产品：' + str(counts['产品']))

        if project == 'UPD':
            self.write_value(19, 3, counts['前端'])
            self.write_value(20, 3, counts['服务端'])
            self.write_value(21, 3, counts['android端'])
            self.write_value(22, 3, counts['iOS端'])
            self.write_value(23, 3, counts['设计'])
            self.write_value(24, 3, counts['业务'])
            self.write_value(25, 3, counts['产品'])
        elif project == 'BPD':
            self.write_value(19, 4, counts['前端'])
            self.write_value(20, 4, counts['服务端'])
            self.write_value(21, 4, counts['android端'])
            self.write_value(22, 4, counts['iOS端'])
            self.write_value(23, 4, counts['设计'])
            self.write_value(24, 4, counts['业务'])
            self.write_value(25, 4, counts['产品'])
        else:
            self.write_value(19, 5, counts['前端'])
            self.write_value(20, 5, counts['服务端'])
            self.write_value(21, 5, counts['android端'])
            self.write_value(22, 5, counts['iOS端'])
            self.write_value(23, 5, counts['设计'])
            self.write_value(24, 5, counts['业务'])
            self.write_value(25, 5, counts['产品'])

    def bug_notclosed(self, project, sprint):
        # 未关闭bug数量
        buglist = []
        buglist1 = []
        story = self.jira.search_issues('project = {} AND issuetype = Story AND Sprint = {}'.format(project, sprint),
                                        maxResults=-1, expand='changelog')
        for s in story:
            links = s.fields.issuelinks
            for i in links:
                if hasattr(i, 'inwardIssue'):
                    if i.inwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.id)
                        buglist1.append(i.inwardIssue.fields.status.name)
                        counts = defaultdict(int)
                        for kw in buglist1:
                            counts[kw] += 1
                elif hasattr(i, 'outwardIssue'):
                    if i.outwardIssue.fields.issuetype.description == '缺陷':
                        buglist.append(i.id)
                        buglist1.append(i.outwardIssue.fields.status.name)
                        counts = defaultdict(int)
                        for kw in buglist1:
                            counts[kw] += 1
                else:
                    print('不是缺陷类型')
        if project == 'UPD':
            self.write_value(29, 3, len(buglist)-counts['已关闭'])
        elif project == 'BPD':
            self.write_value(29, 4, len(buglist)-counts['已关闭'])
        else:
            self.write_value(29, 5, len(buglist)-counts['已关闭'])
        print(str(project) + '-----------------------------')
        print('4.未关闭bug数量：' + str(len(buglist)-counts['已关闭']))

    def bug_defect(self, project, sprint):
        # 线上故障数，由于线上故障不一定有story，但是一定有sprint，所以按照sprint统计
        UPD_Defect = self.jira.search_issues(
            'project = ' + str(project) + ' AND issuetype = Defect AND Sprint = ' + str(sprint), maxResults=100000)
        if project == 'UPD':
            self.write_value(30, 3, len(UPD_Defect))
        elif project == 'BPD':
            self.write_value(30, 4, len(UPD_Defect))
        else:
            self.write_value(30, 5, len(UPD_Defect))
        print('5.线上故障数：' + str(len(UPD_Defect)))

    def totaltime(self, project, sprint):
        for bug_id in self.story_bug(project, sprint):
            bug = self.jira.search_issues('project = {} AND issuetype = bug AND id = "{}" '.format(project, bug_id),
                                          maxResults=-1, expand='changelog')
            for i in bug:
                timelist = []
                issue = self.jira.issue(i)
                # 创建日期-转成日期格式
                createtime = issue.fields.created
                # 替换成日期格式
                finalcreatetime = createtime.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
                createtimeArray = datetime.strptime(finalcreatetime, "%Y-%m-%d %H:%M:%S")
                print('创建时间：' + str(createtimeArray))
                historieslistlen = len(issue.changelog.histories)
                for j in range(historieslistlen):
                    historieslist = issue.changelog.histories[j]
                    if historieslist.items[0].toString == 'Resolved':
                        Resolvedtime = historieslist.created
                        finalresolvedtime = \
                            Resolvedtime.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
                        resolvedtimeArray = datetime.strptime(finalresolvedtime, "%Y-%m-%d %H:%M:%S")
                        print('解决时间：' + str(resolvedtimeArray))
                        # 计算时间差
                        daytime = (resolvedtimeArray - createtimeArray).days
                        sec = (resolvedtimeArray - createtimeArray).seconds
                        hours = round(sec / 3600, 2)
                        min = round(sec / 60, 2)
                        # print('解决时长为：'+str(hours)+'小时')
                        print('解决时长为：' + str(min) + '分钟')
                        timelist.append(min)
                        print(timelist)
                        if project == 'UPD':
                            self.write_value(15, 3, round(sum(timelist), 2))
                        elif project == 'BPD':
                            self.write_value(15, 4, round(sum(timelist), 2))
                        else:
                            self.write_value(15, 5, round(sum(timelist), 2))
                    else:
                        Resolvedtime = createtime
                        finalresolvedtime = \
                            Resolvedtime.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
                        resolvedtimeArray = datetime.strptime(finalresolvedtime, "%Y-%m-%d %H:%M:%S")
                        print('解决时间：' + str(resolvedtimeArray))
                        min = 0
                        print('解决时长为：' + str(min) + '分钟')
                        if project == 'UPD':
                            self.write_value(26, 3, round(sum(timelist), 2))
                        elif project == 'BPD':
                            self.write_value(26, 4, round(sum(timelist), 2))
                        else:
                            self.write_value(26, 5, round(sum(timelist), 2))
                print('6.缺陷总解决时长-------' + str(round(sum(timelist), 2)) + '分钟')
                return round(sum(timelist), 2)

    def averagetime(self, project, sprint):
        # 缺陷平均解决时长(缺陷总数量/缺陷总解决时长)
        average1 = self.bug_Total(project, sprint)
        average2 = self.totaltime(project, sprint)
        if average1 or average2 == '0':
            averagetime = 0
        else:
            averagetime = round(average1 / average2, 2)
        if project == 'UPD':
            self.write_value(27, 3, averagetime)
        elif project == 'BPD':
            self.write_value(27, 4, averagetime)
        else:
            self.write_value(27, 5, averagetime)
        print('7.缺陷平均解决时长为：' + str(averagetime))

    # 开发总时间
    def SubTask(self,project,sprint):
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype in (subTaskIssueTypes(), Sub-Task) AND Sprint = {} AND '
            'assignee in (membersOf(研发部_供应链研发), membersOf(研发部_产品研发)) ORDER BY created DESC'
                .format(project, sprint), expand='changelog')
        # print("用户产品19-30迭代研发子任务:",len(UPD_dev_subTaskIssue))   #'直播间回放页测试评审'
        _subtask_time_all = 0
        test_task_list = [i for i in jira_data if str(i.fields.creator) not in QA]
        for project in test_task_list:
            for log in project.changelog.histories:
                for log_info in log.items:
                    if "In Progress" in str(log_info.toString):
                        stardata = self.Time(log.created)
                        enddata = self.Time(project.fields.resolutiondate)
                        t1 = datetime.strptime(stardata, "%Y-%m-%d %H:%M:%S")
                        if enddata == 0:
                            t2 = datetime.now()
                        else:
                            t2 = datetime.strptime(str(enddata), "%Y-%m-%d %H:%M:%S")
                        total_interval_time = (t2 - t1).total_seconds()
                        _subtask_time_all += total_interval_time
                    else:
                        pass
        subtask_time_h1 = round(_subtask_time_all / 3600, 2)
        print('开发总工时为：' + str(subtask_time_h1) + '小时')
        return subtask_time_h1


    def density(self,project,sprint):
        # 缺陷密度(缺陷数量/开发总工时)
        bugdensity1 = self.bug_Total(project,sprint)
        bugdensity2 = self.SubTask(project,sprint)
        if bugdensity1 or bugdensity2 == '0':
            bugdensity = 0
        else:
            bugdensity = round(bugdensity1 / bugdensity2, 2)
        if project == 'UPD':
            self.write_value(28, 3, bugdensity)
        elif project == 'BPD':
            self.write_value(28, 4, bugdensity)
        else:
            self.write_value(28, 5, bugdensity)
        print('8.缺陷密度为：' + str(bugdensity))


if __name__ == '__main__':
    jira = JiraOperation()
    # sprint = '221'
    # project = 'INSC'
    # jira.averagetime(project, sprint)
    # jira.bug_level(project, sprint)
    # jira.bug_category(project, sprint)
    # jira.bug_notclosed(project, sprint)
    # jira.bug_defect(project, sprint)
    # jira.density(project,sprint)

    Linedic = {'UPD': 219, 'BPD': 220, 'INSC': 221}
    for p in Linedic:
        project = p
        sprint = Linedic[project]
        jira.averagetime(project, sprint)
        jira.bug_level(project, sprint)
        jira.bug_category(project, sprint)
        jira.bug_notclosed(project, sprint)
        jira.bug_defect(project, sprint)
        jira.density(project,sprint)
