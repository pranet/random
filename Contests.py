import requests
import json
import decimal
from collections import defaultdict
import random


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class Problem(object):

    def __init__(self, contest_id: int, index: str):
        self.key = (contest_id, index)
        self.weight = 0


class Contest(object):

    def __init__(self, questions):
        self.contest_id = None
        self.questions = questions
        self.scores = []


class ContestMaker(object):
    """Responsible for creating a new contest and saving it to db"""

    def __init__(self, contest_table):
        self.contest_table = contest_table

    def get_problems(self):
        r = requests.get("http://codeforces.com/api/problemset.problems")
        problems = r.json()['result']['problems']
        ret = []
        for problem in problems:
            ret.append(Problem(problem['contestId'], problem['index']))
        return ret

    def get_all_contests(self):
        ret_raw = self.contest_table.scan()["Items"]
        ret_str = json.dumps(ret_raw, cls=DecimalEncoder)
        ret_json = json.loads(ret_str)
        return ret_json

    def get_problem_usage_history(self):
        """Return a dict whose key identifies the problem, and value is a list of all contests it was a part of """
        contests = self.get_all_contests()
        ret = defaultdict(list)
        for contest in contests:
            contest_id = contest['contestId']
            if contest_id == 0:
                continue
            questions = contest['questions']
            for question in questions:
                ret[tuple(question)].append(contest_id)
        return ret

    def assign_weights(self, problems, problem_usage_history):
        pass

    def save_to_table(self, contest: Contest):
        next_id = int(self.contest_table.get_item(Key={
            "contestId": 0
        })["Item"]["nextId"])
        contest.contest_id = next_id

        self.contest_table.put_item(Item={
            "contestId": 0,
            "nextId": next_id + 1
        })

        self.contest_table.put_item(Item={
            "contestId": contest.contest_id,
            "questions": contest.questions,
            "scores": contest.scores
        })

    def generate_questions(self, problems):
        chosen = random.sample(problems, 10)
        ret = []
        for problem in chosen:
            ret.append(list(problem.key))
        return ret

    def create_contest(self):
        """Creates a new contest based on old ones and saved it to db"""
        problem_usage_history = self.get_problem_usage_history()
        problems = self.get_problems()
        self.assign_weights(problems, problem_usage_history)
        questions = self.generate_questions(problems)
        contest = Contest(questions)
        self.save_to_table(contest)
        return contest