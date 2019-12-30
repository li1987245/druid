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
mybatis plus 启动顺序：
MybatisPlusAutoConfiguration -》 MybatisSqlSessionFactoryBean -》 MybatisSqlSessionFactoryBean#afterPropertiesSet -》 MybatisSqlSessionFactoryBean#buildSqlSessionFactory
                -》 MybatisXMLConfigBuilder -》 org.apache.ibatis.builder.BaseBuilder#getConfiguration -》 com.baomidou.mybatisplus.MybatisXMLConfigBuilder#parse
                -》 匹配type alias记录到TypeAliasRegistry -》 org.apache.ibatis.type.TypeAliasRegistry#registerAliases(String packageName,
                            Class<?> superType) -》org.apache.ibatis.io.ResolverUtil#find  spring-boot集成mybatis需要指定spring boot VFS，因为DefaultVFS会校验if (name.indexOf(path) == 0) ，而spring boot直接打包文件以/BOOT-INF/classes/开头
                -》 注册拦截器 -》 org.apache.ibatis.session.Configuration#addInterceptor
                -》 注册mapper -》 org.springframework.core.io.support.PathMatchingResourcePatternResolver#getResources -》 org.apache.ibatis.builder.xml.XMLMapperBuilder#parse
                                    -》 org.apache.ibatis.builder.xml.XMLMapperBuilder#bindMapperForNamespace

mybatis结果映射 BeanWrapper.instantiatePropertyValue->DefaultResultSetHandler.applyAutomaticMappings->BaseTypeHandler.getResult->具体的TypeHandler.getResult
```
- java cp
```
java -cp loan-monitor-api.jar:libs/*.jar com.br.loan.strategy.api.MonitorApiApplication
```
- java class 加载顺序
```
1.Bootstrap ClassLoader 最顶层的加载类，主要加载核心类库，%JRE_HOME%\lib下的rt.jar、resources.jar、charsets.jar和class等。另外需要注意的是可以通过启动jvm时指定-Xbootclasspath和路径来改变Bootstrap ClassLoader的加载目录。比如java -Xbootclasspath/a:path被指定的文件追加到默认的bootstrap路径中。我们可以打开我的电脑，在上面的目录下查看，看看这些jar包是不是存在于这个目录。
2.Extention ClassLoader 扩展的类加载器，加载目录%JRE_HOME%\lib\ext目录下的jar包和class文件。还可以加载-D java.ext.dirs选项指定的目录。
3.Appclass Loader也称为SystemAppClass 加载当前应用的classpath的所有类。
java虚拟机的入口:sun.misc.Launcher
tomcat入口类：org.apache.catalina.startup.BootStrap
spring boot 入口类：SpringApplication
spring boot内嵌tomcat入口类：EmbeddedWebApplicationContext#onRefresh -》 EmbeddedServletContainerAutoConfiguration -》 TomcatEmbeddedServletContainerFactory#getEmbeddedServletContainer
AutoConfigurationImportSelector:加载spring.factories中配置的所有类型为org.springframework.boot.autoconfigure.EnableAutoConfiguration的配置类
```
- 加载的类所在包路径
```
java –verbose:class 在项目启动时增加，可以打印出加载的类以及类所属包
System.out.println(类名.class.getProtectionDomain().getCodeSource().getLocation());
查看内存中的类的加载信息
ps -ef|grep proc找出进程号
jmap -dump:live,format=b,file=heap.bin pid（进程号）
使用jhat或mat分析
jhat -J-mx800m heap.bin
http://ip:7000/
```
- java 打印jvm参数
```
java -XX:+PrintFlagsFinal -version | grep ThreadStackSize
```
- java gc
```
java –verbose:gc
```
- java jni
```
java -verbose:jni
```
- java 更新jar包
```
jar uf test.jar com\test\Test.class
```

#### spring
##### 启动
- 默认加载类
```
AbstractAutowireCapableBeanFactory
```
##### annotation
- ConfigurationProperties
```
PropertySource注解加载指定的属性文件
@PropertySource(value= {"classpath:config/jdbc.properties"},ignoreResourceNotFound=false,encoding="UTF-8",name="jdbc.properties",)
1.Value
@Value("${spring.datasource.url:xxx}")  获取PropertySource指定配置文件中的配置信息
2.ConfigurationProperties
@ConfigurationProperties(prefix = "spring.datasource")   注解类，获取PropertySource指定配置文件中已prefix开头的配置信息并注入到ConfigurationProperties注解的类
@ConfigurationProperties(prefix = "spring.datasource")  注解工厂方法，@bean标识的方法，等同于对工厂生成类进行ConfigurationProperties注解

Spring中对资源文件的封装类Resource。如果是classpath开头的，使用的是Resource的子类ClassPathResource。如果是file开头的，则最终使用的类是FileSystemResource
SpringApplication springApplication = new SpringApplication(DemoApplication.class);
ConfigurableApplicationContext configurableApplicationContext = springApplication.run(args);
T bean = configurableApplicationContext.getBean(T.class);
Environment env =configurableApplicationContext.getEnvironment()
```