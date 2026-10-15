/** Decode only API JSON; never expose a gateway or sign-in HTML document. */
export async function readApiResponse(response:Response):Promise<any> {
  if(response.status===401 || (response.redirected && /\/(signin-with-chatgpt|callback|auth)(\/|\?|$)/i.test(response.url))) {
    throw new Error('Sign in again to access this workspace. Open it in a new tab if the embedded view cannot restore your session.');
  }
  if(response.status===403)throw new Error('Access was denied. Open the workspace with the account that has access.');
  const contentType=response.headers.get('content-type')||'';
  if(!/\bapplication\/(?:[\w.-]+\+)?json\b/i.test(contentType)) {
    throw new Error(response.status>=500?'The service is temporarily unavailable. Please retry.':'The server returned a page instead of workspace data. Retry, or open the workspace in a new tab to check your session.');
  }
  let result:any;
  try {result=await response.json();}catch {throw new Error('The server returned incomplete data. Please retry.');}
  if(!response.ok)throw new Error(typeof result?.error==='string'?result.error:`Request failed (${response.status}). Please retry.`);
  return result;
}
export async function apiRequest(url:string,body?:unknown,signal?:AbortSignal):Promise<any> {
  const response=await fetch(url,{method:body===undefined?'GET':'POST',credentials:'same-origin',cache:'no-store',signal,headers:{Accept:'application/json',...(body===undefined?{}:{'Content-Type':'application/json'})},...(body===undefined?{}:{body:JSON.stringify(body)})});
  return readApiResponse(response);
}
