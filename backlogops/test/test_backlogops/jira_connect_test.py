#! /usr/local/bin/python3
"""Test the connection to Jira."""

from pathlib import Path
from jira import JIRA


def connect_test() -> None:
    """Test the connection to Jira."""
    server = 'https://tom-bjorkholm.atlassian.net'
    email = 'klausuler_linnet0q@icloud.com'
    token_file = Path('~/Documents/jobb/knowit_connectivity/jira_experiment'
                      '/API_token_jira-test.txt').expanduser()
    with open(token_file, 'r', encoding='utf-8') as file:
        token = file.read().strip()
#    print('email:', email)
#    print('token:', token)
    jira = JIRA(server=server, basic_auth=(email, token))

#    print('myself:', jira.myself())
    print('jira projects:', jira.projects())
    print('jira user:', jira.current_user())
    print('jira issues:', jira.search_issues('project = "SCRUM"'))
    for issue in jira.search_issues('project = "SCRUM"'):
        print('Key:', issue.key, '\nSummary:', issue.fields.summary)
        print('Status:', issue.fields.status.name)
        print('Description:', issue.fields.description)
        print('Story Points:', issue.fields.__dict__['customfield_10016'])
#        print(issue.fields.__dict__)
    fields = jira.fields()
    custom_fields = {f["id"]: f["name"] for f in fields
                     if f["id"].startswith("customfield_")}
    print('Custom fields:')
    for the_id, name in custom_fields.items():
        print(f'{the_id}: {name}')
    for version in jira.project_versions('SCRUM'):
        print('Version:', version.name, 'Release Date:', version.releaseDate)


if __name__ == '__main__':
    connect_test()
