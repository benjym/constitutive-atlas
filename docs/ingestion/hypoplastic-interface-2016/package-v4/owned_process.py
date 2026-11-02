"""Owned-session lifecycle; import is inert. Fixture injection never runs real commands."""
import os,signal,subprocess,time

def group_members(pgid):
 """Read-only group snapshot. Permission failure is never absence-of-process proof."""
 text=subprocess.check_output(['ps','-axo','pid=,pgid=,stat='],text=True)
 members=[]
 for line in text.splitlines():
  fields=line.split()
  if len(fields)>=3 and int(fields[1])==pgid:
   pid=int(fields[0]);assert os.getpgid(pid)==pgid, 'Group membership changed during snapshot'
   members.append({'pid':pid,'state':fields[2]})
 return members

def cleanup_owned_group(child,ownership,snapshot=group_members,term_seconds=1.0,kill_seconds=3.0):
 """Only this Popen's independently verified new group may be signalled.
 The leader is not reaped until the whole captured group is terminal, preventing
 reuse of its group ID while surviving descendants are being cleaned up.
 """
 assert ownership['pid']==child.pid==ownership['pgid']==ownership['sid']
 pgid=os.getpgid(child.pid);sid=os.getsid(child.pid)
 assert pgid==ownership['pgid'] and sid==ownership['sid'], 'Refuse signalling changed ownership'
 events=[]
 def live_members():
  members=snapshot(pgid)
  for row in members:assert os.getsid(row['pid'])==ownership['sid'], 'Refuse group with foreign-session member'
  return [row for row in members if not row['state'].startswith('Z')]
 if not live_members():
  code=child.wait(timeout=5);events.append('reap-leader');return {'status':'whole-owned-group-terminal-and-leader-reaped','events':events,'returncode':code}
 os.killpg(pgid,signal.SIGTERM);events.append('SIGTERM-own-group')
 deadline=time.monotonic()+term_seconds
 while True:
  live=live_members()
  if not live:
   code=child.wait(timeout=5);events.append('reap-leader');return {'status':'whole-owned-group-terminal-and-leader-reaped','events':events,'returncode':code}
  if time.monotonic()>=deadline:break
  time.sleep(.02)
 # A still-unreaped own leader reserves this PGID even if it is already zombie.
 assert os.getpgid(child.pid)==pgid and os.getsid(child.pid)==sid
 os.killpg(pgid,signal.SIGKILL);events.append('SIGKILL-own-group');deadline=time.monotonic()+kill_seconds
 while live_members():
  if time.monotonic()>=deadline:raise TimeoutError('Own group not terminal after bounded KILL wait')
  time.sleep(.02)
 code=child.wait(timeout=5);events.append('reap-leader');return {'status':'whole-owned-group-terminal-and-leader-reaped','events':events,'returncode':code}

def run_owned(argv,cwd,env,out,err,verify,on_started,*,snapshot=group_members):
 verify();child=None;ownership=None
 try:
  child=subprocess.Popen(argv,cwd=cwd,env=env,stdout=out,stderr=err,start_new_session=True)
  ownership={'pid':child.pid,'pgid':os.getpgid(child.pid),'sid':os.getsid(child.pid)}
  assert ownership['pid']==ownership['pgid']==ownership['sid'],'Own process group/session was not created'
  on_started(child,ownership)
  # WNOWAIT preserves the leader identity throughout interruptible waiting.
  while True:
   observed=os.waitid(os.P_PID,child.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
   if observed is not None and observed.si_pid==child.pid:break
   time.sleep(.05)
  return child.wait()
 except BaseException as error:
  if child is not None:
   try:
    if ownership is None:
     ownership={'pid':child.pid,'pgid':os.getpgid(child.pid),'sid':os.getsid(child.pid)}
    cleanup=cleanup_owned_group(child,ownership,snapshot=snapshot)
   except BaseException as failure:
    # Do not hide incomplete cleanup or signal a guessed/foreign group. Parent
    # must resolve permission/identity failures before resuming any execution.
    cleanup={'status':'cleanup-incomplete-block-resumption','error':repr(failure),'pid':child.pid,'ownership':ownership}
    try:cleanup['leader_returncode']=child.wait(timeout=5)
    except BaseException as reap_error:cleanup['reap_error']=repr(reap_error)
   try:error.owned_process_cleanup=cleanup
   except AttributeError:pass
  raise
