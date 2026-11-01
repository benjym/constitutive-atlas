// UI support declarations describe qualified host controls, not constitutive equations.
export function validateSupport(policy,catalogue){
 if(policy?.schema_version!=='0.1'||!Array.isArray(policy.models))throw Error('Invalid laboratory control support.');
 const seen=new Set();
 for(const row of policy.models){
  if(!catalogue.models.some(m=>m.id===row.model)||seen.has(row.model)||!Array.isArray(row.unsupported))throw Error('Unknown or duplicate support model.');seen.add(row.model);
  for(const c of row.unsupported)if(!Number.isInteger(c.protocol)||c.protocol<0||c.protocol>4||!Number.isInteger(c.minimum_cycles)||c.minimum_cycles<0||typeof c.reason!=='string'||!c.reason.trim())throw Error('Invalid unsupported control declaration.');
 }
 return policy;
}
export function unsupportedReason(policy,s){return policy?.models.find(m=>m.model===s.model)?.unsupported.find(c=>c.protocol===s.protocol&&s.cycles>=c.minimum_cycles)?.reason??'';}
export function requireSupportedControl(policy,s){const reason=unsupportedReason(policy,s);if(reason)throw Error(reason);}
