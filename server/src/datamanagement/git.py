import json

from git import Repo
import config

import ipdb; ipdb.set_trace()
repo = Repo(config.DATA_DIR)

if hasattr(config, 'GIT_BRANCH'):
    branch = config.GIT_BRANCH
else:
    branch = "master"

def commit_file(user, relative_path):
    if repo.is_dirty():
        diffs = repo.head.commit.diff(None, create_patch=True)
        relevant_diffs = [str(diff) for diff in diffs if relative_path in str(diff)]
        added_ids = set()
        removed_ids = set()
        for diff in relevant_diffs:
            for line in diff.split("\n"):
                if line.startswith("+T") or line.startswith("-T"):
                    changed_label = line.split()[0]
                    if line.startswith("+"):
                        added_ids.add(changed_label[1:])
                    else:
                        removed_ids.add(changed_label[1:])
        changed_ids = added_ids.intersection(removed_ids)
        added_ids = added_ids.difference(changed_ids)
        removed_ids = removed_ids.difference(changed_ids)
        git_data = {
            "user": user,
            "changed_path": relative_path,
            "new_labels": list(added_ids),
            "removed_labels": list(removed_ids),
            "changed_labels": list(changed_ids)
        }
        git_message = json.dumps(git_data, indent=4)
        repo.index.add([relative_path])
        repo.index.commit(git_message)

def push_to_origin():
    origin = repo.remote('origin')
    assert origin.exists()
    origin.pull(branch)
    origin.push(branch)