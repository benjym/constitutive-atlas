export const signatures={atlas_integrate_with_settings:['string','string','string','string','string'],atlas_integrate:['string','string','string','string'],atlas_run_scope_with_settings:['string','string','string','number','number','number','number','string']};
export function encodeArgs(types,args){
 if(!Array.isArray(types)||!Array.isArray(args)||types.length!==args.length)throw Error('argument shape');
 return args.map((v,i)=>{if(types[i]==='string'&&typeof v==='string')return v;if(types[i]==='number'&&typeof v==='number'){const b=Buffer.alloc(8);b.writeDoubleBE(v);return {binary64:b.toString('hex')};}throw Error('argument kind');});
}
export function decodeRequest(r){
 if(r.result!=='string'||!Object.hasOwn(signatures,r.name)||JSON.stringify(r.types)!==JSON.stringify(signatures[r.name])||!Array.isArray(r.encoded_args)||r.encoded_args.length!==r.types.length)throw Error('API signature');
 return r.encoded_args.map((v,i)=>{if(r.types[i]==='string'&&typeof v==='string')return v;if(r.types[i]==='number'&&v&&Object.keys(v).length===1&&typeof v.binary64==='string'&&/^[0-9a-f]{16}$/.test(v.binary64))return Buffer.from(v.binary64,'hex').readDoubleBE();throw Error('argument transport');});
}
