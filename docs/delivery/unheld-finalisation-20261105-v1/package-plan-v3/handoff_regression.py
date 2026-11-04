"""Only manufactured handoff arguments and saved authority bytes; no child/process/source work."""
import copy

def run(L,check,reject,handoff,process,resource,claim,now):
 # The old event time remains old; only the verification time is fresh.
 check('historical child timestamp unchanged',handoff['historical_child_ended_ns']==1793770505429313000)
 check('fresh verification accepts genuinely old terminal',L.handoff_guard(claim,process,handoff,resource,now)>0)
 for kind in ['activeowner','staleverification','unreaped','wrongterminal','wrongreap','wrongowner','wrongverifier','historicaltime','verificationfuture','verificationorder']:
  h=copy.deepcopy(handoff)
  if kind=='activeowner':h['no_newer_active_owner']=False
  elif kind=='staleverification':h['verified_epoch']=now-301
  elif kind=='unreaped':h['all_children_reaped']=False
  elif kind=='wrongterminal':h['terminal_sha256']='0'*64
  elif kind=='wrongreap':h['reap_sha256']='0'*64
  elif kind=='wrongowner':h['prior_owner']='Interface'
  elif kind=='wrongverifier':h['verified_by']='/other'
  elif kind=='historicaltime':h['historical_child_ended_ns']+=1
  elif kind=='verificationfuture':h['verified_epoch']=now+1
  else:h['verified_epoch']=process['captured_epoch']+1
  reject('v3 rejects '+kind,lambda h=h:L.handoff_guard(claim,process,h,resource,now))
 check('v3 execution explicitly blocked',L.POLICY['execution_permitted']is False)
 reject('blocked before reading authorization/source',lambda:L.execute('/never/read/authorization','0'*64))
