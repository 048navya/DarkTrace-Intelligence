import {PGlite} from '@electric-sql/pglite';
import {PGLiteSocketServer} from '@electric-sql/pglite-socket';
import {spawn} from 'node:child_process';
import net from 'node:net';
const probe=net.createServer();await new Promise(r=>probe.listen(0,'127.0.0.1',r));const port=probe.address().port;await new Promise(r=>probe.close(r));
const db=await PGlite.create();const server=new PGLiteSocketServer({db,host:'127.0.0.1',port,maxConnections:32});await server.start();
try{const code=await new Promise((resolve,reject)=>{const child=spawn(process.env.TEST_PYTHON||'python',['tests/test_repository.py'],{stdio:'inherit',env:{...process.env,DARKTRACE_DISPOSABLE_TEST_DB:'1',PGSSLMODE:'disable',DB_HOST:'127.0.0.1',DB_PORT:String(port),DB_NAME:'postgres',DB_USER:'postgres',DB_PASSWORD:'test-only-pglite'}});child.on('error',reject);child.on('exit',resolve);});process.exitCode=code??1;}finally{await server.stop();await db.close();}
