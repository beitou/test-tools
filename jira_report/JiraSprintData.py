import time
import pandas as pd
import numpy as np
from jira import JIRA
import datetime
from dateutil.parser import parse
#连接创建jira对象
QA = [
    "刘丽雨", "陈晨","陈帅（技术）","耿金龙","候丽娟","李丽莉","刘苹苹", "田孝庆",
    "宿宇", "耿金龙", "万莞羚", "刘苹苹", "闫茜","卫鑫",
    "张力达",
]
class Jira:

    def __init__(self,board_id=None,project=None,type=None,sprint=None,create_time=None,end_time=None):
        self.jira = JIRA(auth=("chenshuai2", "Chenshua1&"), options={'server': 'http://jira.xiaobangtouzi.com'})
        self.board_id = board_id
        self.project = project
        self.type = type
        self.sprint = sprint
        self.create_time = create_time
        self.end_time = end_time


    def Time(self,data):
        #创建时间：2021-04-26T15:49:57.000+0800,1
        try:
            date = data.replace('T', ' ').replace('Z', '').replace('.000', '').split('+')[0]
            return date
            #创建时间2021-04-28 11:24:29
        except Exception as e:

            return 0

    def Star_Time_h(self,data):
        day_work_time = parse("20:0:0")
        stardata_day = str(data).split(' ')[0]
        stardata_time = parse(str(data).split(' ')[1])

        if stardata_time > day_work_time:
            stardata_h_int = 0
            return stardata_day, stardata_h_int
        else:
            stardata_h = str(day_work_time - stardata_time)
            stardata_h_int = int(stardata_h.split(":")[0]) - 2
            stardata_m = int(stardata_h.split(":")[1])
            if stardata_m >= 30 :
                stardata_h_int += 1
            return stardata_day,stardata_h_int

    def End_Time_h(self,data):
        day_work_time = parse("10:0:0")
        time_type_h = parse(data)
        h = int(data.split(":")[0])
        if h > 14:
            endtime_h = str((time_type_h - day_work_time))
            time = int(endtime_h.split(":")[0]) -2
            return time
        else:
            endtime_h = str((time_type_h - day_work_time))
            time = int(endtime_h.split(":")[0])
            #print("对比:",time)
            return time
# 根据board_id获取全部全部sprint原始信息
    def sprint_data(self):
        sprint_data = []
        data = self.jira.sprints(self.board_id)
        for i in data:
            sprint_data.append(i.name+"---id="+str(i.id))
        #br = self.JIRA.sprint
        return sprint_data

