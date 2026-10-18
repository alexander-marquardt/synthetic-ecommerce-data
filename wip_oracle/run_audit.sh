#!/usr/bin/env bash
# one pytest process per test file; records the audit
cd /Volumes/AgentClones/wt-g495 || exit 1
export AUDIT_ROOT=/Volumes/AgentClones/wt-g495
export AUDIT_OUT=/Volumes/AgentClones/wt-g495/.agent/audit.jsonl
export PYTHONPATH=/Volumes/AgentClones/wt-g495/.agent
: > "$AUDIT_OUT"
while read -r f; do
  .venv/bin/python -m pytest -p audit_plugin -x -q --tb=line -p no:cacheprovider "$f" > /Volumes/AgentClones/wt-g495/.agent/audit-last.log 2>&1
  echo "$f rc=$?" >> /Volumes/AgentClones/wt-g495/.agent/audit-progress.log
done < /Volumes/AgentClones/wt-g495/.agent/audit-list.txt
echo DONE >> /Volumes/AgentClones/wt-g495/.agent/audit-progress.log
