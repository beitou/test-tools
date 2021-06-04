from jira import JIRA

jira_server = 'http://jira.xiaobangtouzi.com'
jira_username = 'yanqian'  # 用户名
jira_password = 'Vina0830'  # 密码

jira = JIRA(basic_auth=(jira_username, jira_password), options={'server': jira_server})


def get_story():
    api_done = jira.search_issues(
        'project = UPD AND issuetype = bug AND id = "UPD-173"',
        maxResults=100000, expand='changelog')
    for issue in api_done:
        print(issue.key, 'Status: ', issue.fields.status)
    print(len(api_done))


if __name__ == '__main__':
    get_story()
