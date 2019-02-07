1. jdk8 Nashorn 的线程安全性
```markdown
ScriptEngine for Nashorn is not thread-safe. This can be verified by calling the ScriptEngineFactory.getParameter("THREADING") of the ScriptEngineFactory for Nashorn.
https://blogs.oracle.com/nashorn/nashorn-multithreading-and-mt-safety
如何在多线程中应用：
https://stackoverflow.com/questions/30140103/should-i-use-a-separate-scriptengine-and-compiledscript-instances-per-each-threa 
ScriptEngine 可多线程共享
Bindings 非线程安全，不能多线程共享
public class Test {
    static ScriptEngineManager manager = new ScriptEngineManager();
    static ScriptEngine engine = manager.getEngineByName("javascript");
    public static void main(String[] args) throws Exception {
        int time = 10000;
        ExecutorService executor = Executors.newFixedThreadPool(100);
        final CountDownLatch latch = new CountDownLatch(time);
        AtomicInteger right = new AtomicInteger(0);
		AtomicInteger error =new AtomicInteger(0);
        long begin = System.currentTimeMillis();
		for(int i=0;i<time;i++){
			int finalI = i;
			executor.execute(new Runnable() {
				@Override
				public void run() {
//					ScriptEngine engine = manager.getEngineByName("javascript");
//				    Bindings bindings = engine.getBindings(ScriptContext.ENGINE_SCOPE);
					Bindings bindings = engine.createBindings();
				    bindings.put("obj", finalI);
				    try {
				    	if(Double.parseDouble(engine.eval("Math.pow(obj,2)",bindings).toString())==Math.pow(finalI,2))
							right.incrementAndGet();
				    	else
							error.incrementAndGet();
					}
					catch (Exception e){
				    	e.printStackTrace();
					}

					latch.countDown();
				}
			});
		}
		latch.await();
        long end = System.currentTimeMillis();
        System.out.println(end-begin);
		System.out.println("right:"+right.get()+"\t error:"+error.get());
		executor.shutdown();
    }

}
```

2. GC overhead limit exceeded
```
是JDK6新添的错误类型。是发生在GC占用大量时间为释放很小空间的时候发生的，是一种保护机制,超过98%的时间用来做GC并且回收了不到2%的堆内存时会抛出此异常
解决方案：通过加大内存或排除代码问题（死循环等）
```

- mybatis
```
mybatis结果映射 BeanWrapper.instantiatePropertyValue->DefaultResultSetHandler.applyAutomaticMappings->BaseTypeHandler.getResult->具体的TypeHandler.getResult
```
java -cp loan-monitor-api.jar:libs/*.jar com.br.loan.strategy.api.MonitorApiApplication