# 本迭代总故事数
    def story(self):
        num = 0
        jira_data = self.jira.search_issues('project = {} AND issuetype = {} AND status in ("In Progress", "TO DO", "In Test", Developable, Deployed, Suspended, Refused, Deployable, "In Review", '
                                            '"In Design")AND Sprint={}  ORDER BY created DESC'.format(self.project,self.type,self.sprint),maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return {"story":len(jira_data),"point":num}
        # print(BPD_story)
        # print("商业化产品19-30迭代总故事数:",len(BPD_story))

# sprint计划中故事数
    def plan_story_num(self):
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {} AND created <= {}  ORDER BY created DESC'.format(self.project,self.type,self.sprint,self.create_time),maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return {"计划中故事数:{},point数{}".format(len(jira_data),num)}

# 临时需求故事数
    def temporary_story_num(self):
        num = 0
        #print(self.create_time,self.end_time)  #end_time
        sprint_start = self.create_time
        PD_story_plan = self.jira.search_issues(
            'project = {} AND  issuetype = {} AND Sprint = {} AND created > {}  ORDER BY created DESC'.format(self.project,self.type,self.sprint,sprint_start),maxResults=-1)
        for i in PD_story_plan:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return {"临时需求故事数:{},point数{}".format(len(PD_story_plan),num)}

# 上线完成故事数
    def deployednum(self):
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND status = Deployed AND Sprint = {} ORDER BY created DESC'.format(self.project,self.type,self.sprint),maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return {"deployednum": len(jira_data),"point":num}

# 故事交付率
    def story_deliver_proportion(self):
        story_num = self.story()
        deployed_num = self.deployednum()
        story_deliver_proportion_num = int(deployed_num["deployednum"]) / int(story_num["story"])
        return story_deliver_proportion_num

# 延期发布故事总数
    def delay_release(self):
        delay_release_num = 0
        point_num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {}  ORDER BY created DESC'.format(self.project,self.type,self.sprint), expand='changelog',maxResults=-1)
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
        return delay_release_num,point_num

# 延期故事率
    def delay_proportion(self):
        delay_release_num,point_num = self.delay_release()
        story_num = self.story()
        # print(delay_release_num,story_num)
        delay_pro = delay_release_num / int(story_num["story"])
        point_pro = point_num / story_num["point"]
        return delay_pro,point_pro

# 准时提测故事占比 story
    def on_test_proportion(self):
        on_test_num,point_num = self.accurate_test()
        story_num = self.story()
        story_point = story_num["point"]
        accurate_test_pro = on_test_num / int(story_num["story"])
        point_pro = point_num / story_point
        return accurate_test_pro,point_pro

# 准时提测故事数 story
    def accurate_test(self):
        on_test_num = 0
        point_num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {}  ORDER BY created DESC'.format(self.project,self.type,self.sprint), expand='changelog',maxResults=-1)
        for i in jira_data:
            actual_test_time = self.Time(i.fields.customfield_10400)
            #end_story_time = i.fields.duedate
            for b in i.changelog.histories:
                if b.items[0].toString == 'In Test':
                    on_test_tim = self.Time(b.created)
                    #y_m_d = on_test_tim.split(' ')[0]
                    ymd_on_test = ctime = time.strptime(on_test_tim, "%Y-%m-%d %H:%M:%S")
                    if actual_test_time != 0:
                        actualtime=str(actual_test_time) + " 23:59:50"
                        ymd_actualtime = ctime = time.strptime(actualtime, "%Y-%m-%d %H:%M:%S")
                        on_time = time.mktime(ymd_on_test)
                        ac_time = time.mktime(ymd_actualtime)
                        if int(on_time) <= int(ac_time):
                            on_test_num += 1
                            point_num += int(i.fields.customfield_10106)
                                #print(on_time,ac_time)
                                #if on_test_tim >
        return on_test_num,point_num

# 迭代point数
    def sprint_point(self):
        _subtask_time_all = 0
        num = 0
        jira_data= self.jira.search_issues('project = {} AND issuetype = {} AND Sprint = {}  ORDER BY created DESC'.format(self.project,self.type,self.sprint),expand='changelog',maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return num

# 测试总工时 子任务
    def test_subtask(self):
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype in (subTaskIssueTypes(), Sub-Task) AND Sprint = {} AND '
            'assignee in (membersOf(研发部_供应链研发), membersOf(研发部_产品研发)) ORDER BY created ASC'
                .format(self.project, self.sprint), expand='changelog', maxResults=-1)
        # print("用户产品19-30迭代研发子任务:",len(UPD_dev_subTaskIssue))   #'直播间回放页测试评审'
        _subtask_time_all = 0
        test_task_list = [i for i in jira_data if str(i.fields.assignee)  in QA]
        for project in test_task_list:
            for log in project.changelog.histories:
                for log_info in log.items:
                    if "In Progress" in str(log_info.toString):
                        stardata = self.Time(log.created)
                        t1, stardata_h = self.Star_Time_h(stardata)
                        enddata = self.Time(project.fields.resolutiondate)
                        if enddata == 0:
                            enddata_now = str(datetime.datetime.now())
                            enddata = enddata_now.split(".")[0]
                            end_day = enddata.split(" ")[0]
                            end_time = enddata.split(" ")[1]
                            t2 = pd.to_datetime(end_day, format="%Y/%m/%d").date()
                        else:
                            enddata_day = enddata.split(" ")[0]
                            end_time = enddata.split(" ")[1]
                            t2 = pd.to_datetime(enddata_day, format="%Y/%m/%d").date()
                        days = np.busday_count(t1, t2)
                        if days == 0:
                            t1 = datetime.datetime.strptime(stardata, "%Y-%m-%d %H:%M:%S")
                            t2 = datetime.datetime.strptime(str(enddata), "%Y-%m-%d %H:%M:%S")
                            total_interval_time = (t2 - t1).total_seconds() / 3600
                            _subtask_time_all += int(total_interval_time)
                        elif days != 0:
                            _subtask_time_all += ((days - 1) * 8)
                            end_data_h = self.End_Time_h(end_time)
                            work_time_h = int(stardata_h) + end_data_h
                            _subtask_time_all += (days * 8) + work_time_h
                    else:
                        pass
        # subtask_time_h1 = round(_subtask_time_all / 3600, 2)
        return _subtask_time_all  # subtask_time_h  # {"已完成子任务数：%s,子任务总时长%s"%(_finish_num,subtask_time_h)}


# 研发 子任务
    def SubTask(self):
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype in (subTaskIssueTypes(), Sub-Task) AND Sprint = {} AND '
            'assignee in (membersOf(研发部_供应链研发), membersOf(研发部_产品研发)) ORDER BY created ASC'
            .format(self.project, self.sprint), expand='changelog',maxResults=-1)
        # print("用户产品19-30迭代研发子任务:",len(UPD_dev_subTaskIssue))   #'直播间回放页测试评审'
        _subtask_time_all = 0
        test_task_list = [i for i in jira_data if str(i.fields.assignee) not in QA]
        for project in test_task_list:
            for log in project.changelog.histories:
                for log_info in log.items:
                    if "In Progress" in str(log_info.toString):
                        stardata = self.Time(log.created)
                        t1,stardata_h = self.Star_Time_h(stardata)
                        enddata = self.Time(project.fields.resolutiondate)
                        if enddata == 0:
                            enddata_now = str(datetime.datetime.now())
                            enddata = enddata_now.split(".")[0]
                            end_day = enddata.split(" ")[0]
                            end_time = enddata.split(" ")[1]
                            t2 = pd.to_datetime(end_day, format="%Y/%m/%d").date()
                        else:
                            enddata_day = enddata.split(" ")[0]
                            end_time = enddata.split(" ")[1]
                            t2 = pd.to_datetime(enddata_day, format="%Y/%m/%d").date()
                        days = np.busday_count(t1, t2)
                        if days == 0:
                            t1 = datetime.datetime.strptime(stardata, "%Y-%m-%d %H:%M:%S")
                            t2 = datetime.datetime.strptime(str(enddata), "%Y-%m-%d %H:%M:%S")
                            total_interval_time = (t2 - t1).total_seconds() / 3600
                            _subtask_time_all += int(total_interval_time)
                        elif days != 0:
                            _subtask_time_all += ((days -1) * 8)
                            end_data_h = self.End_Time_h(end_time)
                            work_time_h = int(stardata_h) + end_data_h
                            _subtask_time_all += work_time_h
                    else:
                        pass
        #subtask_time_h1 = round(_subtask_time_all / 3600, 2)
        return _subtask_time_all  # subtask_time_h  # {"已完成子任务数：%s,子任务总时长%s"%(_finish_num,subtask_time_h)}
        #return subtask_time_h1 #subtask_time_h  # {"已完成子任务数：%s,子任务总时长%s"%(_finish_num,subtask_time_h)}
                    #           .format(i.key,total_interval_time,_finish_num,subtask_time_h))

                    # print("子任务名称{},创建时间：{},报告人：{},经办人：{},预计结束时间{}，子任务当前状态{},子任务开始时间{},未完成数量：{}"
                    #       .format(i.key,taskdata.created,
                    #               taskdata.creator,
                    #               taskdata.assignee,
                    #               taskdata.duedate,
                    #               taskdata.status,
                    #               stardata,_no_finish_num))

