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
- jmap
```
1>  -dump:[live,]format=b,file=<filename>
2>  -finalizerinfo 打印正等候回收的对象的信息
3>  -heap 打印heap的概要信息，GC使用的算法，heap（堆）的配置及JVM堆内存的使用情况.
4>  -histo[:live] 打印每个class的实例数目,内存占用,类全名信息. jmap -histo:live 会触发FULL GC（Heap Inspection Initiated GC）
5>  -F
```
- jinfo
```
jinfo [option] pid
no option 输出全部的参数和系统属性
-flag name 输出对应名称的参数
-flag [+|-]name 开启或者关闭对应名称的参数
-flag name=value 设定对应名称的参数
-flags 输出全部的参数
-sysprops 输出系统属性
```
- java gc
```
java -**
-verbose:gc
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-Xloggc:../logs/gc.log

降低stop the world时间 + 吞吐量（应用运行时间/（应用+gc时间））
```
- java jvm 参数
```
-Xms10240m	java Heap初始大小。 默认是物理内存的1/64
-Xmx10240m	java heap最大值
-Xmn1024m	设置年轻代大小，一般设置为Xmx的2/8~3/8,等同于-XX:NewSize 和 -XX:MaxNewSize。
-XX:NewRatio=2 表示新老年代比例为1:n，默认为4
-XX:SurvivorRatio=8 	Eden区与Survivor区的大小比值, 1:1:n
-XX:TargetSurvivorRatio=80，survivor空间的利用率，默认是50
-XX:PretenureSizeThreshold=n	晋升年老代的对象大小。默认为0，超过设置大小的对象将直接进入年老代。
-XX:+DisableExplicitGC	关闭System.gc()
-XX:+UseParNewGC  设置新生代gc，Minor GC（stop the world）
-XX:ParallelGCThreads=10    ParNewGC线程
-XX:MaxTenuringThreshold=10 Survivor的年龄阈值，默认15,Survivor区中年龄相同的对象加起来超过Survivor区一半内存大小的时候，Survivor区就会提前把大于等于此年龄的对象复制到老年代中

-XX:+UseTLAB 使用TLAB
-XX:+TLABSize=64k 设置TLAB大小
-XX:TLABRefillWasteFraction 设置维护进入TLAB空间的单个对象大小，他是一个比例值，默认为64，即如果对象大于整个空间的1/64，
-XX:TLABWasteTargetPercent  设置TLAB空间所占用Eden空间的百分比大小 默认是1%
-XX:+PrintTLAB 查看TLAB信息
-XX:ResizeTLAB 自调整TLABRefillWasteFraction阈值。
```
- java cms
```
Major GC：针对老年代的垃圾回收
1.初始标记（stop the world） CMS-initial-mark
2.并发标记（并发） CMS-concurrent-mark
3.预清理（并发） CMS-concurrent-preclean
4.可被终止的预清理（并发） CMS-concurrent-abortable-preclean
-XX:CMSMaxAbortablePrecleanTime=5000 ，默认值5s，代表该阶段最大的持续时间
-XX:CMSScheduleRemarkEdenPenetration=50 ，默认值50%，代表Eden区使用比例超过50%就结束该阶段进入remark
5.重新标记（stop the world） CMS Final Remark
2020-02-12T18:37:35.276+0800: 5343221.738: [GC (CMS Final Remark) [YG occupancy: 362005 K (377472 K)]2020-02-12T18:37:35.276+0800: 5343221.738: [Rescan (parallel) , 1.4470466 secs]2020-02-12T18:37:36.723+0800: 5343223.185: [weak refs processing, 0.0019745 secs]2020-02-12T18:37:36.725+0800: 5343223.187: [class unloading, 0.0569329 secs]2020-02-12T18:37:36.782+0800: 5343223.244: [scrub symbol table, 0.0112718 secs]2020-02-12T18:37:36.793+0800: 5343223.255: [scrub string table, 0.0019117 secs][1 CMS-remark: 1434437K(1677760K)] 1796443K(2055232K), 1.5193831 secs] [Times: user=6.03 sys=0.00, real=1.52 secs]
2020-02-12T18:37:35.276+0800: 5343221.738 – 触发时间：JVM运行时间；
CMS Final Remark – 收集阶段，这个阶段会标记老年代全部的存活对象，包括那些在并发标记阶段更改的或者新创建的引用对象；
YG occupancy: 362005 K (377472 K) – 年轻代当前占用情况和容量；
[Rescan (parallel) , 1.4470466 secs] – 这个阶段在应用停止的阶段完成存活对象的标记工作；
[weak refs processing, 0.0019745 secs] – 第一个子阶段，随着这个阶段的进行处理弱引用；
[class unloading, 0.0569329 secs] – 第二个子阶段(that is unloading the unused classes, with the duration and timestamp of the phase);
scrub string table, 0.0112718 secs – 最后一个子阶段（that is cleaning up symbol and string tables which hold class-level metadata and internalized string respectively）
[1 CMS-remark: 1434437K(1677760K)] – 在这个阶段之后老年代占有的内存大小和老年代的容量；
1796443K(2055232K) – 在这个阶段之后整个堆的内存大小和整个堆的容量；
1.5193831 secs – 这个阶段的持续时间；
[Times: user=6.03 sys=0.00, real=1.52 secs] – 执行时间；
6.并发清除（并发） CMS-concurrent-sweep
2020-02-12T18:37:36.795+0800: 5343223.257: [CMS-concurrent-sweep-start]
2020-02-12T18:37:42.580+0800: 5343229.042: [CMS-concurrent-sweep: 0.887/5.785 secs] [Times: user=21.76 sys=0.00, real=5.78 secs]
CMS-concurrent-sweep – 这个阶段主要是清除那些没有标记的对象并且回收空间；
[CMS-concurrent-sweep: 0.887/5.785 secs] – 展示该阶段持续的时间（CPU时间）和持续时间；
[Times: user=21.76 sys=0.00, real=5.78 secs]
7.重置状态，等待下次CMS的触发（并发） CMS-concurrent-reset

ParNew GC日志
2020-02-12T18:37:36.899+0800: 5343223.361: [GC (Allocation Failure) 2020-02-12T18:37:36.899+0800: 5343223.361: [ParNew: 377472K->41920K(377472K), 4.8952603 secs] 1594442K->1587518K(2055232K), 4.8954677 secs] [Times: user=19.80 sys=0.00, real=4.89 secs]
[ParNew: 377472K->41920K(377472K), 4.8952603 secs] 新生代大小由377472K->41920K，新生代总大小为(377472K)，耗时4.8952603 secs
1594442K->1587518K(2055232K) 总内存大小由1594442K->1587518K，总内存大小为(2055232K)
[Times: user=19.80 sys=0.00, real=4.89 secs] gc耗时4.89 secs

-XX:+UseConcMarkSweepGC
-XX:+CMSParallelRemarkEnabled	开启并行remark
-XX:+CMSScavengeBeforeRemark 执行CMS remark之前进行一次youngGC
-XX:ParallelCMSThreads=4 (ParallelGCThreads + 3)/4  ParallelGCThreads= cpu core-1)
-XX:CMSInitiationgOccupancyFraction=68
-XX:UseCMSInitiatingOccupancyOnly       只在到达阀值的时候才进行CMS回收
-XX:+UseCMSCompactAtFullCollection      FULL GC后是否要进行一次内存碎片的整理
-XX:CMSFullGCsBeforeCompaction=5     CMS进行n次full gc后进行一次压缩，0表示每次都压缩
-XX:+CMSClassUnloadingEnabled       允许对永久代进行CMS回收
-XX:+UseFastAccessorMethods	原始类型的快速优化

YGC晋升失败（promotion failures），触发Concurrent Mode Failure会导致FULL GC（Mark-Sweep-Compact GC）
concurrent mode failure 出现的原因：老年代空间不足以存放新生代历次晋升到老年代对象大小，解决方案：降低CMSInitiatingOccupancyFraction
比例并设置UseCMSInitiatingOccupancyOnly为true，提早触发CMS gc，保证老年代可用空间，但是频繁Major GC会影响性能
2020-02-12T18:37:47.524+0800: 5343233.987: [GC (Allocation Failure) 2020-02-12T18:37:47.525+0800: 5343233.987: [ParNew: 377472K->377472K(377472K), 0.0000595 secs]2020-02-12T18:37:47.525+0800: 5343233.987: [CMS2020-02-12T18:37:55.437+0800: 5343241.900: [CMS-concurrent-mark: 9.643/9.647 secs] [Times: user=38.68 sys=0.00, real=9.65 secs]
 (concurrent mode failure): 1525339K->1528880K(1677760K), 12.7386697 secs] 1902811K->1528880K(2055232K), [Metaspace: 89126K->89126K(1130496K)], 12.7390678 secs] [Times: user=36.51 sys=0.00, real=12.74 secs]
concurrent mode failure CMS GC失败
1525339K->1528880K(1677760K) 老年代从1525339K->1528880K，总大小为(1677760K)
1902811K->1528880K(2055232K) 总内存从1902811K->1528880K，总大小为(2055232K)
```
- java g1
```
-XX:+UseG1GC    使用G1回收器
-XX:MaxGCPauseMillis    设置最大垃圾收集停顿时间
-XX:GCPauseIntervalMillis   设置停顿间隔时间
```
- java jni
```
java -verbose:jni
```
- 逃逸分析
```
逃逸分析的基本行为就是分析对象动态作用域：当一个对象在方法中被定义后，它可能被外部方法所引用，例如作为调用参数传递到其他地方中，称为方法逃逸
使用逃逸分析，编译器可以对代码做如下优化：
一、同步省略。如果一个对象被发现只能从一个线程被访问到，那么对于这个对象的操作可以不考虑同步。
二、将堆分配转化为栈分配。如果一个对象在子程序中被分配，要使指向该对象的指针永远不会逃逸，对象可能是栈分配的候选，而不是堆分配。
三、分离对象或标量替换。有的对象可能不需要作为一个连续的内存结构存在也可以被访问到，那么对象的部分（或全部）可以不存储在内存，而是存储在CPU寄存器中。
在Java代码运行时，通过JVM参数可指定是否开启逃逸分析，
-XX:+DoEscapeAnalysis ： 表示开启逃逸分析
-XX:-DoEscapeAnalysis ： 表示关闭逃逸分析 从jdk 1.7开始已经默认开始逃逸分析，如需关闭，需要指定-XX:-DoEscapeAnalysi
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

@ImportResource引入配置文件
@ImportResource(locations = {"classpath:beans.xml"})
导入Spring的配置文件让其生效
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