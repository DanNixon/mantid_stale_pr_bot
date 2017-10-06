from random import randrange
from string import Template


def get_admins(pr):
    return ['NickDraper']


def get_pr_developer(pr):
    try:
        developer = pr['commits']['nodes'][0]['commit']['author']['user']['login']
        return [developer]
    except TypeError:
        return []


def get_pending_reviewers(pr):
    return [r['author']['login'] for r in pr['reviews']['nodes'] if r['state'] == 'PENDING']


def get_requested_reviewers(pr):
    return [rr['reviewer']['login'] for rr in pr['reviewRequests']['nodes']]


resolutions = {
    'generic': (get_admins, [
        Template('$users can you take a look at this?'),
        Template('$users it looks like there are some issues here, can you investigate?')
    ]),
    'no_dev': (get_admins, [
        Template('$users this PR is now without a developer.')
    ]),
    'conflicting': (get_pr_developer, [
        Template('$users there are merge conflicts here, can you resolve them.')
    ]),
    'failing': (get_pr_developer, [
        Template('$users the build is failing, can you investigate.'),
        Template('$users have you had a chance to see why the build is failing?')
    ]),
    'unreviewed': (get_pr_developer, [
        Template('$users do you want to request a review on this PR?'),
        Template('$users it may be worth bringing this PR to attention for review.')
    ]),
    'pending_review': (get_pending_reviewers, [
        Template('$users have you had a chance to complete your review yet?'),
        Template('$users do you have any comments on this PR?')
    ]),
    'pending_gatekeeper': (get_pr_developer, [
        Template('$users gatekeeper needed')
    ]),
    'review_requested': (get_requested_reviewers, [
        Template('$users have you had a chance to complete your review yet?'),
        Template('$users do you have any comments on this PR?')
    ]),
    'ignored_review': (get_pr_developer, [
        Template('$users have you had a chance to look at the review comments yet?'),
        Template('$users could you review the feedback left on this PR and make '
                 'changes as appropriate'),
    ])
}


def fill_message_template(template, usernames):
    if not isinstance(usernames, list):
        usernames = [usernames]

    user_str = ', '.join(['@{}'.format(u.strip()) for u in usernames])
    msg_str = template.substitute(users=user_str)

    return msg_str


def fill_random_response_message(response_type, pr):
    usernames = resolutions[response_type][0](pr)
    idx = randrange(0, len(resolutions[response_type][1]))
    return fill_message_template(resolutions[response_type][1][idx], usernames)


def generate_resolution_comments(sorted_prs):
    comments = []
    for response_type, prs in sorted_prs.items():
        comments.extend(
                [(pr, fill_random_response_message(response_type, pr)) for pr in prs])
    return comments