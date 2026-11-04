// Generic transport for the incremental public C API, not a model kernel.
import {pathToFileURL} from 'node:url';
import fs from 'node:fs';
import readline from 'node:readline';
export function dispatch(argv, call) {
  if(!Array.isArray(argv)||argv.some(value=>typeof value!=='string'||value.includes('\0')))throw Error('CLI arguments must be strings without NUL');
  if (argv.length === 1 && argv[0] === '--describe') return call('atlas_describe',[],[]);
  const allowed=new Set(['--model','--parameters','--initial','--current','--strain','--mode','--protocol','--target','--steps','--cycles','--integration-settings']);
  const options=new Map();
  if(argv.length%2)throw Error('expected CLI option/value pairs');
  for(let i=0;i<argv.length;i+=2){if(!allowed.has(argv[i])||options.has(argv[i]))throw Error('unsupported or duplicate CLI option');options.set(argv[i],argv[i+1]);}
  const get=(key,value='')=>options.get(key)??value;
  const id=get('--model'),p=get('--parameters'),z=get('--initial'),d=get('--strain'),mode=get('--mode','run');
  if(options.has('--integration-settings') && !['run','integrate'].includes(mode))throw Error('incremental settings require run or integrate mode');
  if(mode==='evaluate')return call('atlas_evaluate',Array(5).fill('string'),[id,p,get('--current'),z,d]);
  if(mode==='integrate')return options.has('--integration-settings')?call('atlas_integrate_with_settings',Array(5).fill('string'),[id,p,z,d,get('--integration-settings')]):call('atlas_integrate',Array(4).fill('string'),[id,p,z,d]);
  if(mode!=='run')throw Error('unsupported mode');
  // std::stod consumes leading C whitespace, but rejects trailing bytes, empty
  // values and JavaScript binary/octal literals. Hexadecimal C floats are
  // supported explicitly so no CLI value is silently reinterpreted.
  const numeric=(key,fallback)=>{
    const s=get(key,fallback), decimal=/^[\t\n\v\f\r ]*[+-]?(?:(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)$/;
    const hex=/^[\t\n\v\f\r ]*([+-]?)0[xX]([0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?|\.[0-9a-fA-F]+)(?:[pP]([+-]?\d+))?$/;
    let value;
    if(decimal.test(s))value=Number(s);
    else {
      const m=s.match(hex);if(!m)throw Error('invalid number: '+key);
      const [whole,fraction='']=m[2].split('.');let significand=BigInt('0x'+(whole+fraction));
      if(significand===0n)value=m[1]==='-'?-0:0;
      else {
        // One exact integer rounding to binary64; no double-rounded digit sum
        // and no overflowing intermediate exponent for finite final values.
        const exponent=BigInt(m[3]||0)-4n*BigInt(fraction.length);
        const shift=BigInt(Math.max(0,significand.toString(2).length-53));
        if(shift>0n){const remainder=significand-((significand>>shift)<<shift),half=1n<<(shift-1n);significand>>=shift;if(remainder>half||(remainder===half&&(significand&1n)))significand+=1n;}
        let scale=exponent+shift;
        if(significand===2n**53n){significand>>=1n;scale+=1n;}
        value=Number(significand)*2**Number(scale)*(m[1]==='-'?-1:1);
      }
    }
    if(!Number.isFinite(value))throw Error('invalid number: '+key);
    const mantissa=s.trimStart().split(hex.test(s)?/[pP]/:/[eE]/)[0].replace(/^[-+]?0[xX]/,'');
    if((value===0 && /[1-9a-fA-F]/.test(mantissa)) || (value!==0 && Math.abs(value)<2**-1022))throw Error('number out of range: '+key);
    if(key!=='--target' && (!Number.isInteger(value)||Math.abs(value)>1000000))throw Error('invalid integer: '+key);
    return value;
  };
  const nums=[['--protocol','1'],['--target','0.01'],['--steps','100'],['--cycles','0']].map(([k,v])=>numeric(k,v));
  const args=[id,p,z,...nums],types=['string','string','string','number','number','number','number'];
  return options.has('--integration-settings')?call('atlas_run_with_settings',[...types,'string'],[...args,get('--integration-settings')]):call('atlas_run',types,args);
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href){
  const [modulePath,wasmPath,...argv]=process.argv.slice(2);
  // A literal pinned Wasm byte buffer prevents Emscripten resolving another sibling.
  const factory=(await import(pathToFileURL(modulePath).href)).default;
  const engine=await factory({wasmBinary:fs.readFileSync(wasmPath),print:()=>{},printErr:s=>process.stderr.write(String(s)+'\n')});
  const invoke=args=>dispatch(args,(name,types,values)=>engine.ccall(name,'string',types,values));
  if(argv.length===1&&argv[0]==='--serve'){
    for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})){
      try{const args=JSON.parse(line),raw=invoke(args);process.stdout.write(JSON.stringify({stdout:raw+'\n',returncode:args[0]==='--describe'||JSON.parse(raw).ok===true?0:1})+'\n');}
      catch(error){process.stdout.write(JSON.stringify({transport_error:String(error)})+'\n');}
    }
    process.exit(0);
  }
  const result=invoke(argv);
  process.stdout.write(result+'\n');
  process.exitCode=argv[0]==='--describe'||JSON.parse(result).ok===true?0:1;
}
