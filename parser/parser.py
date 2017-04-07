from github import Github, GithubObject, RateLimitExceededException
import settings
import networkx as nx
import re
import os
import time


class RepoGraph:
    def __init__(self, repo):
        self.repo = repo

    def parse_text(self, speaker, issue_number, text):
        if text is None:
            return
        for referencing_issue in re.findall(r'#\d+', text):
            self.G.add_edge(
                issue_number, referencing_issue,
                referencing=True,
                user=speaker
            )
        for mentioning_user in re.findall(r'@([\w-]+)', text):
            self.G.add_edge(
                speaker, mentioning_user,
                mentioning=True,
                issue_number=issue_number
            )

    def parse_comment(self, issue, comment):
        username, issue_number = comment.user.login, ('#%d' % (issue.number,))
        if username != issue.user.login:
            self.G.add_node(username, _type='user')
            self.G.add_edge(
                username, issue_number,
                commenter=True,
                created_at=comment.created_at.isoformat()
            )
        self.parse_text(username, issue_number, comment.body)
            
    def parse_issue(self, issue):
        username, issue_number = issue.user.login, ('#%d' % (issue.number,))
        print("parsing issues of %s" % (issue_number,))
        self.G.add_node(username, _type='user')
        self.G.add_node(issue_number, _type='issue',
                            is_pull_request=issue.pull_request is not None)
        self.G.add_edge(
            username, issue_number,
            issuer=True,
            created_at=issue.created_at.isoformat()
        )
        self.parse_text(username, issue_number, issue.body)
        for comment in issue.get_comments():
            self.parse_comment(issue, comment)

    def filter_invalid_nodes(self):
        invalid_nodes = [
            label
            for label
            in self.G.node
            if self.G.node[label].get('_type') is None
        ]
        for node in invalid_nodes:
            self.G.remove_node(node)
        
    def make_graph(self) -> nx.DiGraph:
        print('Making graph start...')
        self.G = nx.DiGraph()
        issues_iterator = repo.get_issues(
            state='all', sort='created', direction='asc'
        )
        for issue in issues_iterator:
            try:
                self.parse_issue(issue)
            except RateLimitExceededException:
                print(
                    'RateLimitExceededException raised!\n'
                    'processor waits for 1 hour and retries...'
                )
                time.sleep(4000)
                self.parse_issue(issue)
            if issue.number % 1000 == 0:
                print('%d issues parsed' % (issue.number,))

        self.filter_invalid_nodes()
        
        return self.G


def write_graph(G):
    output_path = (
        settings.DIST_PATH + '/' +
        settings.REPOSITORY.replace('/','_') + '.gexf'
    )
    if not os.path.exists(settings.DIST_PATH):
        os.makedirs(settings.DIST_PATH)
    nx.write_gexf(G, output_path)
    
    
if __name__ == "__main__":
    github = Github(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET
    )
    repo = github.get_repo(settings.REPOSITORY)
    G = RepoGraph(repo).make_graph()
    write_graph(G)