# 测试开发工时比例
    def dev_test_proportion(self):
        dev = self.SubTask()
        test = self.test_subtask()
        if (dev or test) == 0:
            return {"测试开发工时比例：%s"%(None)}
        else:
            proportiontime = round(float(test) / float(dev),2)
            return {"测试开发工时比例：%s"%(proportiontime)}




# story进行中
    def ongoing_story(self):
        num = 0
        #print(self.create_time,self.end_time)  #end_time
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {} AND status in ("In Progress", "In Test", Developable, Deployed, Deployable, "In Review", "In Design")'.format(self.project, self.type,self.sprint),expand='changelog', maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return {"进行中的故事数:{},point数{}".format(len(jira_data),num)}


# 已提侧故事数
    def Intest_num(self):
        num = 0
        jira_data = self.jira.search_issues(
            'project = {} AND issuetype = {} AND Sprint = {} AND status in ("In Test", Deployed, Deployable)'.format(
                self.project, self.type, self.sprint), expand='changelog', maxResults=-1)
        for i in jira_data:
            if i.fields.customfield_10106:
                num += int(i.fields.customfield_10106)
        return {"已提侧故事数:{},point数{}".format(len(jira_data),num)}









if __name__ == "__main__":


    #board_id=68  = UPD \BPD  board_id=6 = INSU
    # 获取当前全部sprint原始信息
    #deful = Jira(board_id=68)
    #print(deful.sprint_data())
    # 68 =['0419-0430---id=198', 'UPD 2021 Sprint 0506 - 0521---id=219', 'BPD 2021 Sprint 0506 - 0522---id=220', 'UPD 2021 Sprint 0524 - 0604---id=228']


    # 基于sprint_data方法返回数据替换下方默认值，
     #供应链：'INSC 2021 Sprint 0506 - 0521---id=221'
    #用户 :project="UPD", type="Story",sprint= 219,create_time= "2021-05-06", end_time="2021-05-22"
    # 创建目标查询对象，（时间变量仅用于统计临时需求和迭代需求） project=None,type=None,sprint=None,create_time=None,end_time=None
    # 新增进行中、 已提侧 story
    #aa = Jira(board_id=None,project="INSC", type="Story",sprint= 221,create_time= "2021-05-06", end_time="2021-05-22")
    #aa = Jira(board_id=None, project="UPD", type="Story",sprint=219,create_time="2021-05-24", end_time="2021-06-04")
    aa = Jira(board_id=None, project="BPD", type="Story", sprint=220, create_time="2021-05-06", end_time="2021-05-22")

    # # # 本迭代总故事数
    #print("本迭代总故事数:",aa.story())
    # #
    # # # sprint计划中故事数
    # print("sprint中计划故事数:",aa.plan_story_num())
    # #
    # # #临时需求故事数
    # print("sprint中临时故事数:",aa.temporary_story_num())
    # #
    # # # 上线完成故事数
    #print("上线完成故事数:",aa.deployednum())
    # #
    # # # 故事交付率
    # print("故事交付率",aa.story_deliver_proportion())
    # #
    # # # 延期发布故事总数
    #print("延期发布故事总数:",aa.delay_release())
    # #
    # # # 延期故事率
    #print("延期故事率",aa.delay_proportion())
    # #
    # # # 准时提测故事占比 story
    #print("准时提测故事占比",aa.on_test_proportion())
    # #
    # # # 准时提测故事数 story
    #print("准时提测故事数及point数:",aa.accurate_test())
    # #
    # # # 迭代point数1
    # print("迭代point数",aa.sprint_point())
    #
    # # 测试总工时 子任务
    #print("测试总工时 子任务",aa.test_subtask())
    #
    # # 研发 子任务
    #print("研发 子任务:",aa.SubTask())
    #
    # # 测试开发工时比例
    #print("测试开发工时比例",aa.dev_test_proportion())
    #
    # story 进行中
    print("正在进行中的story数：",aa.ongoing_story())

    # story 已提侧数据
    print("已经提侧的story数：",aa.Intest_num())

    '''
                            print("创建时间：{},报告人：{},经办人：{},预计结束时间{}，子任务当前状态{},子任务开始时间{},子任务完成时间{}\n耗时：{}"
                              .format(taskdata.created,
                                      taskdata.creator,
                                      taskdata.assignee,
                                      taskdata.duedate,
                                      taskdata.status, stardata,
                                      enddata,total_interval_time))
    '''