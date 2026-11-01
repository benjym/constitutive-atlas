import {runImplicitPath} from './implicit-path-engine.mjs';
self.onmessage=async({data})=>{const id=data?.id;try{self.postMessage({id,...await runImplicitPath(data.controls)});}catch(error){self.postMessage({id,error:error.message});}};
